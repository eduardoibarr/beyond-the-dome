import pygame
import random
import math
from core.settings import *
from core.noise_generator import NoiseGenerator
from entities.tile import Tile
from entities.obstacle import Obstacle
from entities.radioactive_zone import RadioactiveZone
from entities.collectible import Collectible
from items.item_base import AmmoItem, MaskItem, HealthPackItem, FilterModuleItem

class LevelGenerator:
    def __init__(self, game):
        self.game = game

        self.world_width_tiles = MAP_WIDTH // TILE_SIZE
        self.world_height_tiles = MAP_HEIGHT // TILE_SIZE

        self.map_width_pixels = MAP_WIDTH
        self.map_height_pixels = MAP_HEIGHT
        self.layout = []

        self.spawn_point = (self.world_width_tiles // 2, self.world_height_tiles // 2)
        self.industrial_centers = []

        self.noise_generator = NoiseGenerator(
            seed=random.randint(0, 1000),
            scale=100.0,
            octaves=6,
            persistence=0.5,
            lacunarity=2.0
        )

    def generate_layout(self):
        print("Gerando layout do nível...")

        self.layout = [['grass' for _ in range(self.world_width_tiles)] for _ in range(self.world_height_tiles)]
        self.industrial_centers = []

        seed1 = random.random() * 100
        seed2 = random.random() * 100
        seed3 = random.random() * 100
        seed4 = random.random() * 100
        terrain_scale = 80.0
        water_scale = 120.0
        forest_scale = 60.0
        industrial_placement_scale = 150.0

        print("Gerando terreno base...")
        for y in range(self.world_height_tiles):
            for x in range(self.world_width_tiles):
                terrain_value = self.noise_generator.get_noise_2d(x + seed1, y + seed1)
                water_value = self.noise_generator.get_noise_2d(x + seed2, y + seed2)

                spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
                if spawn_dist < 10:
                    self.layout[y][x] = 'grass'
                    continue

                if water_value < -0.55:

                    if self._is_isolating_water(x, y):
                        self.layout[y][x] = 'grass'
                    else:
                        self.layout[y][x] = 'water'
                elif terrain_value < -0.4 and self.layout[y][x] != 'water':
                    self.layout[y][x] = 'dirt'
                else:
                    self.layout[y][x] = 'grass'

        print("Gerando florestas...")
        for y in range(self.world_height_tiles):
            for x in range(self.world_width_tiles):
                if self.layout[y][x] == 'grass':
                    forest_value = self.noise_generator.get_noise_2d(x + seed3, y + seed3)
                    if forest_value > 0.55:

                        if not self._is_isolating_tree(x, y):
                            self.layout[y][x] = 'tree'

        print("Gerando zonas industriais...")
        self._add_industrial_zones(seed4, industrial_placement_scale)

        print("Gerando zonas urbanas...")
        self._add_urban_zones()

        print("Gerando zonas radioativas...")
        self._add_radioactive_zones()

        print("Limpando área de spawn...")

        if not (0 <= self.spawn_point[0] < self.world_width_tiles and 0 <= self.spawn_point[1] < self.world_height_tiles):
             print(f"Aviso: O ponto de spawn inicial {self.spawn_point} está fora dos limites do mapa. Redefinindo para o centro.")
             self.spawn_point = (self.world_width_tiles // 2, self.world_height_tiles // 2)
        self._clear_spawn_area(radius=7)

        print("Adicionando bordas do mapa...")
        self._add_map_borders()

        self._generate_collectible_items()

        print("Geração do layout completa.")
        return self.layout

    def _is_isolating_water(self, x, y):

        temp_layout = [row[:] for row in self.layout]
        temp_layout[y][x] = 'water'

        return not self._has_path_to_border(temp_layout, self.spawn_point[0], self.spawn_point[1])

    def _is_isolating_tree(self, x, y):

        temp_layout = [row[:] for row in self.layout]
        temp_layout[y][x] = 'tree'

        return not self._has_path_to_border(temp_layout, self.spawn_point[0], self.spawn_point[1])

    def _has_path_to_border(self, layout, start_x, start_y):
        visited = set()
        queue = [(start_x, start_y)]

        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue

            visited.add((x, y))

            if x == 0 or x == self.world_width_tiles - 1 or y == 0 or y == self.world_height_tiles - 1:
                return True

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.world_width_tiles and
                    0 <= ny < self.world_height_tiles and
                    layout[ny][nx] in ['grass', 'dirt'] and
                    (nx, ny) not in visited):
                    queue.append((nx, ny))

        return False

    def _clear_spawn_area(self, radius=5):
        spawn_x, spawn_y = self.spawn_point
        start_x = max(0, spawn_x - radius)
        end_x = min(self.world_width_tiles, spawn_x + radius + 1)
        start_y = max(0, spawn_y - radius)
        end_y = min(self.world_height_tiles, spawn_y + radius + 1)

        clear_types = ['wall', 'tree', 'water', 'building', 'machine', 'pipe', 'tank',
                       'crane', 'generator', 'cooling_tower', 'conveyor', 'chimney',
                       'barrier', 'radioactive']

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    dist_sq = (x - spawn_x)**2 + (y - spawn_y)**2
                    if dist_sq <= radius**2:
                        if self.layout[y][x] in clear_types:
                            self.layout[y][x] = 'grass'

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            path_x, path_y = spawn_x + dx * (radius + 1), spawn_y + dy * (radius + 1)
            if (0 <= path_x < self.world_width_tiles and
                0 <= path_y < self.world_height_tiles and
                self.layout[path_y][path_x] in clear_types):
                self.layout[path_y][path_x] = 'grass'

    def _add_map_borders(self):
        if self.world_height_tiles <= 0 or self.world_width_tiles <= 0: return

        for x in range(self.world_width_tiles):
            if self.world_height_tiles > 0: self.layout[0][x] = 'wall'
            if self.world_height_tiles > 1: self.layout[self.world_height_tiles - 1][x] = 'wall'

        for y in range(self.world_height_tiles):
            if self.world_width_tiles > 0: self.layout[y][0] = 'wall'
            if self.world_width_tiles > 1: self.layout[y][self.world_width_tiles - 1] = 'wall'

    def _add_industrial_zones(self, seed, scale):
        num_zones = random.randint(3, 6)
        print(f"  Tentando colocar {num_zones} zonas industriais...")
        min_dist_between_zones = 25
        min_dist_from_spawn = 20
        padding = max(10, self.world_width_tiles // 10)

        for zone_index in range(num_zones):
            placed = False
            for attempt in range(50):

                noise_x = self.noise_generator.get_noise_2d(zone_index * 10 + seed, attempt + seed)
                noise_y = self.noise_generator.get_noise_2d(attempt + seed, zone_index * 10 + seed)

                zone_x = int((noise_x + 1) / 2 * (self.world_width_tiles - 2 * padding) + padding)
                zone_y = int((noise_y + 1) / 2 * (self.world_height_tiles - 2 * padding) + padding)
                zone_x = max(padding, min(self.world_width_tiles - 1 - padding, zone_x))
                zone_y = max(padding, min(self.world_height_tiles - 1 - padding, zone_y))

                zone_size = random.randint(12, 25)

                spawn_dist = math.sqrt((zone_x - self.spawn_point[0])**2 + (zone_y - self.spawn_point[1])**2)
                if spawn_dist < zone_size + min_dist_from_spawn: continue

                too_close_to_other = False
                for other_x, other_y, other_size in self.industrial_centers:
                    dist = math.sqrt((zone_x - other_x)**2 + (zone_y - other_y)**2)
                    if dist < zone_size + other_size + min_dist_between_zones:
                        too_close_to_other = True; break
                if too_close_to_other: continue

                if self.layout[zone_y][zone_x] == 'water': continue

                print(f"    Colocando zona {zone_index+1} em ({zone_x}, {zone_y}) tamanho {zone_size}")
                self.industrial_centers.append((zone_x, zone_y, zone_size))
                zone_type = random.choice(["factory", "refinery", "power_plant", "warehouse", "mine"])
                print(f"      Tipo: {zone_type}")

                self._create_industrial_floor(zone_x, zone_y, zone_size)
                self._add_specific_industrial_structures(zone_x, zone_y, zone_size, zone_type)
                self._add_industrial_perimeter(zone_x, zone_y, zone_size)
                self._create_transition_zone(zone_x, zone_y, zone_size)
                self._add_environmental_effects(zone_x, zone_y, zone_size)
                placed = True; break
            if not placed: print(f"    Não foi possível encontrar uma localização adequada para a zona {zone_index+1}.")

    def _create_industrial_floor(self, center_x, center_y, radius):
        shape_seed = random.random() * 50
        shape_scale = 15.0
        min_rad = int(radius * 0.6)
        max_rad = int(radius * 1.1)

        for y in range(max(1, center_y - max_rad), min(self.world_height_tiles - 1, center_y + max_rad)):
            for x in range(max(1, center_x - max_rad), min(self.world_width_tiles - 1, center_x + max_rad)):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                angle = math.atan2(y - center_y, x - center_x)

                noise_val = self.noise_generator.get_noise_2d(
                    math.cos(angle) * radius + shape_seed,
                    math.sin(angle) * radius + shape_seed
                )
                current_max_radius = radius + noise_val * (radius * 0.3)
                current_max_radius = max(min_rad, min(max_rad, current_max_radius))

                if dist <= current_max_radius:
                    if self.layout[y][x] != 'water':
                        self.layout[y][x] = 'concrete'

    def _add_specific_industrial_structures(self, center_x, center_y, zone_size, zone_type):
        if zone_type == "factory":

            building_width = min(zone_size - 4, random.randint(8, 12))
            building_height = min(zone_size - 4, random.randint(6, 10))
            building_x = center_x - building_width // 2
            building_y = center_y - building_height // 2

            for y in range(building_y, building_y + building_height):
                for x in range(building_x, building_x + building_width):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        if x == building_x or x == building_x + building_width - 1 or y == building_y or y == building_y + building_height - 1:
                            self.layout[y][x] = 'wall'
                        else:
                            self.layout[y][x] = 'building'

            for _ in range(random.randint(5, 10)):
                offset_x = random.randint(-zone_size + 2, zone_size - 2)
                offset_y = random.randint(-zone_size + 2, zone_size - 2)
                x = center_x + offset_x
                y = center_y + offset_y

                if (x < building_x or x >= building_x + building_width or
                    y < building_y or y >= building_y + building_height) and \
                   0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    if self.layout[y][x] == 'concrete':
                        self.layout[y][x] = 'machine'

        elif zone_type == "refinery":

            for _ in range(random.randint(3, 6)):
                tank_radius = random.randint(2, 3)
                offset_x = random.randint(-zone_size + tank_radius, zone_size - tank_radius)
                offset_y = random.randint(-zone_size + tank_radius, zone_size - tank_radius)
                tank_x = center_x + offset_x
                tank_y = center_y + offset_y

                for y in range(tank_y - tank_radius, tank_y + tank_radius + 1):
                    for x in range(tank_x - tank_radius, tank_x + tank_radius + 1):
                        if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                            dist = math.sqrt((x - tank_x)**2 + (y - tank_y)**2)
                            if dist <= tank_radius and self.layout[y][x] == 'concrete':
                                self.layout[y][x] = 'tank'

            for y in range(center_y - zone_size + 2, center_y + zone_size - 1):
                for x in range(center_x - zone_size + 2, center_x + zone_size - 1):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        if self.layout[y][x] == 'concrete' and random.random() < 0.05:
                            self.layout[y][x] = 'pipe'

        elif zone_type == "power_plant":

            for _ in range(random.randint(2, 4)):
                tower_radius = random.randint(3, 4)
                offset_x = random.randint(-zone_size + tower_radius, zone_size - tower_radius)
                offset_y = random.randint(-zone_size + tower_radius, zone_size - tower_radius)
                tower_x = center_x + offset_x
                tower_y = center_y + offset_y

                for y in range(tower_y - tower_radius, tower_y + tower_radius + 1):
                    for x in range(tower_x - tower_radius, tower_x + tower_radius + 1):
                        if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                            dist = math.sqrt((x - tower_x)**2 + (y - tower_y)**2)
                            if dist <= tower_radius and self.layout[y][x] == 'concrete':
                                self.layout[y][x] = 'cooling_tower'

            for _ in range(random.randint(4, 8)):
                gen_size = random.randint(1, 2)
                offset_x = random.randint(-zone_size + gen_size, zone_size - gen_size)
                offset_y = random.randint(-zone_size + gen_size, zone_size - gen_size)
                gen_x = center_x + offset_x
                gen_y = center_y + offset_y

                if 0 <= gen_y < self.world_height_tiles and 0 <= gen_x < self.world_width_tiles:
                    if self.layout[gen_y][gen_x] == 'concrete':
                        self.layout[gen_y][gen_x] = 'generator'

        elif zone_type == "warehouse":

            warehouse_width = min(zone_size - 2, random.randint(10, 15))
            warehouse_height = min(zone_size - 2, random.randint(8, 12))
            warehouse_x = center_x - warehouse_width // 2
            warehouse_y = center_y - warehouse_height // 2

            for y in range(warehouse_y, warehouse_y + warehouse_height):
                for x in range(warehouse_x, warehouse_x + warehouse_width):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        if x == warehouse_x or x == warehouse_x + warehouse_width - 1 or y == warehouse_y or y == warehouse_y + warehouse_height - 1:
                            self.layout[y][x] = 'wall'
                        else:
                            self.layout[y][x] = 'building'

        elif zone_type == "mine":

            pit_radius = min(zone_size - 2, random.randint(5, 8))
            for y in range(center_y - pit_radius, center_y + pit_radius + 1):
                for x in range(center_x - pit_radius, center_x + pit_radius + 1):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                        if dist <= pit_radius:
                            self.layout[y][x] = 'dirt'

            for _ in range(random.randint(6, 12)):
                offset_x = random.randint(-zone_size + 2, zone_size - 2)
                offset_y = random.randint(-zone_size + 2, zone_size - 2)
                x = center_x + offset_x
                y = center_y + offset_y

                dist_to_center = math.sqrt(offset_x**2 + offset_y**2)
                if dist_to_center > pit_radius and dist_to_center < zone_size and \
                   0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    if self.layout[y][x] == 'concrete':
                        self.layout[y][x] = random.choice(['machine', 'generator', 'conveyor'])

    def _check_area_clear(self, start_x, start_y, width, height, allowed_tiles):
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if not (0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles):
                    return False
                if self.layout[y][x] not in allowed_tiles:
                    return False
        return True

    def _draw_path(self, start_pos, end_pos, path_type, place_on_tiles, straightness=0.5):
        x1, y1 = start_pos
        x2, y2 = end_pos

        if abs(x2 - x1) + abs(y2 - y1) <= 3:

            points = self._get_line_points(x1, y1, x2, y2)
            for x, y in points:
                if (0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles and
                    self.layout[y][x] in place_on_tiles):
                    self.layout[y][x] = path_type
            return

        if random.random() < straightness:

            mid_x, mid_y = x2, y1
        else:

            mid_x, mid_y = x1, y2

        points1 = self._get_line_points(x1, y1, mid_x, mid_y)

        points2 = self._get_line_points(mid_x, mid_y, x2, y2)

        all_points = points1 + points2[1:]

        for x, y in all_points:
            if (0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles and
                self.layout[y][x] in place_on_tiles):
                self.layout[y][x] = path_type

    def _get_line_points(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return points

    def _create_rect_structure(self, start_x, start_y, width, height, structure_type, place_on_tiles, border_type=None):

        if not self._check_area_clear(start_x, start_y, width, height, place_on_tiles):
            return False

        if border_type is None:
            if structure_type == 'building':
                border_type = 'wall'
            else:
                border_type = structure_type

        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if (x == start_x or x == start_x + width - 1 or
                    y == start_y or y == start_y + height - 1):

                    self.layout[y][x] = border_type
                else:

                    self.layout[y][x] = structure_type

        return True

    def _create_circular_structure(self, center_x, center_y, radius, structure_type, place_on_tiles):

        area_clear = True
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if dist <= radius:
                    if not (0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles):
                        area_clear = False
                        break
                    if self.layout[y][x] not in place_on_tiles:
                        area_clear = False
                        break
            if not area_clear:
                break

        if not area_clear:
            return False

        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if dist <= radius and 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    self.layout[y][x] = structure_type

        return True

    def _create_complex_structure(self, start_x, start_y, width, height, structure_types, place_on_tiles):

        pass

    def _scatter_points_in_zone(self, center_x, center_y, radius, num_points, min_dist=1, start_radius=0):

        pass

    def _connect_points(self, points, path_type, place_on_tiles, max_connections=None, straightness=0.5):

        pass

    def _add_loading_docks(self, building_x, building_y, building_w, building_h):

        pass

    def _create_pit_area(self, center_x, center_y, radius):

        pass

    def _add_urban_zones(self):

        pass

    def _add_radioactive_zones(self):
        num_zones = random.randint(2, 5)
        print(f"  Tentando colocar {num_zones} zonas radioativas...")
        min_dist_from_spawn = 20

        for _ in range(num_zones):
            for attempt in range(30):
                zone_x = random.randint(self.world_width_tiles // 8, self.world_width_tiles * 7 // 8)
                zone_y = random.randint(self.world_height_tiles // 8, self.world_height_tiles * 7 // 8)
                zone_radius = random.randint(4, 8)

                spawn_dist = math.sqrt((zone_x - self.spawn_point[0])**2 + (zone_y - self.spawn_point[1])**2)
                if spawn_dist < zone_radius + min_dist_from_spawn: continue

                for y in range(max(1, zone_y - zone_radius), min(self.world_height_tiles - 1, zone_y + zone_radius + 1)):
                    for x in range(max(1, zone_x - zone_radius), min(self.world_width_tiles - 1, zone_x + zone_radius + 1)):
                        dist_sq = (x - zone_x)**2 + (y - zone_y)**2
                        if dist_sq <= zone_radius**2 and random.random() < 0.8 * (1 - math.sqrt(dist_sq) / zone_radius):
                            if self.layout[y][x] not in ['water', 'wall', 'building', 'machine', 'tank', 'pipe', 'barrier']:
                                self.layout[y][x] = 'radioactive'
                placed = True; break

    def _add_industrial_perimeter(self, center_x, center_y, zone_size):

        pass

    def _create_transition_zone(self, center_x, center_y, zone_size):

        pass

    def _add_environmental_effects(self, center_x, center_y, zone_size):

        pass

    def create_level(self):
        self.generate_layout()
        print("Instanciando tiles...")

        tile_type_to_asset = {
            'grass': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Grass/tile_0048_grass25.png',
            'dirt': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Dirt/tile_0023_dirt24.png',
            'water': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Water/tile_0101_water28.png',
            'concrete': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0102_asphalt1.png',
            'concrete_oil_stain': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0126_asphalt25.png',
            'radioactive': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Dirt/tile_0005_dirt6.png'
        }

        for y, row in enumerate(self.layout):
            for x, tile_type in enumerate(row):

                groups = [self.game.all_sprites, self.game.world_tiles]
                is_obstacle = False

                if tile_type == 'wall':

                    asset_key = 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0114_asphalt13.png'
                    Obstacle(self.game, x, y, groups, kind='wall', asset_key=asset_key)
                    is_obstacle = True
                elif tile_type == 'water':

                    asset_key = tile_type_to_asset.get(tile_type)
                    Tile(self.game, x, y, groups, kind='water', asset_key=asset_key)
                elif tile_type == 'tree':

                    tree_types = [
                        'assets/images/tds-modern-tilesets-environment/PNG/Trees Bushes/TDS04_0022_Tree1.png',
                        'assets/images/tds-modern-tilesets-environment/PNG/Trees Bushes/TDS04_0023_Tree2.png',
                        'assets/images/tds-modern-tilesets-environment/PNG/Trees Bushes/TDS04_0024_Tree3.png',
                        'assets/images/tds-modern-tilesets-environment/PNG/Trees Bushes/TDS04_0025_Tree4.png',
                    ]
                    asset_key = random.choice(tree_types)
                    Obstacle(self.game, x, y, groups, kind='tree', asset_key=asset_key)
                    is_obstacle = True
                elif tile_type == 'radioactive':

                    asset_key = tile_type_to_asset.get(tile_type)
                    RadioactiveZone(self.game, x, y, groups, asset_key=asset_key)
                    is_obstacle = True
                elif tile_type in ['building', 'machine', 'pipe', 'tank', 'crane', 'generator',
                                   'cooling_tower', 'conveyor', 'chimney', 'barrier']:

                    structure_to_asset = {
                        'building': 'assets/images/tds-modern-tilesets-environment/PNG/House/TDS04_House02.png',
                        'machine': 'assets/images/tds-modern-tilesets-environment/PNG/Crates Barrels/barrel_01.png',
                        'pipe': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0120_asphalt19.png',
                        'tank': 'assets/images/tds-modern-tilesets-environment/PNG/SandBag/sandbag_01.png',
                        'crane': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0118_asphalt17.png',
                        'generator': 'assets/images/tds-modern-tilesets-environment/PNG/Crates Barrels/crate_01.png',
                        'cooling_tower': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0118_asphalt17.png',
                        'conveyor': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0116_asphalt15.png',
                        'chimney': 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0118_asphalt17.png',
                        'barrier': 'assets/images/tds-modern-tilesets-environment/PNG/SandBag/sandbag_01.png'
                    }
                    asset_key = structure_to_asset.get(tile_type, 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Asphalt/tile_0114_asphalt13.png')
                    Obstacle(self.game, x, y, groups, kind=tile_type, asset_key=asset_key)
                    is_obstacle = True
                else:

                    asset_key = tile_type_to_asset.get(tile_type, 'assets/images/tds-modern-tilesets-environment/PNG/Tileset_v2/Tiles/Grass/tile_0024_grass1.png')
                    Tile(self.game, x, y, groups, kind=tile_type, asset_key=asset_key)

        self._add_filter_modules(num_modules=FILTER_MODULE_COUNT)

        self._add_reinforced_masks(num_masks=REINFORCED_MASK_COUNT)

        print(f"Nível criado. Ponto de spawn: {self.spawn_point}")
        return self.spawn_point

    def _add_filter_modules(self, num_modules=3):
        if not hasattr(self.game, 'items'): self.game.items = pygame.sprite.Group()
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()

        try:
            from items.filter_module import FilterModule
        except ImportError as e:
            print(f"Erro ao importar FilterModule: {e}. Itens não serão adicionados.")
            return

        placed_locations = []
        walkable_tiles = ['grass', 'dirt', 'concrete']
        min_dist_from_spawn = 25
        min_dist_between_items = 15
        padding = 5

        print(f"  Tentando colocar {num_modules} módulos de filtro...")
        attempts_per_module = 100
        modules_placed = 0

        for _ in range(num_modules):
            placed = False
            for attempt in range(attempts_per_module):

                x = random.randint(padding, self.world_width_tiles - 1 - padding)
                y = random.randint(padding, self.world_height_tiles - 1 - padding)

                if self.layout[y][x] not in walkable_tiles:
                    continue

                spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
                if spawn_dist < min_dist_from_spawn:
                    continue

                too_close = False
                for px, py in placed_locations:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist_between_items:
                        too_close = True
                        break
                if too_close:
                    continue

                pixel_x = x * TILE_SIZE + TILE_SIZE // 2
                pixel_y = y * TILE_SIZE + TILE_SIZE // 2

                FilterModule(self.game, pixel_x, pixel_y)
                placed_locations.append((x, y))
                modules_placed += 1
                placed = True
                break

            if not placed:
                print(f"    Não foi possível encontrar localização para um módulo após {attempts_per_module} tentativas.")

        print(f"  {modules_placed}/{num_modules} módulos de filtro colocados.")

    def _add_reinforced_masks(self, num_masks=2):

        if not hasattr(self.game, 'items'): self.game.items = pygame.sprite.Group()
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()

        try:
            from items.reinforced_mask import ReinforcedMask
        except ImportError as e:
            print(f"Erro ao importar ReinforcedMask: {e}. Máscaras não serão adicionadas.")
            return

        placed_locations = []
        walkable_tiles = ['grass', 'dirt', 'concrete']
        min_dist_from_spawn = 20
        min_dist_between_items = 12
        padding = 5

        print(f"  Tentando colocar {num_masks} máscaras reforçadas...")
        attempts_per_item = 100
        masks_placed = 0

        for _ in range(num_masks):
            placed = False
            for attempt in range(attempts_per_item):

                x = random.randint(padding, self.world_width_tiles - 1 - padding)
                y = random.randint(padding, self.world_height_tiles - 1 - padding)

                if self.layout[y][x] not in walkable_tiles:
                    continue

                spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
                if spawn_dist < min_dist_from_spawn:
                    continue

                too_close = False
                for px, py in placed_locations:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist_between_items:
                        too_close = True
                        break
                if too_close:
                    continue

                pixel_x = x * TILE_SIZE + TILE_SIZE // 2
                pixel_y = y * TILE_SIZE + TILE_SIZE // 2

                ReinforcedMask(self.game, pixel_x, pixel_y)
                placed_locations.append((x, y))
                masks_placed += 1
                placed = True
                break

            if not placed:
                print(f"    Não foi possível encontrar localização para uma máscara após {attempts_per_item} tentativas.")

        print(f"  {masks_placed}/{num_masks} máscaras reforçadas colocadas.")

    def _generate_collectible_items(self):
        print("Gerando itens coletáveis...")

        self._spawn_ammo_items(8)

        self._spawn_health_packs(5)

        self._spawn_mask_items(3)

    def _spawn_ammo_items(self, count):
        placed = 0
        attempts = 0
        max_attempts = count * 50

        while placed < count and attempts < max_attempts:
            attempts += 1

            x = random.randint(5, self.world_width_tiles - 5)
            y = random.randint(5, self.world_height_tiles - 5)

            if self.layout[y][x] not in ['grass', 'dirt', 'concrete']:
                continue

            spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
            if spawn_dist < 10:
                continue

            pixel_x = x * TILE_SIZE + TILE_SIZE // 2
            pixel_y = y * TILE_SIZE + TILE_SIZE // 2

            ammo_item = AmmoItem("pistol", 15)
            ammo_item.load_icon(self.game.asset_manager)

            Collectible(self.game, pixel_x, pixel_y, ammo_item)
            placed += 1

        print(f"  {placed}/{count} itens de munição colocados.")

    def _spawn_health_packs(self, count):
        placed = 0
        attempts = 0
        max_attempts = count * 50

        while placed < count and attempts < max_attempts:
            attempts += 1

            x = random.randint(5, self.world_width_tiles - 5)
            y = random.randint(5, self.world_height_tiles - 5)

            if self.layout[y][x] not in ['grass', 'dirt', 'concrete']:
                continue

            spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
            if spawn_dist < 15:
                continue

            pixel_x = x * TILE_SIZE + TILE_SIZE // 2
            pixel_y = y * TILE_SIZE + TILE_SIZE // 2

            health_item = HealthPackItem()
            health_item.load_icon(self.game.asset_manager)

            Collectible(self.game, pixel_x, pixel_y, health_item)
            placed += 1

        print(f"  {placed}/{count} kits médicos colocados.")

    def _spawn_mask_items(self, count):
        placed = 0
        attempts = 0
        max_attempts = count * 50

        while placed < count and attempts < max_attempts:
            attempts += 1

            x = random.randint(5, self.world_width_tiles - 5)
            y = random.randint(5, self.world_height_tiles - 5)

            if self.layout[y][x] not in ['grass', 'dirt', 'concrete']:
                continue

            spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
            if spawn_dist < 20:
                continue

            pixel_x = x * TILE_SIZE + TILE_SIZE // 2
            pixel_y = y * TILE_SIZE + TILE_SIZE // 2

            mask_item = MaskItem()
            mask_item.load_icon(self.game.asset_manager)

            Collectible(self.game, pixel_x, pixel_y, mask_item)
            placed += 1

        print(f"  {placed}/{count} máscaras colocadas.")
