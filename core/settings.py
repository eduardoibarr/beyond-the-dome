# Importação da biblioteca Pygame
import pygame

# Configurações da janela do jogo
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Beyond the Dome"

# Definição das cores utilizadas no jogo
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255) # Adicionado para módulo de filtro/radiação
LIGHTBLUE = (173, 216, 230) # Adicionado para módulo de filtro
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREY = (128, 128, 128) # Adicionado cinza para prompt de introdução

# Configurações do tamanho dos tiles (movido para cima)
TILE_SIZE = 32

# Configurações do jogador
PLAYER_COLOR = (0, 200, 0) # Verde
PLAYER_SPEED = 200 # Pixels por segundo
PLAYER_WIDTH = TILE_SIZE * 0.8 # Torna o jogador ligeiramente menor que o tile
PLAYER_HEIGHT = 32
PLAYER_HEALTH = 100
PLAYER_INVINCIBILITY_DURATION = 1000 # Milissegundos
PLAYER_RENDER_LAYER = 3 # Camada de renderização para o sprite do jogador
PLAYER_SPRITE_WIDTH = 64 # Largura padrão para os quadros do spritesheet do jogador
PLAYER_SPRITE_HEIGHT = 64 # Altura padrão para os quadros do spritesheet do jogador
PLAYER_IDLE_FRAMES = 4  # Número de quadros na faixa de animação de ocioso
PLAYER_RUN_FRAMES = 8   # Número de quadros na faixa de animação de corrida

# Configurações gerais dos inimigos
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_DETECT_RADIUS = 250
ENEMY_ATTACK_RADIUS = 50
ENEMY_PATROL_RADIUS = 100
ENEMY_ATTACK_COOLDOWN = 1500 # Milissegundos
ENEMY_SEARCH_DURATION = 5000 # Milissegundos
ENEMY_INVINCIBILITY_DURATION = 500 # Milissegundos

# Configurações específicas do inimigo Saqueador
ENEMY_RAIDER_COLOR = RED
ENEMY_RAIDER_HEALTH = 75
ENEMY_RAIDER_DAMAGE = 10
ENEMY_RAIDER_SPEED = 2 # Pixels por quadro

# Configurações específicas do inimigo Cão Selvagem
ENEMY_DOG_COLOR = YELLOW
ENEMY_DOG_HEALTH = 55
ENEMY_DOG_DAMAGE = 5
ENEMY_DOG_SPEED = 3 # Pixels por quadro

# Configurações dos itens
ITEM_COLOR = GREEN
ITEM_WIDTH = 16
ITEM_HEIGHT = 16
ITEM_COLLECT_RADIUS = TILE_SIZE * 0.6 # Distância para coletar automaticamente (pouco mais da metade de um tile)

# Configurações da arma corpo a corpo
MELEE_WEAPON_RANGE = 50
MELEE_WEAPON_DAMAGE = 20
MELEE_WEAPON_COOLDOWN = 500 # Milissegundos
MELEE_WEAPON_ANIMATION_DURATION = 200 # Milissegundos
MELEE_WEAPON_ARC = 90 # Graus
MELEE_WEAPON_COLOR = YELLOW
MELEE_WEAPON_WIDTH = 40
MELEE_WEAPON_HEIGHT = 5

# Configurações da Pistola (Beretta M9)
PISTOL_COLOR = LIGHTGREY # Cor visual (se necessário)
PISTOL_FIRE_RATE = 120 # Milissegundos entre disparos (aprox 500 RPM)
PISTOL_MAGAZINE_SIZE = 15
PISTOL_RELOAD_TIME = 1500 # Milissegundos
PISTOL_RECOIL_AMOUNT = 5 # Recuo em pixels (efeito visual)
PISTOL_MUZZLE_FLASH_DURATION = 50 # Milissegundos
PISTOL_MUZZLE_FLASH_COLOR = YELLOW
PISTOL_MUZZLE_FLASH_SIZE = 10

# Configurações das Balas (Munição da Pistola)
BULLET_COLOR = WHITE
BULLET_WIDTH = 6
BULLET_HEIGHT = 3
BULLET_SPEED = 800 # Pixels por segundo
BULLET_DAMAGE = 18
BULLET_LIFETIME = 1000 # Milissegundos
BULLET_INITIAL_MAGS = 3 # Quantidade inicial de pentes
BULLET_RENDER_LAYER = 2
BULLET_INITIAL_AMMO = PISTOL_MAGAZINE_SIZE * BULLET_INITIAL_MAGS

