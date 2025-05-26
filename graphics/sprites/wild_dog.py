import pygame
from core.settings import *
from graphics.sprites.enemy_base import Enemy
from core.ai.enhanced_ai import EnhancedWildDogAI

class WildDog(Enemy):
    def __init__(self, game, x_pixel, y_pixel):

        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        self.health = ENEMY_DOG_HEALTH
        self.max_health = ENEMY_DOG_HEALTH
        self.damage = ENEMY_DOG_DAMAGE
        self.speed = ENEMY_DOG_SPEED * TILE_SIZE

        if not self.setup_animations('wild_dog'):

            dog_width = int(ENEMY_WIDTH * 0.8)
            dog_height = int(ENEMY_HEIGHT * 0.8)
            self.image = pygame.Surface((dog_width, dog_height))
            self.image.fill(ENEMY_DOG_COLOR)
            self.rect = self.image.get_rect(center=self.position)

        self.ai_controller = EnhancedWildDogAI(self)

        self.is_attacking = False
        self.attack_timer = 0

        self._create_sprite()

    def _create_sprite(self):
        if hasattr(self.game, 'asset_manager'):

            soldier_base = "assets/images/tds-pixel-art-modern-soldiers-and-vehicles-sprites/Soldier/"

            if self.health <= 0:

                death_frame = min(4, max(1, 4 - int((self.health / self.max_health) * 4)))
                asset_path = soldier_base + f"Die/SD_{death_frame}.png"
            elif self.is_attacking:

                asset_path = soldier_base + "SoldierWaepon.png"
            else:

                asset_path = soldier_base + "Soldier.png"

            try:
                self.image = self.game.asset_manager.get_image(asset_path).copy()

                dog_size = int(ENEMY_WIDTH * 0.8)
                if self.image.get_width() != dog_size or self.image.get_height() != dog_size:
                    self.image = pygame.transform.scale(self.image, (dog_size, dog_size))

                self.image.fill((180, 140, 60), special_flags=pygame.BLEND_MULT)

                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

                self.rect = self.image.get_rect(center=self.position)
                return
            except Exception as e:
                print(f"Erro ao carregar sprite do Wild Dog: {e}")

        dog_size = int(ENEMY_WIDTH * 0.8)
        self.image = pygame.Surface((dog_size, dog_size))
        self.image.fill(ENEMY_DOG_COLOR)
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
        self.attack_timer = 0.3

        if hasattr(self.game, 'asset_manager'):
            self.game.asset_manager.play_sound('wild_dog_bite')

        attack_range = ENEMY_ATTACK_RADIUS * 0.7

        if self.position.distance_squared_to(self.game.player.position) < attack_range**2:
            self.game.player.take_damage(self.damage)
