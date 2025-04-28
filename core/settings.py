# =============================================================================
# CONFIGURAÇÕES BÁSICAS DO JOGO
# =============================================================================
# Configurações da janela e loop principal
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Beyond the Dome"

# Configurações do cursor
CURSOR_VISIBLE = False  # Esconde o cursor padrão do sistema

# =============================================================================
# PALETA DE CORES
# =============================================================================
# Cores básicas
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
LIGHTBLUE = (173, 216, 230)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREY = (128, 128, 128)

# =============================================================================
# CONFIGURAÇÕES DO MAPA E TILES
# =============================================================================
# Dimensões do mapa
MAP_WIDTH = 6400   # Largura total do mapa em pixels (aumentado de 4800)
MAP_HEIGHT = 4800  # Altura total do mapa em pixels (aumentado de 3600)

# Configurações dos tiles
TILE_SIZE = 32  # Tamanho base dos tiles em pixels

# =============================================================================
# CONFIGURAÇÕES DO JOGADOR
# =============================================================================
# Atributos básicos
PLAYER_COLOR = (0, 200, 0)
PLAYER_SPEED = 200  # Pixels por segundo
PLAYER_WIDTH = TILE_SIZE * 0.8
PLAYER_HEIGHT = 32
PLAYER_HEALTH = 100
PLAYER_INVINCIBILITY_DURATION = 1000  # Milissegundos
PLAYER_RENDER_LAYER = 3

# Configurações de animação
PLAYER_SPRITE_WIDTH = 64
PLAYER_SPRITE_HEIGHT = 64
PLAYER_IDLE_FRAMES = 4
PLAYER_RUN_FRAMES = 8
PLAYER_FRICTION = 0.15

# Configurações de combate
PLAYER_MELEE_COOLDOWN = 500  # Milissegundos entre ataques corpo a corpo

# =============================================================================
# CONFIGURAÇÕES DOS INIMIGOS
# =============================================================================
# Configurações gerais
ENEMY_WIDTH = 32
ENEMY_HEIGHT = 32
ENEMY_DETECT_RADIUS = 250
ENEMY_ATTACK_RADIUS = 50
ENEMY_PATROL_RADIUS = 100
ENEMY_ATTACK_COOLDOWN = 1500
ENEMY_SEARCH_DURATION = 5000
ENEMY_INVINCIBILITY_DURATION = 500

# Saqueador (Raider)
ENEMY_RAIDER_COLOR = RED
ENEMY_RAIDER_HEALTH = 75
ENEMY_RAIDER_DAMAGE = 10
ENEMY_RAIDER_SPEED = 2

# Cão Selvagem (Wild Dog)
ENEMY_DOG_COLOR = YELLOW
ENEMY_DOG_HEALTH = 55
ENEMY_DOG_DAMAGE = 5
ENEMY_DOG_SPEED = 3

# =============================================================================
# CONFIGURAÇÕES DE ARMAS E COMBATE
# =============================================================================
# Arma corpo a corpo
MELEE_WEAPON_RANGE = 50
MELEE_WEAPON_DAMAGE = 20
MELEE_WEAPON_COOLDOWN = 500
MELEE_WEAPON_ANIMATION_DURATION = 200
MELEE_WEAPON_ARC = 90
MELEE_WEAPON_COLOR = YELLOW
MELEE_WEAPON_WIDTH = 40
MELEE_WEAPON_HEIGHT = 5

# Pistola (Beretta M9)
PISTOL_COLOR = LIGHTGREY
PISTOL_FIRE_RATE = 120  # Milissegundos entre disparos
PISTOL_MAGAZINE_SIZE = 15
PISTOL_RELOAD_TIME = 1500
PISTOL_RECOIL_AMOUNT = 5
PISTOL_MUZZLE_FLASH_DURATION = 50
PISTOL_MUZZLE_FLASH_COLOR = YELLOW
PISTOL_MUZZLE_FLASH_SIZE = 10

# Munição
BULLET_COLOR = WHITE
BULLET_WIDTH = 6
BULLET_HEIGHT = 3
BULLET_SPEED = 1200
BULLET_DAMAGE = 18
BULLET_LIFETIME = 1000
BULLET_INITIAL_MAGS = 3
BULLET_RENDER_LAYER = 2
FX_RENDER_LAYER = 4
BULLET_INITIAL_AMMO = PISTOL_MAGAZINE_SIZE * BULLET_INITIAL_MAGS
BULLET_FIRE_RATE = 200