# Configurações da barra de vida dos inimigos
ENEMY_HEALTH_BAR_WIDTH = 40
ENEMY_HEALTH_BAR_HEIGHT = 5
ENEMY_HEALTH_BAR_OFFSET = 5 # Deslocamento vertical acima do inimigo
ENEMY_HEALTH_BAR_COLOR_MAX = GREEN
ENEMY_HEALTH_BAR_COLOR_MIN = RED
ENEMY_HEALTH_BAR_BACKGROUND_COLOR = DARKGREY
ENEMY_HEALTH_BAR_BORDER_COLOR = WHITE

# Configurações das partículas de sangue
BLOOD_PARTICLE_COUNT = 5
BLOOD_PARTICLE_SIZE = 2
BLOOD_PARTICLE_SPEED = 2 # Pixels por quadro
BLOOD_PARTICLE_LIFETIME = 1000 # Milissegundos
BLOOD_PARTICLE_COLOR = RED

# Configurações da barra de vida do jogador
HEALTH_BAR_WIDTH = 150
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_X = 10
HEALTH_BAR_Y = 10
HEALTH_BAR_COLOR_MAX = GREEN
HEALTH_BAR_COLOR_MIN = RED
HEALTH_BAR_BACKGROUND_COLOR = DARKGREY
HEALTH_BAR_BORDER_COLOR = WHITE

# Configurações da radiação (Placeholder - Precisa de integração com RadioactiveZone)
RADIATION_MAX = 100
RADIATION_INCREASE_RATE = 0.5 # Por segundo em zona radioativa (precisa de implementação)
RADIATION_DAMAGE_THRESHOLD = 75 # Nível de radiação onde o jogador começa a sofrer dano
RADIATION_DAMAGE_RATE = 2 # Pontos de vida perdidos por segundo acima do limiar (precisa de implementação)

# Configurações da barra de radiação
RADIATION_BAR_WIDTH = 150
RADIATION_BAR_HEIGHT = 20
RADIATION_BAR_X = 10
RADIATION_BAR_Y = 40 # Posição abaixo da barra de vida
RADIATION_BAR_COLOR_MIN = (0, 255, 0) # Verde em baixa radiação
RADIATION_BAR_COLOR_MAX = (0, 255, 255) # Ciano/Amarelo em alta radiação (ajustar conforme necessário)
RADIATION_BAR_BACKGROUND_COLOR = DARKGREY
RADIATION_BAR_BORDER_COLOR = WHITE

# Configurações da Câmera
CAMERA_LERP_FACTOR = 0.08  # Quão rápido a câmera segue o jogador (menor = mais suave)

# Configurações do mapa (Usado por LevelGenerator)
MAP_WIDTH = 4800   # Largura total do mapa em pixels (ex: 150 tiles de largura se TILE_SIZE=32)
MAP_HEIGHT = 3600  # Altura total do mapa em pixels (ex: 112.5 tiles de altura se TILE_SIZE=32)

# Configurações de renderização avançada (Usado pela renderização de Tile e Câmera)
ENABLE_SHADOWS = True
SHADOW_INTENSITY = 0.6 # Placeholder, implementação real na renderização de Tile
ENABLE_LIGHTING = True
DAYLIGHT_COLOR = (255, 255, 220) # Tom quente para sobreposição de iluminação
LIGHTING_OVERLAY_ALPHA = 35 # Intensidade da sobreposição de luz (0-255)

