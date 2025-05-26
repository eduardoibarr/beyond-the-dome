import pygame
from core.settings import *
from graphics.sprites.enemy_base import Enemy
from core.ai.enhanced_ai import EnhancedRaiderAI

class Raider(Enemy):
    def __init__(self, game, x_pixel, y_pixel):

        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED * TILE_SIZE

        self.ai_controller = EnhancedRaiderAI(self)

        self.is_attacking = False
        self.attack_timer = 0

        self._create_sprite()

    def _create_sprite(self):
        if hasattr(self.game, 'asset_manager'):

            soldier_base = "assets/images/tds-pixel-art-modern-soldiers-and-vehicles-sprites/Soldier 02/"

            if self.health <= 0:

                death_frame = min(4, max(1, 4 - int((self.health / self.max_health) * 4)))
                asset_path = soldier_base + f"Die/SD2_0{death_frame}.png"
            elif hasattr(self, 'is_attacking') and self.is_attacking:

                attack_frame = (pygame.time.get_ticks() // 100) % 5 + 1
                asset_path = soldier_base + f"Fire/SF_0{attack_frame}.png"
            else:

                asset_path = soldier_base + "Soldier02.png"

            try:
                self.image = self.game.asset_manager.get_image(asset_path).copy()

                if self.image.get_width() != ENEMY_WIDTH or self.image.get_height() != ENEMY_HEIGHT:
                    self.image = pygame.transform.scale(self.image, (ENEMY_WIDTH, ENEMY_HEIGHT))

                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

                self.rect = self.image.get_rect(center=self.position)
                return
            except Exception as e:
                print(f"Erro ao carregar sprite do Raider: {e}")

        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_RAIDER_COLOR)
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        super().update(dt)

        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False

        self._create_sprite()

    def attack(self):

        self.is_attacking = True
        self.attack_timer = 0.5

        if hasattr(self.game, 'asset_manager'):
            self.game.asset_manager.play_sound('raider_attack')

        hitbox_offset = TILE_SIZE * 0.6
        hitbox_width = TILE_SIZE * 0.8
        hitbox_height = self.rect.height * 0.9

        if self.facing_right:
            hitbox_center_x = self.rect.centerx + hitbox_offset
        else:
            hitbox_center_x = self.rect.centerx - hitbox_offset
        hitbox_center_y = self.rect.centery

        attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

        if attack_hitbox.colliderect(self.game.player.rect):
            self.game.player.take_damage(self.damage)
