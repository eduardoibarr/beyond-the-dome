import pygame
import random
from core.settings import *
from graphics.particles import BloodParticleSystem

vec = pygame.math.Vector2

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x_pixel, y_pixel, groups):
        self._layer = 2
        self.groups = groups
        super().__init__(self.groups)
        self.game = game

        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.speed = 50
        self.invincibility_duration = ENEMY_INVINCIBILITY_DURATION

        self.position = vec(x_pixel, y_pixel)
        self.velocity = vec(0, 0)
        self.rect = None

        self.ai_controller = None
        self.last_hit_time = 0
        self.invincible = False

        self.blood_system = BloodParticleSystem()

        self.animations = {}
        self.current_animation = None
        self.animation_frame = 0
        self.animation_frame_duration = 0.15
        self.animation_timer = 0
        self.facing_right = random.choice([True, False])
        self.original_image = None
        self.image = None

    def setup_animations(self, enemy_type):

        if not hasattr(self.game, 'asset_manager'):
            print(f"Erro: Asset manager não encontrado para {type(self).__name__}.")
            return False

        try:

            anim_idle = f"{enemy_type}_idle"
            anim_walk = f"{enemy_type}_walk"
            anim_hurt = f"{enemy_type}_hurt"
            anim_attack = f"{enemy_type}_attack"

            idle_frames = self.game.asset_manager.get_animation(anim_idle)
            walk_frames = self.game.asset_manager.get_animation(anim_walk)
            hurt_frames = self.game.asset_manager.get_animation(anim_hurt)
            attack_frames = self.game.asset_manager.get_animation(anim_attack)

            if not idle_frames:
                idle_frames = self.game.asset_manager.get_animation('enemy_idle')
            if not walk_frames:
                walk_frames = self.game.asset_manager.get_animation('enemy_walk')
            if not hurt_frames:
                hurt_frames = self.game.asset_manager.get_animation('enemy_hurt')
            if not attack_frames:
                attack_frames = self.game.asset_manager.get_animation('enemy_attack')

            if not idle_frames:
                raise ValueError(f"Nenhum frame encontrado para a animação 'idle' do inimigo {enemy_type}.")

            self.animations = {
                ANIM_ENEMY_IDLE: idle_frames,
                ANIM_ENEMY_WALK: walk_frames if walk_frames else idle_frames,
                ANIM_ENEMY_HURT: hurt_frames if hurt_frames else idle_frames,
                ANIM_ENEMY_SLASH: attack_frames if attack_frames else idle_frames
            }

            self.current_animation = ANIM_ENEMY_IDLE
            self.image = self.animations[ANIM_ENEMY_IDLE][0]
            self.original_image = self.image
            self.rect = self.image.get_rect(center=self.position)
            print(f"Animações carregadas para {type(self).__name__}")
            return True

        except Exception as e:
            print(f"Erro ao configurar animações para {type(self).__name__}: {e}")
            self.animations = {}
            self.current_animation = None

            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(RED)
            self.rect = self.image.get_rect(center=self.position)
            return False

    def set_animation(self, animation_name):
        if not self.animations or self.current_animation == animation_name:
            return
        if animation_name in self.animations:

             if self.current_animation == ANIM_ENEMY_HURT and self.animation_frame < len(self.animations[ANIM_ENEMY_HURT]) - 1:
                  return
             self.current_animation = animation_name
             self.animation_frame = 0
             self.animation_timer = 0
        else:

             if ANIM_ENEMY_IDLE in self.animations: self.current_animation = ANIM_ENEMY_IDLE

    def update_animation(self, dt):
        if not self.current_animation or not self.animations: return

        frames = self.animations[self.current_animation]
        num_frames = len(frames)
        if num_frames == 0: return

        current_frame_duration = self.animation_frame_duration
        if self.current_animation == ANIM_ENEMY_WALK:
            speed_mag = self.velocity.length()
            if speed_mag > 1.0 and self.speed > 0:
                 speed_factor = max(0.5, min(1.5, speed_mag / self.speed))
                 current_frame_duration = self.animation_frame_duration / speed_factor

        self.animation_timer += dt
        while self.animation_timer >= current_frame_duration:
            self.animation_timer -= current_frame_duration
            self.animation_frame = (self.animation_frame + 1) % num_frames
            if self.animation_frame == 0:
                 if self.current_animation in [ANIM_ENEMY_HURT, ANIM_ENEMY_SLASH]:
                      self.set_animation(ANIM_ENEMY_IDLE)

        self.original_image = frames[self.animation_frame]
        self.image = self.original_image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def move_towards(self, target_pos, dt):
        direction = target_pos - self.position
        dist = direction.length()

        if dist > 1.0:
            self.velocity = direction.normalize() * self.speed

            if self.velocity.x > 0.1: self.facing_right = True
            elif self.velocity.x < -0.1: self.facing_right = False
            self.set_animation(ANIM_ENEMY_WALK)
        else:
            self.velocity = vec(0, 0)
            self.set_animation(ANIM_ENEMY_IDLE)

        new_position = self.position + self.velocity * dt
        self.position = self.collide_with_obstacles(new_position)
        if self.rect: self.rect.center = self.position

    def collide_with_obstacles(self, new_position):
         potential_rect = self.rect.copy()
         potential_rect.center = new_position
         for obstacle in self.game.obstacles:
              if potential_rect.colliderect(obstacle.rect):
                   self.velocity = vec(0, 0)
                   return self.position
         return new_position

    def take_damage(self, amount):
        self.health -= amount
        self.health = max(0, self.health)
        self.blood_system.add_particles(self.rect.centerx, self.rect.centery, count=3)
        self.set_animation(ANIM_ENEMY_HURT)

        if self.ai_controller:

            self.ai_controller.alert_damage(self.game.player.position)

        if self.health <= 0:

            if hasattr(self.game, 'trigger_mission_event'):
                enemy_type = self.__class__.__name__.lower()
                if "raider" in enemy_type:
                    self.game.trigger_mission_event("kill", "raider", 1)
                elif "wilddog" in enemy_type or "dog" in enemy_type:
                    self.game.trigger_mission_event("kill", "wild_dog", 1)
                elif "scavenger" in enemy_type:
                    self.game.trigger_mission_event("kill", "friendly_scavenger", 1)

            if hasattr(self.game, 'create_explosion'):
                if "explosive" in enemy_type or "fuel" in enemy_type:
                    self.game.create_explosion(self.position.x, self.position.y, "fuel", 1.2)

            self.kill()

    def draw_health_bar(self, screen, camera):
        if self.health <= 0 or self.max_health <= 0 or not self.rect: return

        health_pct = max(0.0, min(1.0, self.health / self.max_health))
        bar_width = ENEMY_HEALTH_BAR_WIDTH
        bar_height = ENEMY_HEALTH_BAR_HEIGHT

        screen_rect = camera.apply(self)
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - ENEMY_HEALTH_BAR_OFFSET - bar_height

        color_r = int(ENEMY_HEALTH_BAR_COLOR_MIN[0] + (ENEMY_HEALTH_BAR_COLOR_MAX[0] - ENEMY_HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(ENEMY_HEALTH_BAR_COLOR_MIN[1] + (ENEMY_HEALTH_BAR_COLOR_MAX[1] - ENEMY_HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(ENEMY_HEALTH_BAR_COLOR_MIN[2] + (ENEMY_HEALTH_BAR_COLOR_MAX[2] - ENEMY_HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_color = (max(0,min(255,color_r)), max(0,min(255,color_g)), max(0,min(255,color_b)))

        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_pct), bar_height)
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BACKGROUND_COLOR, bg_rect)
        if health_pct > 0:
            pygame.draw.rect(screen, current_color, fill_rect)
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BORDER_COLOR, bg_rect, 1)

    def update(self, dt):

        if self.ai_controller:
            self.ai_controller.update(dt)

        new_position = self.position + self.velocity * dt
        self.position = self.collide_with_obstacles(new_position)
        if self.rect: self.rect.center = self.position

        self.update_animation(dt)
        self.blood_system.update(dt)

    def draw(self, screen, camera):
        if not self.rect: return

        screen_rect = camera.apply(self)

        if screen_rect.colliderect(screen.get_rect()):
            if self.image:
                screen.blit(self.image, screen_rect)
            else:

                fallback_rect = pygame.Rect(screen_rect.left, screen_rect.top, ENEMY_WIDTH, ENEMY_HEIGHT)
                pygame.draw.rect(screen, RED, fallback_rect)

            self.draw_health_bar(screen, camera)

        self.blood_system.draw(screen, camera)

    def attack(self):
        if not self.game.player.invincible:
            self.game.player.take_damage(self.damage)

            self.set_animation(ANIM_ENEMY_SLASH)
            return True
        return False
