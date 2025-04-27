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
CYAN = (0, 255, 255) # Added for filter module/radiation
LIGHTBLUE = (173, 216, 230) # Added for filter module
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREY = (128, 128, 128) # Added grey for intro prompt

# Configurações do tamanho dos tiles (moved up)
TILE_SIZE = 32

# Configurações do jogador
PLAYER_COLOR = (0, 200, 0) # Green
PLAYER_SPEED = 200 # Pixels per second
PLAYER_WIDTH = TILE_SIZE * 0.8 # Make player slightly smaller than tile
PLAYER_HEIGHT = 32
PLAYER_HEALTH = 100
PLAYER_INVINCIBILITY_DURATION = 1000 # Milliseconds
PLAYER_RENDER_LAYER = 3 # Rendering layer for the player sprite
PLAYER_SPRITE_WIDTH = 64 # Default width for player spritesheet frames
PLAYER_SPRITE_HEIGHT = 64 # Default height for player spritesheet frames
PLAYER_IDLE_FRAMES = 4  # Number of frames in the idle animation strip
PLAYER_RUN_FRAMES = 8   # Number of frames in the run animation strip

# Configurações gerais dos inimigos
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_DETECT_RADIUS = 250
ENEMY_ATTACK_RADIUS = 50
ENEMY_PATROL_RADIUS = 100
ENEMY_ATTACK_COOLDOWN = 1500 # Milliseconds
ENEMY_SEARCH_DURATION = 5000 # Milliseconds
ENEMY_INVINCIBILITY_DURATION = 500 # Milliseconds

# Configurações específicas do inimigo Saqueador
ENEMY_RAIDER_COLOR = RED
ENEMY_RAIDER_HEALTH = 75
ENEMY_RAIDER_DAMAGE = 10
ENEMY_RAIDER_SPEED = 2 # Pixels per frame

# Configurações específicas do inimigo Cão Selvagem
ENEMY_DOG_COLOR = YELLOW
ENEMY_DOG_HEALTH = 55
ENEMY_DOG_DAMAGE = 5
ENEMY_DOG_SPEED = 3 # Pixels per frame

# Configurações dos itens
ITEM_COLOR = GREEN
ITEM_WIDTH = 16
ITEM_HEIGHT = 16
ITEM_COLLECT_RADIUS = TILE_SIZE * 0.6 # Distância para coletar automaticamente (pouco mais da metade de um tile)

# Configurações da arma corpo a corpo
MELEE_WEAPON_RANGE = 50
MELEE_WEAPON_DAMAGE = 20
MELEE_WEAPON_COOLDOWN = 500 # Milliseconds
MELEE_WEAPON_ANIMATION_DURATION = 200 # Milliseconds
MELEE_WEAPON_ARC = 90 # Degrees
MELEE_WEAPON_COLOR = YELLOW
MELEE_WEAPON_WIDTH = 40
MELEE_WEAPON_HEIGHT = 5

# Configurações da Pistola (Beretta M9)
PISTOL_COLOR = LIGHTGREY # Cor visual (se necessário)
PISTOL_FIRE_RATE = 120 # Milliseconds between shots (500 RPM approx)
PISTOL_MAGAZINE_SIZE = 15
PISTOL_RELOAD_TIME = 1500 # Milliseconds
PISTOL_RECOIL_AMOUNT = 5 # Pixels kickback (visual effect)
PISTOL_MUZZLE_FLASH_DURATION = 50 # Milliseconds
PISTOL_MUZZLE_FLASH_COLOR = YELLOW
PISTOL_MUZZLE_FLASH_SIZE = 10

# Configurações das Balas (Munição da Pistola)
BULLET_COLOR = WHITE
BULLET_WIDTH = 6
BULLET_HEIGHT = 3
BULLET_SPEED = 800 # Pixels per second
BULLET_DAMAGE = 18
BULLET_LIFETIME = 1000 # Milliseconds
BULLET_INITIAL_MAGS = 3 # Quantidade inicial de pentes
BULLET_INITIAL_AMMO = PISTOL_MAGAZINE_SIZE * BULLET_INITIAL_MAGS

