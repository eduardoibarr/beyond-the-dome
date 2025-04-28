import pygame
import random
import math
from core.settings import *
from core.noise_generator import NoiseGenerator
from entities.tile import Tile
from entities.obstacle import Obstacle
from entities.radioactive_zone import RadioactiveZone

class LevelGenerator:
    """Gera o layout procedural do mundo do jogo e o preenche com tiles."""
    def __init__(self, game):
        """
        Inicializa o LevelGenerator.
        Args:
            game: Referência para o objeto principal do jogo.
        """
        self.game = game
        # Calcular as dimensões do mapa em tiles
        self.world_width_tiles = MAP_WIDTH // TILE_SIZE
        self.world_height_tiles = MAP_HEIGHT // TILE_SIZE
        # Dimensões em pixels
        self.map_width_pixels = MAP_WIDTH
        self.map_height_pixels = MAP_HEIGHT
        self.layout = [] # Lista 2D representando os tipos de tile
        # Garantir que o ponto de spawn seja calculado corretamente com base nas dimensões do tile
        self.spawn_point = (self.world_width_tiles // 2, self.world_height_tiles // 2)
        self.industrial_centers = [] # Manter o controle das zonas industriais colocadas
        
        # Inicializa o gerador de ruído
        self.noise_generator = NoiseGenerator(
            seed=random.randint(0, 1000),
            scale=100.0,
            octaves=6,
            persistence=0.5,
            lacunarity=2.0
        )

    def generate_layout(self):
        """
        Gera a grade de layout 2D para o mundo usando funções de ruído.
        Returns:
            list[list[str]]: A grade de layout 2D gerada.
        """
        print("Gerando layout do nível...")
        # Inicializar o layout com um tipo de terreno base (ex: grama)
        self.layout = [['grass' for _ in range(self.world_width_tiles)] for _ in range(self.world_height_tiles)]
        self.industrial_centers = [] # Redefinir para nova geração

        # --- Configuração do Ruído ---
        seed1 = random.random() * 100 # Terreno base / elevação
        seed2 = random.random() * 100 # Corpos d'água
        seed3 = random.random() * 100 # Florestas / Árvores
        seed4 = random.random() * 100 # Ruído para posicionamento de zonas industriais
        terrain_scale = 80.0
        water_scale = 120.0
        forest_scale = 60.0
        industrial_placement_scale = 150.0

        # --- Gerar Terreno Base (Água, Terra, Grama) ---
        print("Gerando terreno base...")
        for y in range(self.world_height_tiles):
            for x in range(self.world_width_tiles):
                terrain_value = self.noise_generator.get_noise_2d(x + seed1, y + seed1)
                water_value = self.noise_generator.get_noise_2d(x + seed2, y + seed2)
                
                # Verifica se o tile está próximo do spawn point
                spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
                if spawn_dist < 10:  # Área segura ao redor do spawn
                    self.layout[y][x] = 'grass'
                    continue
                
                if water_value < -0.55:
                    # Verifica se a água não está isolando áreas
                    if self._is_isolating_water(x, y):
                        self.layout[y][x] = 'grass'
                    else:
                        self.layout[y][x] = 'water'
                elif terrain_value < -0.4 and self.layout[y][x] != 'water':
                    self.layout[y][x] = 'dirt'
                else:
                    self.layout[y][x] = 'grass'

        # --- Gerar Florestas ---
        print("Gerando florestas...")
        for y in range(self.world_height_tiles):
            for x in range(self.world_width_tiles):
                if self.layout[y][x] == 'grass':
                    forest_value = self.noise_generator.get_noise_2d(x + seed3, y + seed3)
                    if forest_value > 0.55:
                        # Verifica se a árvore não está isolando áreas
                        if not self._is_isolating_tree(x, y):
                            self.layout[y][x] = 'tree'

        # --- Gerar Zonas Industriais ---
        print("Gerando zonas industriais...")
        self._add_industrial_zones(seed4, industrial_placement_scale)

        # --- Gerar Zonas Urbanas ---
        print("Gerando zonas urbanas...")
        self._add_urban_zones()

        # --- Gerar Zonas Radioativas ---
        print("Gerando zonas radioativas...")
        self._add_radioactive_zones()

        # --- Limpar Área de Spawn ---
        print("Limpando área de spawn...")
        # Garantir que o ponto de spawn seja válido antes de limpar
        if not (0 <= self.spawn_point[0] < self.world_width_tiles and 0 <= self.spawn_point[1] < self.world_height_tiles):
             print(f"Aviso: O ponto de spawn inicial {self.spawn_point} está fora dos limites do mapa. Redefinindo para o centro.")
             self.spawn_point = (self.world_width_tiles // 2, self.world_height_tiles // 2)
        self._clear_spawn_area(radius=7)

        # --- Adicionar Bordas do Mapa ---
        print("Adicionando bordas do mapa...")
        self._add_map_borders()

        print("Geração do layout completa.")
        return self.layout

    def _is_isolating_water(self, x, y):
        """Verifica se a adição de água em (x,y) criaria uma área isolada."""
        # Cria uma cópia temporária do layout para teste
        temp_layout = [row[:] for row in self.layout]
        temp_layout[y][x] = 'water'
        
        # Verifica se há caminho do spawn para as bordas
        return not self._has_path_to_border(temp_layout, self.spawn_point[0], self.spawn_point[1])

    def _is_isolating_tree(self, x, y):
        """Verifica se a adição de uma árvore em (x,y) criaria uma área isolada."""
        # Cria uma cópia temporária do layout para teste
        temp_layout = [row[:] for row in self.layout]
        temp_layout[y][x] = 'tree'
        
        # Verifica se há caminho do spawn para as bordas
        return not self._has_path_to_border(temp_layout, self.spawn_point[0], self.spawn_point[1])

    def _has_path_to_border(self, layout, start_x, start_y):
        """Verifica se existe um caminho de (start_x, start_y) até as bordas do mapa."""
        visited = set()
        queue = [(start_x, start_y)]
        
        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            # Se chegou a uma borda, retorna True
            if x == 0 or x == self.world_width_tiles - 1 or y == 0 or y == self.world_height_tiles - 1:
                return True
                
            # Verifica vizinhos
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.world_width_tiles and 
                    0 <= ny < self.world_height_tiles and 
                    layout[ny][nx] in ['grass', 'dirt'] and 
                    (nx, ny) not in visited):
                    queue.append((nx, ny))
                    
        return False

    def _clear_spawn_area(self, radius=5):
        """Garante que a área ao redor do ponto de spawn esteja livre de obstáculos."""
        spawn_x, spawn_y = self.spawn_point
        start_x = max(0, spawn_x - radius)
        end_x = min(self.world_width_tiles, spawn_x + radius + 1)
        start_y = max(0, spawn_y - radius)
        end_y = min(self.world_height_tiles, spawn_y + radius + 1)

        clear_types = ['wall', 'tree', 'water', 'building', 'machine', 'pipe', 'tank',
                       'crane', 'generator', 'cooling_tower', 'conveyor', 'chimney',
                       'barrier', 'radioactive']

        # Primeiro, limpa a área central
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    dist_sq = (x - spawn_x)**2 + (y - spawn_y)**2
                    if dist_sq <= radius**2:
                        if self.layout[y][x] in clear_types:
                            self.layout[y][x] = 'grass'

        # Depois, garante que haja pelo menos um caminho para cada direção
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            path_x, path_y = spawn_x + dx * (radius + 1), spawn_y + dy * (radius + 1)
            if (0 <= path_x < self.world_width_tiles and 
                0 <= path_y < self.world_height_tiles and 
                self.layout[path_y][path_x] in clear_types):
                self.layout[path_y][path_x] = 'grass'

    def _add_map_borders(self):
        """Adiciona uma borda intransponível ao redor de todo o mapa."""
        if self.world_height_tiles <= 0 or self.world_width_tiles <= 0: return # Sem mapa para bordar

        # Bordas Superior e Inferior
        for x in range(self.world_width_tiles):
            if self.world_height_tiles > 0: self.layout[0][x] = 'wall'
            if self.world_height_tiles > 1: self.layout[self.world_height_tiles - 1][x] = 'wall'
        # Bordas Esquerda e Direita
        for y in range(self.world_height_tiles):
            if self.world_width_tiles > 0: self.layout[y][0] = 'wall'
            if self.world_width_tiles > 1: self.layout[y][self.world_width_tiles - 1] = 'wall'

    def _add_industrial_zones(self, seed, scale):
        """Adiciona várias zonas industriais complexas ao mapa."""
        num_zones = random.randint(3, 6)
        print(f"  Tentando colocar {num_zones} zonas industriais...")
        min_dist_between_zones = 25  # Reduzido de 40 para 25
        min_dist_from_spawn = 20     # Reduzido de 30 para 20
        padding = max(10, self.world_width_tiles // 10)  # Reduzido de 15 para 10

        for zone_index in range(num_zones):
            placed = False
            for attempt in range(50):
                # Usa o seed recebido para variar as coordenadas do noise_generator
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
                
                if self.layout[zone_y][zone_x] == 'water': continue # Evitar o centro na água

                print(f"    Colocando zona {zone_index+1} em ({zone_x}, {zone_y}) tamanho {zone_size}")
                self.industrial_centers.append((zone_x, zone_y, zone_size))
                zone_type = random.choice(["factory", "refinery", "power_plant", "warehouse", "mine"])
                print(f"      Tipo: {zone_type}")

                self._create_industrial_floor(zone_x, zone_y, zone_size)
                self._add_specific_industrial_structures(zone_x, zone_y, zone_size, zone_type)
                self._add_industrial_perimeter(zone_x, zone_y, zone_size)
                self._create_transition_zone(zone_x, zone_y, zone_size)
                self._add_environmental_effects(zone_x, zone_y, zone_size)
                placed = True; break # Colocado com sucesso, passar para a próxima zona
            if not placed: print(f"    Não foi possível encontrar uma localização adequada para a zona {zone_index+1}.")

    def _create_industrial_floor(self, center_x, center_y, radius):
        """Cria uma área de piso de concreto irregular."""
        # print(f"      Criando piso para zona em ({center_x}, {center_y}) raio {radius}")
        shape_seed = random.random() * 50
        shape_scale = 15.0
        min_rad = int(radius * 0.6)
        max_rad = int(radius * 1.1)

        for y in range(max(1, center_y - max_rad), min(self.world_height_tiles - 1, center_y + max_rad)):
            for x in range(max(1, center_x - max_rad), min(self.world_width_tiles - 1, center_x + max_rad)):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                angle = math.atan2(y - center_y, x - center_x)
                # Ajusta a chamada para usar coordenadas modificadas pelo ângulo
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
        """Adiciona estruturas específicas para cada tipo de zona industrial."""
        if zone_type == "factory":
            # Fábrica: um edifício principal com máquinas ao redor
            building_width = min(zone_size - 4, random.randint(8, 12))
            building_height = min(zone_size - 4, random.randint(6, 10))
            building_x = center_x - building_width // 2
            building_y = center_y - building_height // 2
            
            # Cria o edifício principal
            for y in range(building_y, building_y + building_height):
                for x in range(building_x, building_x + building_width):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        if x == building_x or x == building_x + building_width - 1 or y == building_y or y == building_y + building_height - 1:
                            self.layout[y][x] = 'wall'
                        else:
                            self.layout[y][x] = 'building'
            
            # Adiciona algumas máquinas em volta do edifício
            for _ in range(random.randint(5, 10)):
                offset_x = random.randint(-zone_size + 2, zone_size - 2)
                offset_y = random.randint(-zone_size + 2, zone_size - 2)
                x = center_x + offset_x
                y = center_y + offset_y
                
                # Verifica se está fora do edifício e dentro do mapa
                if (x < building_x or x >= building_x + building_width or 
                    y < building_y or y >= building_y + building_height) and \
                   0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    if self.layout[y][x] == 'concrete':  # Coloca apenas em concreto
                        self.layout[y][x] = 'machine'
        
        elif zone_type == "refinery":
            # Refinaria: tanques e tubulações
            # Adiciona tanques
            for _ in range(random.randint(3, 6)):
                tank_radius = random.randint(2, 3)
                offset_x = random.randint(-zone_size + tank_radius, zone_size - tank_radius)
                offset_y = random.randint(-zone_size + tank_radius, zone_size - tank_radius)
                tank_x = center_x + offset_x
                tank_y = center_y + offset_y
                
                # Cria um tanque circular
                for y in range(tank_y - tank_radius, tank_y + tank_radius + 1):
                    for x in range(tank_x - tank_radius, tank_x + tank_radius + 1):
                        if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                            dist = math.sqrt((x - tank_x)**2 + (y - tank_y)**2)
                            if dist <= tank_radius and self.layout[y][x] == 'concrete':
                                self.layout[y][x] = 'tank'
            
            # Adiciona tubulações conectando os tanques
            for y in range(center_y - zone_size + 2, center_y + zone_size - 1):
                for x in range(center_x - zone_size + 2, center_x + zone_size - 1):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        if self.layout[y][x] == 'concrete' and random.random() < 0.05:
                            self.layout[y][x] = 'pipe'
        
        elif zone_type == "power_plant":
            # Usina de energia: torres de resfriamento e edifícios
            # Adiciona torres de resfriamento
            for _ in range(random.randint(2, 4)):
                tower_radius = random.randint(3, 4)
                offset_x = random.randint(-zone_size + tower_radius, zone_size - tower_radius)
                offset_y = random.randint(-zone_size + tower_radius, zone_size - tower_radius)
                tower_x = center_x + offset_x
                tower_y = center_y + offset_y
                
                # Cria uma torre circular
                for y in range(tower_y - tower_radius, tower_y + tower_radius + 1):
                    for x in range(tower_x - tower_radius, tower_x + tower_radius + 1):
                        if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                            dist = math.sqrt((x - tower_x)**2 + (y - tower_y)**2)
                            if dist <= tower_radius and self.layout[y][x] == 'concrete':
                                self.layout[y][x] = 'cooling_tower'
            
            # Adiciona geradores
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
            # Armazém: grandes edifícios retangulares
            warehouse_width = min(zone_size - 2, random.randint(10, 15))
            warehouse_height = min(zone_size - 2, random.randint(8, 12))
            warehouse_x = center_x - warehouse_width // 2
            warehouse_y = center_y - warehouse_height // 2
            
            # Cria o armazém
            for y in range(warehouse_y, warehouse_y + warehouse_height):
                for x in range(warehouse_x, warehouse_x + warehouse_width):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        if x == warehouse_x or x == warehouse_x + warehouse_width - 1 or y == warehouse_y or y == warehouse_y + warehouse_height - 1:
                            self.layout[y][x] = 'wall'
                        else:
                            self.layout[y][x] = 'building'
        
        elif zone_type == "mine":
            # Mina: escavações e máquinas
            # Cria um poço central
            pit_radius = min(zone_size - 2, random.randint(5, 8))
            for y in range(center_y - pit_radius, center_y + pit_radius + 1):
                for x in range(center_x - pit_radius, center_x + pit_radius + 1):
                    if 0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                        dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                        if dist <= pit_radius:
                            self.layout[y][x] = 'dirt'  # Fundo do poço é terra
            
            # Adiciona algumas máquinas e estruturas ao redor
            for _ in range(random.randint(6, 12)):
                offset_x = random.randint(-zone_size + 2, zone_size - 2)
                offset_y = random.randint(-zone_size + 2, zone_size - 2)
                x = center_x + offset_x
                y = center_y + offset_y
                
                # Verifica se está fora do poço e dentro do mapa
                dist_to_center = math.sqrt(offset_x**2 + offset_y**2)
                if dist_to_center > pit_radius and dist_to_center < zone_size and \
                   0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles:
                    if self.layout[y][x] == 'concrete':
                        self.layout[y][x] = random.choice(['machine', 'generator', 'conveyor'])

    def _check_area_clear(self, start_x, start_y, width, height, allowed_tiles):
        """Verifica se uma área retangular contém apenas tipos de tile permitidos."""
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if not (0 <= y < self.world_height_tiles and 0 <= x < self.world_width_tiles): 
                    return False # Fora dos limites
                if self.layout[y][x] not in allowed_tiles:
                    return False # Contém tile não permitido
        return True

    def _create_rect_structure(self, start_x, start_y, width, height, structure_type, place_on_tiles, border_type=None):
        """Cria uma estrutura retangular se a área for válida. Retorna sucesso e retângulo final."""
        # TODO: Implementar a criação de estruturas retangulares
        pass

    def _create_circular_structure(self, center_x, center_y, radius, structure_type, place_on_tiles):
        """Cria uma estrutura circular. Retorna sucesso e centro/raio."""
        # TODO: Implementar a criação de estruturas circulares
        pass

    def _create_complex_structure(self, start_x, start_y, width, height, structure_types, place_on_tiles):
        """Cria uma estrutura com uma mistura de tipos."""
        # TODO: Implementar a criação de estruturas complexas
        pass

    def _scatter_points_in_zone(self, center_x, center_y, radius, num_points, min_dist=1, start_radius=0):
        """Espalha pontos aleatoriamente dentro de uma zona circular, garantindo distância mínima."""
        # TODO: Implementar a dispersão de pontos em uma zona
        pass

    def _connect_points(self, points, path_type, place_on_tiles, max_connections=None, straightness=0.5):
        """Conecta uma lista de pontos com caminhos usando ideia de árvore geradora mínima (simplificada)."""
        # TODO: Implementar a conexão de pontos
        pass

    def _draw_path(self, start_pos, end_pos, path_type, place_on_tiles, straightness=0.5):
        """Desenha um caminho entre dois pontos usando um algoritmo simples randomizado."""
        # TODO: Implementar o desenho de caminhos
        pass

    def _add_loading_docks(self, building_x, building_y, building_w, building_h):
        """Adiciona plataformas de concreto e possíveis portas às paredes do armazém."""
        # TODO: Implementar a adição de docas de carregamento
        pass

    def _create_pit_area(self, center_x, center_y, radius):
        """Cria uma depressão para uma área de mina."""
        # TODO: Implementar a criação de áreas de escavação
        pass

    def _add_urban_zones(self):
        """Adiciona zonas urbanas mais simples com edifícios."""
        # TODO: Implementar a adição de zonas urbanas
        pass

    def _add_radioactive_zones(self):
        """Adiciona manchas de terreno radioativo."""
        num_zones = random.randint(2, 5)
        print(f"  Tentando colocar {num_zones} zonas radioativas...")
        min_dist_from_spawn = 20 # Distância mínima do spawn

        for _ in range(num_zones):
            for attempt in range(30): # Tentar até 30 vezes
                zone_x = random.randint(self.world_width_tiles // 8, self.world_width_tiles * 7 // 8)
                zone_y = random.randint(self.world_height_tiles // 8, self.world_height_tiles * 7 // 8)
                zone_radius = random.randint(4, 8)

                spawn_dist = math.sqrt((zone_x - self.spawn_point[0])**2 + (zone_y - self.spawn_point[1])**2) # Distância para o spawn
                if spawn_dist < zone_radius + min_dist_from_spawn: continue

                # print(f"    Colocando zona radioativa em ({zone_x}, {zone_y}) raio {zone_radius}")
                # Cria mancha radioativa irregular
                for y in range(max(1, zone_y - zone_radius), min(self.world_height_tiles - 1, zone_y + zone_radius + 1)):
                    for x in range(max(1, zone_x - zone_radius), min(self.world_width_tiles - 1, zone_x + zone_radius + 1)):
                        dist_sq = (x - zone_x)**2 + (y - zone_y)**2
                        if dist_sq <= zone_radius**2 and random.random() < 0.8 * (1 - math.sqrt(dist_sq) / zone_radius):
                            if self.layout[y][x] not in ['water', 'wall', 'building', 'machine', 'tank', 'pipe', 'barrier']: # Evitar estruturas/água/barreiras
                                self.layout[y][x] = 'radioactive'
                placed = True; break
            # if not placed: print("    Não foi possível colocar a zona radioativa.")
        
    def _add_industrial_perimeter(self, center_x, center_y, zone_size):
        """Adiciona barreiras ao redor da borda de uma zona industrial."""
        # TODO: Implementar a adição de perímetros industriais
        pass

    def _create_transition_zone(self, center_x, center_y, zone_size):
        """Mistura a borda da zona industrial com o terreno circundante."""
        # TODO: Implementar a criação de zonas de transição
        pass

    def _add_environmental_effects(self, center_x, center_y, zone_size):
        """Adiciona efeitos visuais como manchas de óleo alterando os tipos de tile."""
        # TODO: Implementar a adição de efeitos ambientais
        pass

    def create_level(self):
        """
        Gera o layout do nível e instancia todos os objetos Tile.
        Returns:
            tuple: O ponto de spawn calculado (x, y) em coordenadas de tile.
        """
        self.generate_layout()
        print("Instanciando tiles...")

        for y, row in enumerate(self.layout):
            for x, tile_type in enumerate(row):
                # Determinar o(s) grupo(s) para o tile
                # Adiciona TODOS os tiles ao all_sprites para update/draw
                # Adiciona tiles não andáveis aos obstáculos
                groups = [self.game.all_sprites, self.game.world_tiles]
                is_obstacle = False
                
                if tile_type == 'wall':
                    # Passa tipo específico de parede se necessário (ex: 'wall_industrial', 'wall_metal')
                    Obstacle(self.game, x, y, groups, kind='wall')
                    is_obstacle = True # Adiciona aos obstáculos implicitamente via classe Obstacle
                elif tile_type == 'water':
                    # Água é tratada por Tile, mas também por Obstacle se não for andável
                    Tile(self.game, x, y, groups, kind='water')
                    # Se água deve ser um obstáculo:
                    # Obstacle(self.game, x, y, groups, kind='water') 
                    # is_obstacle = True
                elif tile_type == 'tree':
                    Obstacle(self.game, x, y, groups, kind='tree')
                    is_obstacle = True
                elif tile_type == 'radioactive':
                    # Zonas radioativas são obstáculos especiais
                    RadioactiveZone(self.game, x, y, groups)
                    is_obstacle = True # RadioactiveZone provavelmente se adiciona aos obstáculos
                elif tile_type in ['building', 'machine', 'pipe', 'tank', 'crane', 'generator', 
                                    'cooling_tower', 'conveyor', 'chimney', 'barrier']:
                    # Trata outras estruturas industriais como obstáculos
                    Obstacle(self.game, x, y, groups, kind=tile_type)
                    is_obstacle = True
                # --- ADICIONAR TRATAMENTO DE PONTE AQUI --- (será adicionado depois)
                # elif tile_type == 'bridge':
                #     Tile(self.game, x, y, groups, kind='bridge') # Andável, não é obstáculo
                else: # Tiles de piso padrão (grama, terra, concreto)
                    Tile(self.game, x, y, groups, kind=tile_type)
                
                # Nota: A classe Obstacle deve lidar com a adição de si mesma ao self.game.obstacles
                # Não é necessário adicionar manualmente tiles `is_obstacle` a esse grupo aqui se Obstacle fizer isso.

        # Adiciona os módulos de filtro após a criação do nível base
        self._add_filter_modules(num_modules=FILTER_MODULE_COUNT)
        # Adiciona as máscaras reforçadas
        self._add_reinforced_masks(num_masks=REINFORCED_MASK_COUNT) # Usa constante de settings.py

        print(f"Nível criado. Ponto de spawn: {self.spawn_point}")
        return self.spawn_point

    def _add_filter_modules(self, num_modules=3):
        """Adiciona itens coletáveis FilterModule ao mapa.
        
        Tenta colocar itens em tiles andáveis ('grass', 'dirt') longe do
        ponto de spawn e de outros itens.
        """
        if not hasattr(self.game, 'items'): self.game.items = pygame.sprite.Group()
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()
            
        # Importa tarde para evitar dependência circular se Item importar coisas do LevelGenerator
        try:
            from items.filter_module import FilterModule
        except ImportError as e:
            print(f"Erro ao importar FilterModule: {e}. Itens não serão adicionados.")
            return

        placed_locations = []
        walkable_tiles = ['grass', 'dirt', 'concrete'] # Define em quais tiles os itens podem spawnar
        min_dist_from_spawn = 25
        min_dist_between_items = 15
        padding = 5 # Evitar bordas

        print(f"  Tentando colocar {num_modules} módulos de filtro...")
        attempts_per_module = 100
        modules_placed = 0

        for _ in range(num_modules):
            placed = False
            for attempt in range(attempts_per_module):
                # Escolhe uma localização potencial aleatória
                x = random.randint(padding, self.world_width_tiles - 1 - padding)
                y = random.randint(padding, self.world_height_tiles - 1 - padding)

                # Verifica se o tile é andável
                if self.layout[y][x] not in walkable_tiles:
                    continue

                # Verifica distância do spawn
                spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
                if spawn_dist < min_dist_from_spawn:
                    continue

                # Verifica distância de outros itens
                too_close = False
                for px, py in placed_locations:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist_between_items:
                        too_close = True
                        break
                if too_close:
                    continue

                # Se todas as verificações passarem, coloca o item
                pixel_x = x * TILE_SIZE + TILE_SIZE // 2 # Centraliza o item no tile
                pixel_y = y * TILE_SIZE + TILE_SIZE // 2
                # O FilterModule deve se adicionar ao game.all_sprites e game.items via super().__init__
                FilterModule(self.game, pixel_x, pixel_y)
                placed_locations.append((x, y))
                modules_placed += 1
                placed = True
                # print(f"    Módulo colocado em ({x}, {y})")
                break # Vai para o próximo módulo
            
            if not placed:
                print(f"    Não foi possível encontrar localização para um módulo após {attempts_per_module} tentativas.")

        print(f"  {modules_placed}/{num_modules} módulos de filtro colocados.") 

    def _add_reinforced_masks(self, num_masks=2):
        """Adiciona itens coletáveis ReinforcedMask ao mapa."""
        # Garante que os grupos de sprites existem
        if not hasattr(self.game, 'items'): self.game.items = pygame.sprite.Group()
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()

        # Importa tarde para evitar dependência circular
        try:
            from items.reinforced_mask import ReinforcedMask
        except ImportError as e:
            print(f"Erro ao importar ReinforcedMask: {e}. Máscaras não serão adicionadas.")
            return

        # Reutiliza a lógica de posicionamento de _add_filter_modules
        # TODO: Considerar refatorar a lógica de posicionamento para uma função auxiliar comum
        placed_locations = [] # Pode ser necessário obter locais de módulos de filtro se a distância for entre *todos* os itens
        walkable_tiles = ['grass', 'dirt', 'concrete'] # Define em quais tiles os itens podem spawnar
        min_dist_from_spawn = 20 # Distância mínima do ponto de spawn inicial do jogador
        min_dist_between_items = 12 # Distância mínima entre máscaras (e talvez outros itens)
        padding = 5 # Para evitar colocar itens muito perto das bordas do mapa

        print(f"  Tentando colocar {num_masks} máscaras reforçadas...")
        attempts_per_item = 100
        masks_placed = 0

        for _ in range(num_masks):
            placed = False
            for attempt in range(attempts_per_item):
                # Escolhe uma localização potencial aleatória
                x = random.randint(padding, self.world_width_tiles - 1 - padding)
                y = random.randint(padding, self.world_height_tiles - 1 - padding)

                # Verifica se o tile é andável
                if self.layout[y][x] not in walkable_tiles:
                    continue

                # Verifica distância do spawn
                spawn_dist = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
                if spawn_dist < min_dist_from_spawn:
                    continue

                # Verifica distância de outras máscaras já colocadas
                too_close = False
                for px, py in placed_locations:
                    dist = math.sqrt((x - px)**2 + (y - py)**2)
                    if dist < min_dist_between_items:
                        too_close = True
                        break
                if too_close:
                    continue
                
                # TODO: Opcional - Verificar distância de Módulos de Filtro também
                # filter_module_locations = [...] # Obter locais dos módulos colocados anteriormente
                # for fpx, fpy in filter_module_locations:
                #    dist = math.sqrt((x - fpx)**2 + (y - fpy)**2)
                #    if dist < min_dist_between_items:
                #        too_close = True; break
                # if too_close: continue

                # Se todas as verificações passarem, coloca o item
                pixel_x = x * TILE_SIZE + TILE_SIZE // 2 # Centraliza o item no tile
                pixel_y = y * TILE_SIZE + TILE_SIZE // 2
                # ReinforcedMask se adiciona aos grupos via super().__init__
                ReinforcedMask(self.game, pixel_x, pixel_y)
                placed_locations.append((x, y))
                masks_placed += 1
                placed = True
                # print(f"    Máscara colocada em ({x}, {y})")
                break # Vai para a próxima máscara
            
            if not placed:
                print(f"    Não foi possível encontrar localização para uma máscara após {attempts_per_item} tentativas.")

        print(f"  {masks_placed}/{num_masks} máscaras reforçadas colocadas.") 