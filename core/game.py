import pygame
import sys
# Use importações relativas dentro do pacote 'core' para módulos irmãos
from .settings import (
    WIDTH, HEIGHT, TITLE, FPS,
    HUD_FONT_SIZE, INTRO_TITLE_FONT_SIZE, INTRO_FONT_SIZE, # Use constantes de tamanho
    PROMPT_FONT_SIZE, GAME_OVER_FONT_SIZE, # Use constantes de tamanho
    BLACK, TILE_SIZE # Removido FONT_NAME, PLAYER_HEALTH (adicionar se necessário)
)
from .audio_manager import AudioManager
from .spawner import spawn_initial_enemies

# Importações de outros pacotes
from graphics.sprites import Player # Assumindo que Player é necessário para dica de tipo/verificação
from level.generator import LevelGenerator # Importação corrigida
from graphics.camera import Camera # Importação corrigida
from graphics.ui.screens import display_intro, show_start_screen, show_go_screen
from graphics.ui.hud import draw_hud

class Game:
    def __init__(self):
        """Inicializa o Pygame, a tela, o relógio, as fontes e os gerenciadores."""
        pygame.init()
        # Inicializa o mixer de som *antes* de carregar os sons
        #pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.dt = 0
        self.cause_of_death = None

        # Carrega as fontes *depois* de pygame.init()
        self.load_fonts()

        # Inicializa os Gerenciadores
        #self.audio_manager = AudioManager()
        # Os grupos de sprites serão inicializados em new()
        self.all_sprites = None
        self.world_tiles = None
        self.enemies = None
        self.bullets = None
        self.obstacles = None
        self.radioactive_zones = None
        self.items = None
        self.camera = None
        self.player = None
        self.level_generator = None

    def load_fonts(self):
        """Carrega as fontes usadas no jogo."""
        try:
            # Tenta encontrar uma fonte adequada como Arial
            font_path = pygame.font.match_font('arial')
            if font_path is None:
                print("Fonte 'arial' não encontrada, usando fonte padrão.")
                font_path = pygame.font.get_default_font()

            self.font = pygame.font.Font(font_path, HUD_FONT_SIZE)
            self.intro_title_font = pygame.font.Font(font_path, INTRO_TITLE_FONT_SIZE)
            self.intro_font = pygame.font.Font(font_path, INTRO_FONT_SIZE)
            self.prompt_font = pygame.font.Font(font_path, PROMPT_FONT_SIZE)
            self.game_over_font = pygame.font.Font(font_path, GAME_OVER_FONT_SIZE)
            print(f"Fonte carregada: {font_path}")

        except Exception as e:
            print(f"Erro ao carregar fonte: {e}. Usando fontes padrão do Pygame.")
            # Usa fonte padrão do Pygame se ocorrer qualquer erro
            self.font = pygame.font.Font(None, HUD_FONT_SIZE)
            self.intro_title_font = pygame.font.Font(None, INTRO_TITLE_FONT_SIZE)
            self.intro_font = pygame.font.Font(None, INTRO_FONT_SIZE)
            self.prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)

    def new(self):
        """Inicia uma nova sessão de jogo: inicializa sprites, nível, jogador, inimigos."""
        # Inicializa grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.world_tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group() # Grupo para balas
        self.obstacles = pygame.sprite.Group()
        self.radioactive_zones = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Configura Nível e Câmera
        self.level_generator = LevelGenerator(self)
        spawn_point = self.level_generator.create_level()
        # A câmera deve ser criada pelo LevelGenerator ou aqui
        if not self.camera:
            self.camera = Camera(self.level_generator.map_width_pixels, self.level_generator.map_height_pixels)

        # Cria o Jogador
        spawn_tile_x, spawn_tile_y = spawn_point
        self.player = Player(self, spawn_tile_x * TILE_SIZE, spawn_tile_y * TILE_SIZE)

        # Gera Inimigos (usando o módulo spawner)
        spawn_initial_enemies(self)

        # Reinicia variáveis de estado do jogo
        self.cause_of_death = None
        self.playing = True

        # Mostra Introdução (movido para a lógica do loop principal)
        # display_intro(self)

        # Inicia o loop do jogo para esta sessão
        self.run()

    def run(self):
        """Loop principal do jogo para uma única sessão de jogo."""
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            if not self.playing: # Verifica se os eventos fizeram o jogo parar
                break
            self.update()
            self.draw()

    def events(self):
        """Processa todos os eventos do Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False # Para o loop externo também
            # Entrada do jogador (como pressionamentos de tecla) é processada em Player.get_keys
            # Cliques do mouse para atirar são processados em Player.get_keys
            # Tecla para recarregar (R) processada em Player.get_keys

    def update(self):
        """Atualiza todos os elementos do jogo."""
        if not self.camera or not self.player:
             print("Erro: Câmera ou Jogador não inicializados em update.")
             self.playing = False
             return

        self.camera.update(self.player)
        self.all_sprites.update(self.dt)

        # --- Detecção de Colisões ---
        # Jogador vs Inimigos
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            if hasattr(enemy, 'damage'):
                self.player.take_damage(enemy.damage)
            # else: imprimir aviso?

        # Balas vs Inimigos/Obstáculos (Processado em Bullet.update)

        # --- Verificações de Estado do Jogo ---
        self.check_radioactive_zones()

        if self.player.health <= 0:
            self.playing = False
            if not self.cause_of_death:
                self.cause_of_death = "Eliminado"

    def check_radioactive_zones(self):
        """Verifica se o jogador está em uma zona radioativa."""
        if not self.player or not self.radioactive_zones:
            return # Não pode verificar se o jogador ou zonas não existem
        in_zone_list = pygame.sprite.spritecollide(self.player, self.radioactive_zones, False)
        self.player.is_in_radioactive_zone = bool(in_zone_list)

    def draw(self):
        """Desenha todos os elementos do jogo."""
        if not self.camera:
            print("Erro: Câmera não inicializada em draw.")
            self.screen.fill(BLACK)
            pygame.display.flip()
            return

        self.screen.fill(BLACK)

        # --- Desenha tiles do mundo, itens, jogador, obstáculos, inimigos --- 
        # Usando desenho em camadas baseado na ordem de iteração do grupo (ajustar conforme necessário)
        for sprite in self.world_tiles:
            if self.camera.is_rect_visible(sprite.rect): # Culling básico
                self.screen.blit(sprite.image, self.camera.apply(sprite))
        for sprite in self.items:
            if self.camera.is_rect_visible(sprite.rect):
                 self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        # Desenha sprites do grupo all_sprites respeitando o offset da câmera
        # Assume que sprites atualizam seu rect corretamente OU camera.apply funciona
        # Prefere desenhar grupos específicos se as camadas são importantes
        for sprite in self.all_sprites:
             if self.camera.is_rect_visible(sprite.rect): # Culling
                 # Jogador e Inimigos têm seus próprios métodos draw que lidam com a câmera
                 if isinstance(sprite, (Player)): # Jogador desenhado separadamente depois?
                     pass
                 elif hasattr(sprite, 'draw') and callable(sprite.draw):
                      # Assume que draw personalizado lida com a câmera se necessário (como Enemy)
                      # sprite.draw(self.screen, self.camera) # Já chamado via update? Não.
                      pass # Inimigos desenhados via grupo enemy abaixo
                 elif hasattr(sprite, 'image'): # Desenha outros sprites (como Balas)
                     self.screen.blit(sprite.image, self.camera.apply(sprite))

        # Desenho explícito para o jogador (garante camadas corretas) 
        if self.player and hasattr(self.player, 'image'):
             self.screen.blit(self.player.image, self.camera.apply(self.player))
             if hasattr(self.player, 'draw_weapon'):
                  self.player.draw_weapon(self.screen, self.camera) # Desenha efeitos da arma
        
        # Desenho explícito para inimigos (garante camadas corretas e barras de vida)
        for enemy in self.enemies:
             if self.camera.is_rect_visible(enemy.rect):
                 enemy.draw(self.screen, self.camera) # Usa o método draw do inimigo

        # --- Efeitos Globais (Iluminação) ---
        # if ENABLE_LIGHTING and self.camera:
        #    self.camera.apply_lighting(self.screen)

        # --- HUD ---
        draw_hud(self) # Chama a função de hud.py

        pygame.display.flip()

    def quit(self):
        """Limpa e encerra o Pygame."""
        pygame.quit()
        sys.exit() 