# Configurações da barra de vida dos inimigos
ENEMY_HEALTH_BAR_WIDTH = 40
ENEMY_HEALTH_BAR_HEIGHT = 5
ENEMY_HEALTH_BAR_OFFSET = 5 # Vertical offset above enemy
ENEMY_HEALTH_BAR_COLOR_MAX = GREEN
ENEMY_HEALTH_BAR_COLOR_MIN = RED
ENEMY_HEALTH_BAR_BACKGROUND_COLOR = DARKGREY
ENEMY_HEALTH_BAR_BORDER_COLOR = WHITE

# Configurações das partículas de sangue
BLOOD_PARTICLE_COUNT = 5
BLOOD_PARTICLE_SIZE = 2
BLOOD_PARTICLE_SPEED = 2 # Pixels per frame
BLOOD_PARTICLE_LIFETIME = 1000 # Milliseconds
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

# Configurações da radiação (Placeholder - Needs integration with RadioactiveZone)
RADIATION_MAX = 100
RADIATION_INCREASE_RATE = 0.5 # Per second in radioactive zone (needs implementation)
RADIATION_DAMAGE_THRESHOLD = 75 # Radiation level where player starts taking damage
RADIATION_DAMAGE_RATE = 2 # Health points lost per second when above threshold (needs implementation)

# Configurações da barra de radiação
RADIATION_BAR_WIDTH = 150
RADIATION_BAR_HEIGHT = 20
RADIATION_BAR_X = 10
RADIATION_BAR_Y = 40 # Position below health bar
RADIATION_BAR_COLOR_MIN = (0, 255, 0) # Green at low radiation
RADIATION_BAR_COLOR_MAX = (0, 255, 255) # Cyan/Yellow at high radiation (adjust as needed)
RADIATION_BAR_BACKGROUND_COLOR = DARKGREY
RADIATION_BAR_BORDER_COLOR = WHITE

# Configurações da Câmera
CAMERA_LERP_FACTOR = 0.08  # Quão rápido a câmera segue o jogador (menor = mais suave)

# Configurações do mapa (Used by LevelGenerator)
MAP_WIDTH = 4800   # Total map width in pixels (e.g., 150 tiles wide if TILE_SIZE=32)
MAP_HEIGHT = 3600  # Total map height in pixels (e.g., 112.5 tiles high if TILE_SIZE=32)

# Configurações de renderização avançada (Used by Tile rendering and Camera)
ENABLE_SHADOWS = True
SHADOW_INTENSITY = 0.6 # Placeholder, actual implementation in Tile rendering
ENABLE_LIGHTING = True
DAYLIGHT_COLOR = (255, 255, 220) # Warm tint for lighting overlay
LIGHTING_OVERLAY_ALPHA = 35 # Intensity of the light overlay (0-255)

