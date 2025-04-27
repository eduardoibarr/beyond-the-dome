import pygame
import random
import math
# Import settings relative to project root
from core.settings import *
from utils.drawing import simple_noise
from entities.tile import Tile
from entities.obstacle import Obstacle, Water
from entities.radioactive_zone import RadioactiveZone
# Import camera from its new location
from graphics.camera import Camera

class LevelGenerator:
    """Generates the procedural game world layout and populates it with tiles."""
    def __init__(self, game):
        """
        Initializes the LevelGenerator.
        Args:
            game: Reference to the main game object.
        """
        self.game = game
        # Calculate map dimensions in tiles
        self.world_width_tiles = MAP_WIDTH // TILE_SIZE
        self.world_height_tiles = MAP_HEIGHT // TILE_SIZE
        self.layout = [] # 2D list representing the tile types
        # Ensure spawn point is calculated correctly based on tile dimensions
        self.spawn_point = (self.world_width_tiles // 2, self.world_height_tiles // 2)
        self.industrial_centers = [] # Keep track of placed industrial zones

    def generate_layout(self):
        """
        Generates the 2D layout grid for the world using noise functions.
        Returns:
            list[list[str]]: The generated 2D layout grid.
        """
        print("Generating level layout...")
        # Initialize layout with a base terrain type (e.g., grass)
        self.layout = [['grass' for _ in range(self.world_width_tiles)] for _ in range(self.world_height_tiles)]
        self.industrial_centers = [] # Reset for new generation

        # --- Noise Setup ---
        seed1 = random.random() * 100 # Base terrain / elevation
        seed2 = random.random() * 100 # Water bodies
        seed3 = random.random() * 100 # Forests / Trees
        seed4 = random.random() * 100 # Industrial zone placement noise
        terrain_scale = 80.0
        water_scale = 120.0
        forest_scale = 60.0
        industrial_placement_scale = 150.0

        # --- Generate Base Terrain (Water, Dirt, Grass) ---
        print("Generating base terrain...")
        for y in range(self.world_height_tiles):
            for x in range(self.world_width_tiles):
                terrain_value = simple_noise(x, y, seed1, scale=terrain_scale)
                water_value = simple_noise(x, y, seed2, scale=water_scale)
                if water_value < -0.55:
                    self.layout[y][x] = 'water'
                elif terrain_value < -0.4 and self.layout[y][x] != 'water':
                    self.layout[y][x] = 'dirt'
                # Else remains 'grass'

        # --- Generate Forests ---
        print("Generating forests...")
        for y in range(self.world_height_tiles):
            for x in range(self.world_width_tiles):
                if self.layout[y][x] == 'grass':
                    forest_value = simple_noise(x, y, seed3, scale=forest_scale)
                    if forest_value > 0.55:
                        self.layout[y][x] = 'tree'

        # --- Generate Industrial Zones ---
        print("Generating industrial zones...")
        self._add_industrial_zones(seed4, industrial_placement_scale)

        # --- Generate Urban Zones ---
        print("Generating urban zones...")
        self._add_urban_zones()

        # --- Generate Radioactive Zones ---
        print("Generating radioactive zones...")
        self._add_radioactive_zones()

        # --- Clear Spawn Area ---
        print("Clearing spawn area...")
        # Ensure spawn point is valid before clearing
        if not (0 <= self.spawn_point[0] < self.world_width_tiles and 0 <= self.spawn_point[1] < self.world_height_tiles):
             print(f"Warning: Initial spawn point {self.spawn_point} is outside map bounds. Resetting to center.")
             self.spawn_point = (self.world_width_tiles // 2, self.world_height_tiles // 2)
        self._clear_spawn_area(radius=7)

        # --- Add Map Borders ---
        print("Adding map borders...")
        self._add_map_borders()

        print("Layout generation complete.")
        return self.layout

    def _clear_spawn_area(self, radius=5):
        """Ensures the area around the spawn point is clear of obstacles."""
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
                # Check bounds just in case
                if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    dist_sq = (x - spawn_x)**2 + (y - spawn_y)**2
                    if dist_sq <= radius**2: # Circular clear zone
                        if self.layout[y][x] in clear_types:
                            self.layout[y][x] = 'grass' # Replace with a safe tile type

    def _add_map_borders(self):
        """Adds an impassable border around the entire map."""
        if self.world_height_tiles <= 0 or self.world_width_tiles <= 0: return # No map to border

        # Top and Bottom borders
        for x in range(self.world_width_tiles):
            if self.world_height_tiles > 0: self.layout[0][x] = 'wall'
            if self.world_height_tiles > 1: self.layout[self.world_height_tiles - 1][x] = 'wall'
        # Left and Right borders
        for y in range(self.world_height_tiles):
            if self.world_width_tiles > 0: self.layout[y][0] = 'wall'
            if self.world_width_tiles > 1: self.layout[y][self.world_width_tiles - 1] = 'wall'

    def _add_industrial_zones(self, seed, scale):
        """Adds several complex industrial zones to the map."""
        num_zones = random.randint(3, 6)
        print(f"  Attempting to place {num_zones} industrial zones...")
        min_dist_between_zones = 40
        min_dist_from_spawn = 30
        padding = max(15, self.world_width_tiles // 8) # Ensure padding is reasonable

        for zone_index in range(num_zones):
            placed = False
            for attempt in range(50):
                noise_x = simple_noise(zone_index * 10, attempt, seed, scale)
                noise_y = simple_noise(attempt, zone_index * 10, seed * 1.2, scale)

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

                if self.layout[zone_y][zone_x] == 'water': continue # Avoid center in water

                print(f"    Placing zone {zone_index+1} at ({zone_x}, {zone_y}) size {zone_size}")
                self.industrial_centers.append((zone_x, zone_y, zone_size))
                zone_type = random.choice(["factory", "refinery", "power_plant", "warehouse", "mine"])
                print(f"      Type: {zone_type}")

                self._create_industrial_floor(zone_x, zone_y, zone_size)
                self._add_specific_industrial_structures(zone_x, zone_y, zone_size, zone_type)
                self._add_industrial_perimeter(zone_x, zone_y, zone_size)
                self._create_transition_zone(zone_x, zone_y, zone_size)
                self._add_environmental_effects(zone_x, zone_y, zone_size)
                placed = True; break
            if not placed: print(f"    Could not find suitable location for zone {zone_index+1}.")

    def _create_industrial_floor(self, center_x, center_y, radius):
        """Creates an irregular concrete floor area."""
        # print(f"      Creating floor for zone at ({center_x}, {center_y}) radius {radius}")
        shape_seed = random.random() * 50
        shape_scale = 15.0
        min_rad = int(radius * 0.6)
        max_rad = int(radius * 1.1)

        for y in range(max(1, center_y - max_rad), min(self.world_height_tiles - 1, center_y + max_rad)):
            for x in range(max(1, center_x - max_rad), min(self.world_width_tiles - 1, center_x + max_rad)):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                angle = math.atan2(y - center_y, x - center_x)
                noise_val = simple_noise(math.cos(angle) * radius, math.sin(angle) * radius, shape_seed, shape_scale)
                current_max_radius = radius + noise_val * (radius * 0.3)
                current_max_radius = max(min_rad, min(max_rad, current_max_radius))

                if dist <= current_max_radius:
                    if self.layout[y][x] != 'water':
                        self.layout[y][x] = 'concrete'

    def _add_specific_industrial_structures(self, center_x, center_y, zone_size, zone_type):
        """Adds structures like buildings, tanks, machines based on zone type."""
        # Implementações das estruturas específicas para cada tipo de zona industrial
        # (factory, refinery, power_plant, warehouse, mine)
        pass

    def _check_area_clear(self, start_x, start_y, width, height, allowed_tiles):
        """Checks if a rectangular area contains only allowed tile types."""
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if not (0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles):
                    return False # Out of bounds
                if self.layout[y][x] not in allowed_tiles:
                    return False # Contains disallowed tile
        return True

    def _create_rect_structure(self, start_x, start_y, width, height, structure_type, place_on_tiles, border_type=None):
        """Creates a rectangular structure if the area is valid. Returns success and final rect."""
        # Implementação da criação de estruturas retangulares
        pass

    def _create_circular_structure(self, center_x, center_y, radius, structure_type, place_on_tiles):
        """Creates a circular structure. Returns success and center/radius."""
        # Implementação da criação de estruturas circulares
        pass

    def _create_complex_structure(self, start_x, start_y, width, height, structure_types, place_on_tiles):
        """Creates a structure with a mix of types."""
        # Implementação da criação de estruturas complexas
        pass

    def _scatter_points_in_zone(self, center_x, center_y, radius, num_points, min_dist=1, start_radius=0):
        """Scatters points randomly within a circular zone, ensuring minimum distance."""
        # Implementação da dispersão de pontos em uma zona
        pass

    def _connect_points(self, points, path_type, place_on_tiles, max_connections=None, straightness=0.5):
        """Connects a list of points with paths using minimum spanning tree idea (simplified)."""
        # Implementação da conexão de pontos
        pass

    def _draw_path(self, start_pos, end_pos, path_type, place_on_tiles, straightness=0.5):
        """Draws a path between two points using a simple randomized algorithm."""
        # Implementação do desenho de caminhos
        pass

    def _add_loading_docks(self, building_x, building_y, building_w, building_h):
        """Adds concrete pads and potential doors to warehouse walls."""
        # Implementação da adição de docas de carregamento
        pass

    def _create_pit_area(self, center_x, center_y, radius):
        """Creates a depression for a mine pit."""
        # Implementação da criação de áreas de escavação
        pass

    def _add_urban_zones(self):
        """Adds simpler urban zones with buildings."""
        # Implementação da adição de zonas urbanas
        pass

    def _add_radioactive_zones(self):
        """Adds patches of radioactive terrain."""
        num_zones = random.randint(2, 5)
        print(f"  Attempting to place {num_zones} radioactive zones...")
        min_dist_from_spawn = 20

        for _ in range(num_zones):
            placed = False
            for attempt in range(30):
                zone_x = random.randint(self.world_width_tiles // 8, self.world_width_tiles * 7 // 8)
                zone_y = random.randint(self.world_height_tiles // 8, self.world_height_tiles * 7 // 8)
                zone_radius = random.randint(4, 8)

                spawn_dist = math.sqrt((zone_x - self.spawn_point[0])**2 + (zone_y - self.spawn_point[1])**2)
                if spawn_dist < zone_radius + min_dist_from_spawn: continue

                # print(f"    Placing radioactive zone at ({zone_x}, {zone_y}) radius {zone_radius}")
                # Create irregular radioactive patch
                for y in range(max(1, zone_y - zone_radius), min(self.world_height_tiles - 1, zone_y + zone_radius + 1)):
                    for x in range(max(1, zone_x - zone_radius), min(self.world_width_tiles - 1, zone_x + zone_radius + 1)):
                        dist_sq = (x - zone_x)**2 + (y - zone_y)**2
                        if dist_sq <= zone_radius**2 and random.random() < 0.8 * (1 - math.sqrt(dist_sq) / zone_radius):
                            if self.layout[y][x] not in ['water', 'wall', 'building', 'machine', 'tank', 'pipe', 'barrier']: # Avoid structures/water/barriers
                                self.layout[y][x] = 'radioactive'
                placed = True; break
            # if not placed: print("    Could not place radioactive zone.")

    def _add_industrial_perimeter(self, center_x, center_y, zone_size):
        """Adds barriers around the edge of an industrial zone."""
        # Implementação da adição de perímetros industriais
        pass

    def _create_transition_zone(self, center_x, center_y, zone_size):
        """Blends the industrial zone edge with the surrounding terrain."""
        # Implementação da criação de zonas de transição
        pass

    def _add_environmental_effects(self, center_x, center_y, zone_size):
        """Adds visual effects like oil stains by changing tile kinds."""
        # Implementação da adição de efeitos ambientais
        pass

    def create_level(self):
        """
        Generates the layout and creates all the necessary Tile sprites.
        Returns:
            tuple: The (x, y) tile coordinates for player spawn.
        """
        layout = self.generate_layout()

        # Define which tile kinds are obstacles (used by Obstacle class check)
        obstacle_types = [
            'wall', 'barrier', 'tree', 'building', 'machine', 'pipe',
            'tank', 'crane', 'generator', 'cooling_tower', 'conveyor', 'chimney'
            # Note: 'water' is handled separately via the Water class inheriting Obstacle
        ]

        print("Creating sprites from layout...")
        # Iterate through the generated layout and create sprites
        # Ensure game groups exist
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()
        if not hasattr(self.game, 'world_tiles'): self.game.world_tiles = pygame.sprite.Group()
        if not hasattr(self.game, 'obstacles'): self.game.obstacles = pygame.sprite.Group()
        if not hasattr(self.game, 'radioactive_zones'): self.game.radioactive_zones = pygame.sprite.Group()
        if not hasattr(self.game, 'items'): self.game.items = pygame.sprite.Group()


        for y, row in enumerate(layout):
            for x, tile_type in enumerate(row):
                common_groups = self.game.all_sprites, self.game.world_tiles # Groups for most tiles

                if tile_type in ['grass', 'dirt', 'concrete', 'concrete_oil_stain']:
                    Tile(self.game, x, y, common_groups, tile_type)
                elif tile_type in obstacle_types:
                    Obstacle(self.game, x, y, common_groups, tile_type)
                elif tile_type == 'radioactive':
                    RadioactiveZone(self.game, x, y, common_groups)
                elif tile_type == 'water':
                    Water(self.game, x, y, common_groups) # Water is an Obstacle
                # else: tile_type might be None or an unhandled type - implicitly empty/ignored

        # Add collectible items (Filter Modules)
        print("Adding filter modules...")
        self._add_filter_modules(num_modules=FILTER_MODULE_COUNT) # Use constant from settings

        # Configure the camera based on the final map size
        self.game.camera = Camera(MAP_WIDTH, MAP_HEIGHT)

        print("Level creation complete.")
        # Ensure spawn point is valid tile coordinates
        spawn_tile_x = max(0, min(self.world_width_tiles - 1, self.spawn_point[0]))
        spawn_tile_y = max(0, min(self.world_height_tiles - 1, self.spawn_point[1]))
        print(f"Player spawn tile: ({spawn_tile_x}, {spawn_tile_y})")
        return (spawn_tile_x, spawn_tile_y)


    def _add_filter_modules(self, num_modules=3):
        """Adds collectible FilterModule items to the map."""
        # Implementação da adição de módulos de filtro
        pass 