# =============================================================================
# CONFIGURAÇÕES DE ITENS E COLETÁVEIS
# =============================================================================
ITEM_COLOR = GREEN
ITEM_WIDTH = 16
ITEM_HEIGHT = 16
ITEM_COLLECT_RADIUS = TILE_SIZE * 0.6

# =============================================================================
# CONFIGURAÇÕES DE INTERFACE (HUD)
# =============================================================================
# Barras de status
HEALTH_BAR_WIDTH = 150
HEALTH_BAR_HEIGHT = 20
HEALTH_BAR_X = 10
HEALTH_BAR_Y = 10
HEALTH_BAR_COLOR_MAX = GREEN
HEALTH_BAR_COLOR_MIN = RED
HEALTH_BAR_BACKGROUND_COLOR = DARKGREY
HEALTH_BAR_BORDER_COLOR = WHITE

# Barra de radiação
RADIATION_BAR_WIDTH = 150
RADIATION_BAR_HEIGHT = 20
RADIATION_BAR_X = 10
RADIATION_BAR_Y = 40
RADIATION_BAR_COLOR_MIN = (0, 255, 0)
RADIATION_BAR_COLOR_MAX = (0, 255, 255)
RADIATION_BAR_BACKGROUND_COLOR = DARKGREY
RADIATION_BAR_BORDER_COLOR = WHITE

# Barra de vida dos inimigos
ENEMY_HEALTH_BAR_WIDTH = 40
ENEMY_HEALTH_BAR_HEIGHT = 5
ENEMY_HEALTH_BAR_OFFSET = 5
ENEMY_HEALTH_BAR_COLOR_MAX = GREEN
ENEMY_HEALTH_BAR_COLOR_MIN = RED
ENEMY_HEALTH_BAR_BACKGROUND_COLOR = DARKGREY
ENEMY_HEALTH_BAR_BORDER_COLOR = WHITE

# =============================================================================
# CONFIGURAÇÕES DE PARTÍCULAS E EFEITOS
# =============================================================================
# Partículas de sangue
BLOOD_PARTICLE_COUNT = 5
BLOOD_PARTICLE_SIZE = 2
BLOOD_PARTICLE_SPEED = 2
BLOOD_PARTICLE_LIFETIME = 1000
BLOOD_PARTICLE_COLOR = RED

# Partículas de radiação
RAD_PARTICLE_SPEED = 20
RAD_PARTICLE_LIFETIME = 1.5

# =============================================================================
# CONFIGURAÇÕES DE RADIAÇÃO
# =============================================================================
RADIATION_MAX = 100
RADIATION_INCREASE_RATE = 0.5
RADIATION_DAMAGE_THRESHOLD = 75
RADIATION_DAMAGE_RATE = 2

# =============================================================================
# CONFIGURAÇÕES DE RENDERIZAÇÃO AVANÇADA
# =============================================================================
# Iluminação e sombras
ENABLE_SHADOWS = True
SHADOW_INTENSITY = 0.6
ENABLE_LIGHTING = True
DAYLIGHT_COLOR = (255, 255, 220)
LIGHTING_OVERLAY_ALPHA = 35

# Detalhes visuais
DETAIL_LEVEL = 3
TEXTURE_DENSITY_DEFAULT = 30
TEXTURE_POINT_SIZE_MIN = 1
TEXTURE_POINT_SIZE_MAX = 3
TEXTURE_DARK_COLOR_THRESHOLD = 0.6
TEXTURE_LIGHT_COLOR_THRESHOLD = 0.9

# =============================================================================
# PALETA DE CORES PARA TERRENOS
# =============================================================================
# Grama
GRASS_COLOR = (34, 139, 34)
GRASS_DARK = (26, 120, 26)
GRASS_LIGHT = (42, 155, 42)

# Terra
DIRT_COLOR = (101, 67, 33)
DIRT_DARK = (85, 55, 25)
DIRT_LIGHT = (120, 80, 40)

# Água
WATER_COLOR = (65, 105, 225)
WATER_DARK = (55, 90, 205)
WATER_HIGHLIGHT = (85, 125, 245)

# Concreto
CONCRETE_COLOR = (169, 169, 169)
CONCRETE_DARK = (140, 140, 140)
CONCRETE_LIGHT = (190, 190, 190)