# Paleta de cores para terrenos (Used by Tile rendering)
GRASS_COLOR = (34, 139, 34) # ForestGreen
GRASS_DARK = (26, 120, 26)
GRASS_LIGHT = (42, 155, 42)
DIRT_COLOR = (101, 67, 33) # Dark Sienna / Brown
DIRT_DARK = (85, 55, 25)
DIRT_LIGHT = (120, 80, 40)
WATER_COLOR = (65, 105, 225) # RoyalBlue
WATER_DARK = (55, 90, 205)
WATER_HIGHLIGHT = (85, 125, 245)
CONCRETE_COLOR = (169, 169, 169) # DarkGray
CONCRETE_DARK = (140, 140, 140)
CONCRETE_LIGHT = (190, 190, 190)
BUILDING_COLOR = (100, 100, 100) # Gray
BUILDING_DARK = (80, 80, 80)
BUILDING_LIGHT = (120, 120, 120)
METAL_COLOR = (160, 160, 180) # LightSteelBlue-ish
METAL_DARK = (130, 130, 150)
METAL_LIGHT = (190, 190, 210) # Lighter version
METAL_RUST = (140, 80, 60) # Rusty brown
TREE_TRUNK = (101, 67, 33) # Same as DIRT_COLOR
TREE_TRUNK_DARK = (85, 55, 25) # Derived from DIRT_DARK
TREE_TRUNK_LIGHT = (120, 80, 40) # Derived from DIRT_LIGHT
TREE_LEAVES_DARK = (0, 100, 0) # DarkGreen
TREE_LEAVES_LIGHT = (30, 130, 30)
RADIOACTIVE_BASE = (40, 80, 40) # Dark green base for radioactive zones
RADIOACTIVE_BASE_LIGHT = (60, 100, 60) # Lighter version of radioactive base
RADIOACTIVE_GLOW = (100, 255, 100) # Bright green glow
RADIOACTIVE_SYMBOL = (60, 180, 60) # Color for the symbol itself
OIL_STAIN_COLOR = (30, 30, 20, 150) # Semi-transparent dark stain

# Configurações de detalhe visual (Used by Tile rendering)
DETAIL_LEVEL = 3   # 1=low, 2=medium, 3=high
TEXTURE_DENSITY_DEFAULT = 30 # Default density for draw_textured_rect
TEXTURE_POINT_SIZE_MIN = 1
TEXTURE_POINT_SIZE_MAX = 3
TEXTURE_DARK_COLOR_THRESHOLD = 0.6 # Probability threshold for dark color points
TEXTURE_LIGHT_COLOR_THRESHOLD = 0.9 # Probability threshold for light color points (remainder is base color)

# Tipos de terreno industrial (Used by LevelGenerator)
INDUSTRIAL_STRUCTURES = [
    'tank', 'pipe', 'machine', 'crane', 'chimney',
    'conveyor', 'generator', 'cooling_tower', 'barrier', 'wall', 'building' # Added more types used
    # 'reactor' was not implemented in the Tile class, removed for now
]

# Configurações dos módulos de filtro
FILTER_MODULE_COUNT = 3  # Número de módulos de filtro a serem colocados no mapa

# Nomes de Animação (Player)
ANIM_PLAYER_IDLE = 'idle'
ANIM_PLAYER_RUN = 'run'
ANIM_PLAYER_WALK = 'walk'
ANIM_PLAYER_HURT = 'hurt'
ANIM_PLAYER_SHOOT = 'shoot'
ANIM_PLAYER_ATTACK = 'attack'

# Nomes de Animação (Inimigos - Genérico)
ANIM_ENEMY_IDLE = 'idle'
ANIM_ENEMY_WALK = 'walk'
ANIM_ENEMY_HURT = 'hurt'
ANIM_ENEMY_SLASH = 'slash' # Example for Raider
# Adicione outros nomes de animação específicos de inimigos se necessário

# Chaves de Dicionário (Opcional, mas pode ajudar na consistência)
SPRITESHEET_KEY_BASE = 'base'

# Caminhos de Assets
PLAYER_SPRITESHEET_PATH = 'assets/sprites/run.png' # Updated path
ENEMY_SPRITESHEET_PATH = 'assets/sprites/run.png'  # Updated path
# Adicione outros paths de assets aqui (fontes, sons, etc.) se necessário
# FONT_PATH_ARIAL = pygame.font.match_font('arial') # Already handled

# Configurações das fontes
# FONT_NAME = pygame.font.match_font('arial') # Moved to Game.__init__
HUD_FONT_SIZE = 25
INTRO_TITLE_FONT_SIZE = 38 # Added constant
INTRO_FONT_SIZE = 28 # Added constant
PROMPT_FONT_SIZE = 16 # Added constant
GAME_OVER_FONT_SIZE = 50
HUD_COLOR = WHITE
