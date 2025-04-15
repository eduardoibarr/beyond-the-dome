import pygame
from settings import *
from ai import RaiderAIController, WildDogAIController
from weapons import Slingshot
from particles import BloodParticleSystem

vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.image.set_colorkey(BLACK) 
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.vx, self.vy = 0, 0
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.last_hit_time = 0
        self.invincible = False
        self.stone_count = STONE_INITIAL_COUNT
        self.slingshot = Slingshot(game, self)
        self.blood_system = BloodParticleSystem()

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= amount
            for _ in range(3):
                self.blood_system.add_particles(self.rect.centerx, self.rect.centery)
            self.last_hit_time = now
            self.invincible = True
            if self.health <= 0:
                self.kill()
                self.game.playing = False

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def update(self):
        now = pygame.time.get_ticks()
        if self.invincible and now - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
            self.invincible = False

        self.get_keys()
        self.move(self.vx, self.vy)
        self.rect.x = self.x
        self.rect.y = self.y
        self.slingshot.update()
        self.blood_system.update()

        if self.invincible:
            alpha = 128 if now % 200 < 100 else 255
            temp_image = self.original_image.copy().convert_alpha()
            temp_image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = temp_image
        else:
            self.image = self.original_image

    def draw_weapon(self, screen):
        self.slingshot.draw(screen)
        self.blood_system.draw(screen)

    def has_stones(self):
        return self.stone_count > 0
        
    def use_stone(self):
        if self.stone_count > 0:
            self.stone_count -= 1
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, groups):
        self._layer = 2
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = None
        self.rect = None
        self.pos = vec(x * TILE_SIZE, y * TILE_SIZE)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = 0
        self.max_health = 0
        self.damage = 0
        self.speed = 0
        self.ai_controller = None
        self.blood_system = BloodParticleSystem()

    def move(self, dx, dy):
        self.pos += vec(dx, dy)
        self.rect.center = self.pos

    def take_damage(self, amount):
        self.health -= amount
        for _ in range(3):
            self.blood_system.add_particles(self.rect.centerx, self.rect.centery)
        if self.ai_controller:
            self.ai_controller.alert_damage(vec(self.game.player.rect.center))
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, screen):
        if self.health <= 0:
            return

        health_pct = self.health / self.max_health
        bar_width = ENEMY_HEALTH_BAR_WIDTH
        bar_height = ENEMY_HEALTH_BAR_HEIGHT
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - ENEMY_HEALTH_BAR_OFFSET - bar_height

        color_r = int(ENEMY_HEALTH_BAR_COLOR_MIN[0] + (ENEMY_HEALTH_BAR_COLOR_MAX[0] - ENEMY_HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(ENEMY_HEALTH_BAR_COLOR_MIN[1] + (ENEMY_HEALTH_BAR_COLOR_MAX[1] - ENEMY_HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(ENEMY_HEALTH_BAR_COLOR_MIN[2] + (ENEMY_HEALTH_BAR_COLOR_MAX[2] - ENEMY_HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_color = (color_r, color_g, color_b)

        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BACKGROUND_COLOR, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        if health_pct > 0:
            pygame.draw.rect(screen, current_color, 
                           (bar_x, bar_y, int(bar_width * health_pct), bar_height))
        
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BORDER_COLOR, 
                        (bar_x, bar_y, bar_width, bar_height), 1)

    def update(self):
        if self.ai_controller:
            self.ai_controller.update()
        self.blood_system.update()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.draw_health_bar(screen)
        self.blood_system.draw(screen)

class Raider(Enemy):
    def __init__(self, game, x, y):
        groups = game.all_sprites, game.enemies
        super().__init__(game, x, y, groups)

        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_RAIDER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED
        self.ai_controller = RaiderAIController(self)

class WildDog(Enemy):
    def __init__(self, game, x, y):
        groups = game.all_sprites, game.enemies
        super().__init__(game, x, y, groups)

        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_DOG_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.health = ENEMY_DOG_HEALTH
        self.max_health = ENEMY_DOG_HEALTH
        self.damage = ENEMY_DOG_DAMAGE
        self.speed = ENEMY_DOG_SPEED
        self.ai_controller = WildDogAIController(self)
