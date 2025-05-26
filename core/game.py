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
from graphics.ui.screens import display_intro
from core.inventory import InventoryUI

class Game:
    def __init__(self):

        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.running = True
        self.playing = False
        self.dt = 0
        self.cause_of_death = None

        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT

        self.load_fonts()

        self.asset_manager = AssetManager()
        self.audio_manager = AudioManager(self.asset_manager)

        self.particle_systems = type('ParticleSystems', (), {})()
        self.particle_systems.radiation = RadiationSystem()

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

        self.noise_generator = NoiseGenerator(
            seed=random.randint(0, 1000),
            scale=100.0,
            octaves=6,
            persistence=0.5,
            lacunarity=2.0
        )

    def load_fonts(self):
        try:
            font_path = pygame.font.match_font('arial') or pygame.font.get_default_font()
            self.font = pygame.font.Font(font_path, HUD_FONT_SIZE)
            self.intro_title_font = pygame.font.Font(font_path, INTRO_TITLE_FONT_SIZE)
            self.intro_font = pygame.font.Font(font_path, INTRO_FONT_SIZE)
            self.prompt_font = pygame.font.Font(font_path, PROMPT_FONT_SIZE)
            self.game_over_font = pygame.font.Font(font_path, GAME_OVER_FONT_SIZE)
        except Exception:

            self.font = pygame.font.Font(None, HUD_FONT_SIZE)
            self.intro_title_font = pygame.font.Font(None, INTRO_TITLE_FONT_SIZE)
            self.intro_font = pygame.font.Font(None, INTRO_FONT_SIZE)
            self.prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)
            self.game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.world_tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.radioactive_zones = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        self.level_generator = LevelGenerator(self)
        spawn_point = self.level_generator.create_level()

        if not self.camera:
            self.camera = Camera(self.map_width, self.map_height)
        spawn_x, spawn_y = spawn_point
        PlayerClass = self.asset_manager.get_sprite_class('player')
        if not PlayerClass:
            print("Classe Player não encontrada!")
            self.playing = False
            return
        self.player = PlayerClass(self, spawn_x * TILE_SIZE, spawn_y * TILE_SIZE)

        self.inventory_ui = InventoryUI(self, self.player.inventory)

        spawn_initial_enemies(self, self.asset_manager)
        self.cause_of_death = None
        self.playing = True
        self.run()

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            if not self.playing:
                break
            self.update()
            self.draw()

    def events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_TAB]:
            print("[DEBUG] TAB key detected via get_pressed()")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if hasattr(self, 'mission_journal') and self.mission_journal.visible:
                        pass
                    elif hasattr(self, 'inventory_ui'):
                        self.inventory_ui.visible = not self.inventory_ui.visible
                        continue
                    else:
                        print("[DEBUG] Inventário UI não existe!")
                elif event.key == pygame.K_i:
                    if hasattr(self, 'inventory_ui'):
                        self.inventory_ui.visible = not self.inventory_ui.visible
                        continue

            if hasattr(self, 'mission_journal'):
                self.mission_journal.handle_input(event)

            journal_is_visible = hasattr(self, 'mission_journal') and self.mission_journal.visible
            if (hasattr(self, 'inventory_ui') and 
                not (event.type == pygame.KEYDOWN and event.key == pygame.K_TAB) and
                not journal_is_visible):
                self.inventory_ui.handle_input(event)

    def update(self):
        if not self.camera or not self.player:
            self.playing = False
            return

        self.camera.update(self.player)
        self.all_sprites.update(self.dt)

        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:

            if hasattr(enemy, 'attack'):
                enemy.attack()

            elif hasattr(enemy, 'damage') and not self.player.invincible:
                self.player.take_damage(enemy.damage)

                push_direction = self.player.position - enemy.position
                if push_direction.length() > 0:
                    push_direction = push_direction.normalize() * 5
                    self.player.position += push_direction

        self.check_radioactive_zones()

        if getattr(self.player, 'is_in_radioactive_zone', False):
            cx, cy = self.player.rect.center
            self.particle_systems.radiation.emit(cx, cy, count=5)

        self.particle_systems.radiation.update(self.dt)

        if self.player.health <= 0:
            self.playing = False
            if not self.cause_of_death:
                self.cause_of_death = "Eliminado"

    def check_radioactive_zones(self):
        if not self.player or not self.radioactive_zones:
            return
        in_zone = pygame.sprite.spritecollide(self.player, self.radioactive_zones, False)
        self.player.is_in_radioactive_zone = bool(in_zone)

    def draw(self):
        if not self.camera:
            self.screen.fill(BLACK)
            pygame.display.flip()
            return

        self.screen.fill(BLACK)

        for tile in self.world_tiles:
            if self.camera.is_rect_visible(tile.rect):
                self.screen.blit(tile.image, self.camera.apply(tile))

        for item in self.items:
            if self.camera.is_rect_visible(item.rect):
                self.screen.blit(item.image, self.camera.apply(item))

        for sprite in self.all_sprites:
            if self.camera.is_rect_visible(sprite.rect) and hasattr(sprite, 'image'):
                self.screen.blit(sprite.image, self.camera.apply(sprite))

        if self.player and hasattr(self.player, 'image'):
            self.screen.blit(self.player.image, self.camera.apply(self.player))
            if hasattr(self.player, 'draw_weapon'):
                self.player.draw_weapon(self.screen, self.camera)

        for enemy in self.enemies:
            if self.camera.is_rect_visible(enemy.rect):
                enemy.draw(self.screen, self.camera)

        self.particle_systems.radiation.draw(self.screen, self.camera)

        draw_hud(self)

        if hasattr(self, 'mission_ui'):
            self.mission_ui.draw(self.screen)

        if hasattr(self, 'mission_journal'):
            self.mission_journal.draw(self.screen)

        if hasattr(self, 'inventory_ui'):
            self.inventory_ui.draw(self.screen)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

    def play_audio(self, key, volume=1.0, loop=False):
        if self.audio_manager:
            return self.audio_manager.play(key, volume, loop)
        return None

    def stop_audio(self, sound=None, fadeout_ms=500):
        if self.audio_manager:
            self.audio_manager.stop(sound, fadeout_ms)

    def stop_music(self, fadeout_ms=500):
        if self.audio_manager:
            self.audio_manager.stop_music(fadeout_ms)
