import pygame
from core.settings import *
from graphics.sprites.enemy_base import Enemy
from core.ai.enhanced_ai import EnhancedFriendlyScavengerAI

class FriendlyScavenger(Enemy):
    def __init__(self, game, x_pixel, y_pixel):

        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED * TILE_SIZE

        self.friendly_color = BLUE

        if not self.setup_animations('raider'):

            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(self.friendly_color)
            self.rect = self.image.get_rect(center=self.position)

        self.ai_controller = EnhancedFriendlyScavengerAI(self)
        self.ai_controller.game = game

        self.previous_keys = {
            pygame.K_e: False,
            pygame.K_y: False,
            pygame.K_n: False
        }

        self._create_sprite()

    def _create_sprite(self):
        if hasattr(self.game, 'asset_manager'):

            soldier_base = "assets/images/tds-pixel-art-modern-soldiers-and-vehicles-sprites/Soldier/"

            asset_path = soldier_base + "Soldier.png"

            try:
                self.image = self.game.asset_manager.get_image(asset_path).copy()

                if self.image.get_width() != ENEMY_WIDTH or self.image.get_height() != ENEMY_HEIGHT:
                    self.image = pygame.transform.scale(self.image, (ENEMY_WIDTH, ENEMY_HEIGHT))

                self.image.fill((100, 200, 150), special_flags=pygame.BLEND_MULT)

                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)

                self.rect = self.image.get_rect(center=self.position)
                return
            except Exception as e:
                print(f"Erro ao carregar sprite do Friendly Scavenger: {e}")

        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill((0, 150, 100))
        self.rect = self.image.get_rect(center=self.position)

    def take_damage(self, amount, source="player"):

        player_pos = self.game.player.position
        self.ai_controller.alert_damage(player_pos)

        super().take_damage(amount)

    def attack(self):

        if self.ai_controller.has_become_hostile:

            if self.current_animation == ANIM_ENEMY_SLASH:
                return

            self.set_animation(ANIM_ENEMY_SLASH)

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

    def draw(self, screen, camera):

        super().draw(screen, camera)

        if self.ai_controller.current_dialogue:

            font = pygame.font.Font(None, 22)

            text_surface = font.render(self.ai_controller.current_dialogue, True, WHITE)
            text_rect = text_surface.get_rect()

            dialogue_x = self.rect.centerx - text_rect.width // 2
            dialogue_y = self.rect.top - text_rect.height - 10
            dialogue_pos = camera.apply_coords(dialogue_x, dialogue_y)

            padding = 5
            bg_rect = pygame.Rect(
                dialogue_pos[0] - padding,
                dialogue_pos[1] - padding,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, self.friendly_color, bg_rect, 2)

            screen.blit(text_surface, dialogue_pos)

    def update(self, dt):
        super().update(dt)
        self._create_sprite()

        current_keys = pygame.key.get_pressed()

        player_pos = pygame.math.Vector2(self.game.player.position)
        enemy_pos = pygame.math.Vector2(self.position)
        distance_to_player = enemy_pos.distance_to(player_pos)

        interaction_distance = TILE_SIZE * 3
        if distance_to_player < interaction_distance:

            if current_keys[pygame.K_e] and not self.previous_keys[pygame.K_e]:
                self.ai_controller.advance_dialogue()

            if current_keys[pygame.K_y] and not self.previous_keys[pygame.K_y] and self.ai_controller.interaction_state == "PROPOSAL":
                self.ai_controller.accept_proposal()

            if current_keys[pygame.K_n] and not self.previous_keys[pygame.K_n] and self.ai_controller.interaction_state == "PROPOSAL":
                self.ai_controller.refuse_proposal()

        self.previous_keys[pygame.K_e] = current_keys[pygame.K_e]
        self.previous_keys[pygame.K_y] = current_keys[pygame.K_y]
        self.previous_keys[pygame.K_n] = current_keys[pygame.K_n]