# Edifícios
BUILDING_COLOR = (100, 100, 100)
BUILDING_DARK = (80, 80, 80)
BUILDING_LIGHT = (120, 120, 120)

# Metal
METAL_COLOR = (160, 160, 180)
METAL_DARK = (130, 130, 150)
METAL_LIGHT = (190, 190, 210)
METAL_RUST = (140, 80, 60)

# Árvores
TREE_TRUNK = (101, 67, 33)
TREE_TRUNK_DARK = (85, 55, 25)
TREE_TRUNK_LIGHT = (120, 80, 40)
TREE_LEAVES_DARK = (0, 100, 0)
TREE_LEAVES_LIGHT = (30, 130, 30)

# Zonas radioativas
RADIOACTIVE_BASE = (40, 80, 40)
RADIOACTIVE_BASE_LIGHT = (60, 100, 60)
RADIOACTIVE_GLOW = (100, 255, 100)
RADIOACTIVE_SYMBOL = (60, 180, 60)
OIL_STAIN_COLOR = (30, 30, 20, 150)

# =============================================================================
# CONFIGURAÇÕES DE ANIMAÇÕES
# =============================================================================
# Nomes de animação do jogador
ANIM_PLAYER_IDLE = 'ocioso'
ANIM_PLAYER_RUN = 'correr'
ANIM_PLAYER_WALK = 'andar'
ANIM_PLAYER_HURT = 'ferido'
ANIM_PLAYER_SHOOT = 'atirar'
ANIM_PLAYER_ATTACK = 'atacar'

# Nomes de animação dos inimigos
ANIM_ENEMY_IDLE = 'ocioso'
ANIM_ENEMY_WALK = 'andar'
ANIM_ENEMY_HURT = 'ferido'
ANIM_ENEMY_SLASH = 'cortar'

# =============================================================================
# CONFIGURAÇÕES DE FONTES
# =============================================================================
HUD_FONT_SIZE = 25
INTRO_TITLE_FONT_SIZE = 38
INTRO_FONT_SIZE = 28
PROMPT_FONT_SIZE = 16
GAME_OVER_FONT_SIZE = 50
HUD_COLOR = WHITE

# =============================================================================
# CONFIGURAÇÕES DE CAMERA
# =============================================================================
CAMERA_LERP_FACTOR = 0.08  # Quão rápido a câmera segue o jogador

# =============================================================================
# CONFIGURAÇÕES DE ESTRUTURAS INDUSTRIAIS
# =============================================================================
INDUSTRIAL_STRUCTURES = [
    'tank', 'pipe', 'machine', 'crane', 'chimney',
    'conveyor', 'generator', 'cooling_tower', 'barrier', 'wall', 'building'
]

# =============================================================================
# CONFIGURAÇÕES DE MÓDULOS DE FILTRO
# =============================================================================
FILTER_MODULE_COUNT = 3

# =============================================================================
# CAMINHOS DE ASSETS
# =============================================================================
PLAYER_SPRITESHEET_PATH = 'assets/images/run.png'
ENEMY_SPRITESHEET_PATH = 'assets/images/run.png'

# --- Items Settings ---
ITEM_SIZE = 32 # Exemplo, ajuste se necessário
ITEM_COLLECT_RADIUS = 50 # Raio para coleta automática
FILTER_MODULE_COUNT = 3 # Quantos módulos de filtro gerar
REINFORCED_MASK_COUNT = 2 # Quantas máscaras reforçadas gerar
REINFORCED_MASK_DURATION = 30.0 # Duração do buff da máscara em segundos
HEALTH_PACK_HEAL_AMOUNT = 50 # Quantidade de cura do HealthPack

# --- Player Settings ---
# ... (other player settings like PLAYER_HEALTH, PLAYER_SPEED) ...
PLAYER_RADIATION_GAIN_RATE = 5.0 # Taxa de ganho de radiação por segundo em zona perigosa
PLAYER_RADIATION_RECOVERY_RATE = 1.0 # Taxa de recuperação fora de zonas perigosas
RADIATION_DAMAGE_THRESHOLD = 60.0 # Nível de radiação para começar a tomar dano
RADIATION_DAMAGE_MULTIPLIER = 0.5 # Multiplicador de dano por radiação por segundo
# Add any other missing constants here (e.g., CYAN color if not defined)
CYAN = (0, 255, 255) # Exemplo de definição de cor