# Paleta de cores para terrenos (Usado pela renderização de Tile)
GRASS_COLOR = (34, 139, 34) # ForestGreen
GRASS_DARK = (26, 120, 26)
GRASS_LIGHT = (42, 155, 42)
DIRT_COLOR = (101, 67, 33) # Sienna Escuro / Marrom
DIRT_DARK = (85, 55, 25)
DIRT_LIGHT = (120, 80, 40)
WATER_COLOR = (65, 105, 225) # RoyalBlue
WATER_DARK = (55, 90, 205)
WATER_HIGHLIGHT = (85, 125, 245)
CONCRETE_COLOR = (169, 169, 169) # DarkGray
CONCRETE_DARK = (140, 140, 140)
CONCRETE_LIGHT = (190, 190, 190)
BUILDING_COLOR = (100, 100, 100) # Cinza
BUILDING_DARK = (80, 80, 80)
BUILDING_LIGHT = (120, 120, 120)
METAL_COLOR = (160, 160, 180) # Azul Aço Claro
METAL_DARK = (130, 130, 150)
METAL_LIGHT = (190, 190, 210) # Versão mais clara
METAL_RUST = (140, 80, 60) # Marrom enferrujado
TREE_TRUNK = (101, 67, 33) # Mesmo que DIRT_COLOR
TREE_TRUNK_DARK = (85, 55, 25) # Derivado de DIRT_DARK
TREE_TRUNK_LIGHT = (120, 80, 40) # Derivado de DIRT_LIGHT
TREE_LEAVES_DARK = (0, 100, 0) # Verde Escuro
TREE_LEAVES_LIGHT = (30, 130, 30)
RADIOACTIVE_BASE = (40, 80, 40) # Base verde escura para zonas radioativas
RADIOACTIVE_BASE_LIGHT = (60, 100, 60) # Versão mais clara da base radioativa
RADIOACTIVE_GLOW = (100, 255, 100) # Brilho verde intenso
RADIOACTIVE_SYMBOL = (60, 180, 60) # Cor para o símbolo em si
OIL_STAIN_COLOR = (30, 30, 20, 150) # Mancha escura semitransparente

# Configurações de detalhe visual (Usado pela renderização de Tile)
DETAIL_LEVEL = 3   # 1=baixo, 2=médio, 3=alto
TEXTURE_DENSITY_DEFAULT = 30 # Densidade padrão para draw_textured_rect
TEXTURE_POINT_SIZE_MIN = 1
TEXTURE_POINT_SIZE_MAX = 3
TEXTURE_DARK_COLOR_THRESHOLD = 0.6 # Limiar de probabilidade para pontos de cor escura
TEXTURE_LIGHT_COLOR_THRESHOLD = 0.9 # Limiar de probabilidade para pontos de cor clara (restante é cor base)

# Tipos de terreno industrial (Usado por LevelGenerator)
INDUSTRIAL_STRUCTURES = [
    'tank', 'pipe', 'machine', 'crane', 'chimney',
    'conveyor', 'generator', 'cooling_tower', 'barrier', 'wall', 'building' # Adicionado mais tipos usados
    # 'reactor' não foi implementado na classe Tile, removido por enquanto
]

# Configurações dos módulos de filtro
FILTER_MODULE_COUNT = 3  # Número de módulos de filtro a serem colocados no mapa

# Nomes de Animação (Jogador)
ANIM_PLAYER_IDLE = 'ocioso'
ANIM_PLAYER_RUN = 'correr'
ANIM_PLAYER_WALK = 'andar'
ANIM_PLAYER_HURT = 'ferido'
ANIM_PLAYER_SHOOT = 'atirar'
ANIM_PLAYER_ATTACK = 'atacar'

# Nomes de Animação (Inimigos - Genérico)
ANIM_ENEMY_IDLE = 'ocioso'
ANIM_ENEMY_WALK = 'andar'
ANIM_ENEMY_HURT = 'ferido'
ANIM_ENEMY_SLASH = 'cortar' # Exemplo para Saqueador
# Adicione outros nomes de animação específicos de inimigos se necessário

# Chaves de Dicionário (Opcional, mas pode ajudar na consistência)
SPRITESHEET_KEY_BASE = 'base'

# Caminhos de Assets
PLAYER_SPRITESHEET_PATH = 'assets/images/run.png' # Caminho atualizado
ENEMY_SPRITESHEET_PATH = 'assets/images/run.png'  # Caminho atualizado
# Adicione outros caminhos de assets aqui (fontes, sons, etc.) se necessário
# FONT_PATH_ARIAL = pygame.font.match_font('arial') # Já tratado

# Configurações das fontes
# FONT_NAME = pygame.font.match_font('arial') # Movido para Game.__init__
HUD_FONT_SIZE = 25
INTRO_TITLE_FONT_SIZE = 38 # Adicionado constante
INTRO_FONT_SIZE = 28 # Adicionado constante
PROMPT_FONT_SIZE = 16 # Adicionado constante
GAME_OVER_FONT_SIZE = 50
HUD_COLOR = WHITE
