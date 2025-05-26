import pygame
from core.settings import BULLET_DAMAGE, BULLET_RENDER_LAYER, BULLET_COLOR, BULLET_WIDTH, BULLET_HEIGHT, FX_RENDER_LAYER, BLACK
vec = pygame.math.Vector2
import random

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, direction, speed):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self._layer = BULLET_RENDER_LAYER
        self.damage = BULLET_DAMAGE
        self.position = vec(start_pos)
        self.velocity = direction * speed
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position

        if self.collide_with_obstacles():
            self.kill()
            return

        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in enemy_hits:
            if hasattr(enemy, 'take_damage'):
                enemy.take_damage(self.damage)
                self.kill()
                return

        if self.off_screen():
            self.kill()

    def off_screen(self):
        if self.rect.right < 0 or self.rect.left > self.game.map_width:
            return True
        if self.rect.bottom < 0 or self.rect.top > self.game.map_height:
            return True
        return False

    def collide_with_obstacles(self):
        for obstacle in self.game.obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True
        return False

    def draw(self, screen, camera):
        screen_rect = camera.apply(self)
        screen.blit(self.image, screen_rect)

class Casing(pygame.sprite.Sprite):
    def __init__(self, game, pos, player_facing_right):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = FX_RENDER_LAYER

        self.image_orig = pygame.Surface((5, 3))
        self.image_orig.fill((200, 180, 0))
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=pos)

        self.pos = vec(pos)

        eject_x = random.uniform(20, 40) if player_facing_right else random.uniform(-40, -20)
        self.vel = vec(eject_x, random.uniform(-100, -140))
        self.acc = vec(0, 500)

        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-360, 360)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 800

    def update(self, dt):

        self.vel += self.acc * dt
        self.pos += self.vel * dt

        self.angle = (self.angle + self.rot_speed * dt) % 360
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
