import pygame
from core.settings import BULLET_DAMAGE, BULLET_RENDER_LAYER, BULLET_COLOR, BULLET_WIDTH, BULLET_HEIGHT
vec = pygame.math.Vector2

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