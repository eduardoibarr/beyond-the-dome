import pygame
import sys
import random
from .settings import (
    WIDTH, HEIGHT, TITLE, FPS,
    HUD_FONT_SIZE, INTRO_TITLE_FONT_SIZE, INTRO_FONT_SIZE,
    PROMPT_FONT_SIZE, GAME_OVER_FONT_SIZE,
    BLACK, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT
)
from .audio_manager import AudioManager
from .spawner import spawn_initial_enemies
from .noise_generator import NoiseGenerator
from .asset_manager import AssetManager
from graphics.particles import RadiationSystem

from level.generator import LevelGenerator
from graphics.camera import Camera
from graphics.ui.hud import draw_hud

class Game:
    """Classe principal do jogo, responsável por gerenciar o loop principal e todos os subsistemas.
    Controla a inicialização, atualização e renderização do jogo, além de gerenciar recursos e estados.
    """
    def __init__(self):
        """Inicializa o jogo e todos os seus subsistemas."""
        # Inicialização do Pygame e configurações básicas
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Estados do jogo
        self.running = True      # Indica se o jogo deve continuar rodando
        self.playing = False     # Indica se uma partida está em andamento
        self.dt = 0             # Delta time (tempo entre frames)
        self.cause_of_death = None  # Armazena a causa da morte do jogador

        # Dimensões do mapa
        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT

        # Carrega fontes do jogo
        self.load_fonts()

        # Inicializa gerenciadores de recursos
        self.asset_manager = AssetManager()  # Gerenciador de assets (sprites, imagens, etc)
        self.audio_manager = AudioManager(self.asset_manager)  # Gerenciador de áudio

        # Inicializa sistema de partículas para efeitos visuais
        self.particle_systems = type('ParticleSystems', (), {})()
        self.particle_systems.radiation = RadiationSystem()  # Sistema de partículas de radiação

        # Grupos de sprites e referências
        self.all_sprites = None      # Grupo contendo todos os sprites do jogo
        self.world_tiles = None      # Grupo de tiles do mundo
        self.enemies = None          # Grupo de inimigos
        self.bullets = None          # Grupo de projéteis
        self.obstacles = None        # Grupo de obstáculos
        self.radioactive_zones = None # Grupo de zonas radioativas
        self.items = None            # Grupo de itens coletáveis
        self.camera = None           # Sistema de câmera
        self.player = None           # Referência ao jogador
        self.level_generator = None  # Gerador de níveis

        # Inicializa gerador de ruído para geração procedural
        self.noise_generator = NoiseGenerator(
            seed=random.randint(0, 1000),  # Semente aleatória para geração
            scale=100.0,                   # Escala do ruído
            octaves=6,                     # Número de camadas de ruído
            persistence=0.5,               # Persistência do ruído
            lacunarity=2.0                 # Lacunaridade do ruído
        )

    def load_fonts(self):
        """Carrega e configura as fontes utilizadas no jogo.
        Tenta carregar a fonte Arial, mas usa a fonte padrão do sistema como fallback.
        """
        try:
            font_path = pygame.font.match_font('arial') or pygame.font.get_default_font()
            self.font = pygame.font.Font(font_path, HUD_FONT_SIZE)              # Fonte para HUD
            self.intro_title_font = pygame.font.Font(font_path, INTRO_TITLE_FONT_SIZE)  # Fonte para títulos
            self.intro_font = pygame.font.Font(font_path, INTRO_FONT_SIZE)      # Fonte para texto introdutório
            self.prompt_font = pygame.font.Font(font_path, PROMPT_FONT_SIZE)    # Fonte para prompts
            self.game_over_font = pygame.font.Font(font_path, GAME_OVER_FONT_SIZE)  # Fonte para tela de game over
        except Exception:
            # Fallback para fonte padrão em caso de erro
            self.font = pygame.font.Font(None, HUD_FONT_SIZE)
            self.intro_title_font = pygame.font.Font(None, INTRO_TITLE_FONT_SIZE)
            self.intro_font = pygame.font.Font(None, INTRO_FONT_SIZE)
            self.prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)

    def new(self):
        """Inicia uma nova partida, reinicializando todos os grupos e criando um novo nível."""
        # Inicializa grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.world_tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.radioactive_zones = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Gera novo nível e obtém ponto de spawn
        self.level_generator = LevelGenerator(self)
        spawn_point = self.level_generator.create_level()
        
        # Inicializa câmera se ainda não existir
        if not self.camera:
            self.camera = Camera(self.map_width, self.map_height)

        # Cria jogador no ponto de spawn
        spawn_x, spawn_y = spawn_point
        PlayerClass = self.asset_manager.get_sprite_class('player')
        if not PlayerClass:
            print("Classe Player não encontrada!")
            self.playing = False
            return
        self.player = PlayerClass(self, spawn_x * TILE_SIZE, spawn_y * TILE_SIZE)

        # Spawna inimigos iniciais
        spawn_initial_enemies(self, self.asset_manager)

        # Reseta estado da partida
        self.cause_of_death = None
        self.playing = True
        self.run()

    def run(self):
        """Loop principal do jogo, responsável por atualizar e renderizar o jogo a cada frame."""
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # Calcula delta time
            self.events()                            # Processa eventos
            if not self.playing:
                break
            self.update()                            # Atualiza estado do jogo
            self.draw()                              # Renderiza frame

    def events(self):
        """Processa eventos do Pygame, como fechar a janela."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        """Atualiza o estado do jogo, incluindo física, colisões e lógica."""
        if not self.camera or not self.player:
            self.playing = False
            return

        # Atualiza câmera e todos os sprites
        self.camera.update(self.player)
        self.all_sprites.update(self.dt)

        # Verifica colisões entre jogador e inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            if hasattr(enemy, 'damage'):
                self.player.take_damage(enemy.damage)

        # Verifica zonas radioativas
        self.check_radioactive_zones()

        # Emite partículas de radiação se o jogador estiver em zona radioativa
        if getattr(self.player, 'is_in_radioactive_zone', False):
            cx, cy = self.player.rect.center
            self.particle_systems.radiation.emit(cx, cy, count=5)

        # Atualiza sistema de partículas
        self.particle_systems.radiation.update(self.dt)

        # Verifica morte do jogador
        if self.player.health <= 0:
            self.playing = False
            if not self.cause_of_death:
                self.cause_of_death = "Eliminado"

    def check_radioactive_zones(self):
        """Verifica se o jogador está em uma zona radioativa."""
        if not self.player or not self.radioactive_zones:
            return
        in_zone = pygame.sprite.spritecollide(self.player, self.radioactive_zones, False)
        self.player.is_in_radioactive_zone = bool(in_zone)

    def draw(self):
        """Renderiza todos os elementos do jogo na tela."""
        if not self.camera:
            self.screen.fill(BLACK)
            pygame.display.flip()
            return

        # Limpa tela
        self.screen.fill(BLACK)

        # Renderiza tiles do mundo
        for tile in self.world_tiles:
            if self.camera.is_rect_visible(tile.rect):
                self.screen.blit(tile.image, self.camera.apply(tile))
        
        # Renderiza itens
        for item in self.items:
            if self.camera.is_rect_visible(item.rect):
                self.screen.blit(item.image, self.camera.apply(item))

        # Renderiza todos os sprites
        for sprite in self.all_sprites:
            if self.camera.is_rect_visible(sprite.rect) and hasattr(sprite, 'image'):
                self.screen.blit(sprite.image, self.camera.apply(sprite))

        # Renderiza jogador e sua arma
        if self.player and hasattr(self.player, 'image'):
            self.screen.blit(self.player.image, self.camera.apply(self.player))
            if hasattr(self.player, 'draw_weapon'):
                self.player.draw_weapon(self.screen, self.camera)

        # Renderiza inimigos
        for enemy in self.enemies:
            if self.camera.is_rect_visible(enemy.rect):
                enemy.draw(self.screen, self.camera)

        # Renderiza partículas de radiação
        self.particle_systems.radiation.draw(self.screen, self.camera)

        # Renderiza HUD
        draw_hud(self)
        pygame.display.flip()

    def quit(self):
        """Encerra o jogo e libera recursos."""
        pygame.quit()
        sys.exit()

    def play_audio(self, key, volume=1.0, loop=False):
        """Reproduz um efeito sonoro ou música.
        Args:
            key (str): Chave do áudio a ser reproduzido.
            volume (float): Volume do áudio (0.0 a 1.0).
            loop (bool): Se True, o áudio será reproduzido em loop.
        Returns:
            pygame.mixer.Sound: O objeto de som reproduzido ou None se falhar.
        """
        if self.audio_manager:
            return self.audio_manager.play(key, volume, loop)
        return None

    def stop_audio(self, sound=None, fadeout_ms=500):
        """Para a reprodução de um som específico ou todos os sons.
        Args:
            sound (pygame.mixer.Sound, optional): Som a ser parado. Se None, para todos.
            fadeout_ms (int): Tempo de fade out em milissegundos.
        """
        if self.audio_manager:
            self.audio_manager.stop(sound, fadeout_ms)

    def stop_music(self, fadeout_ms=500):
        """Para a música atual com fade out.
        Args:
            fadeout_ms (int): Tempo de fade out em milissegundos.
        """
        if self.audio_manager:
            self.audio_manager.stop_music(fadeout_ms)
