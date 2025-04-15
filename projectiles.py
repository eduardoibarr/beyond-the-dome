import pygame
import math
from settings import *

class Stone(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, direction, speed):
        self._layer = 1
        self.groups = game.all_sprites, game.stones
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.pos = pygame.math.Vector2(start_pos)
        self.direction = direction.normalize()
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.speed = speed
        self.velocity = self.direction * speed
        self.spawn_time = pygame.time.get_ticks()
        
        self.image = self.create_stone_image()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        self.damage = STONE_DAMAGE
        
    def create_stone_image(self):
        size = STONE_RADIUS * 2
        stone_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        stone_surface.fill((0, 0, 0, 0))
        
        pygame.draw.circle(stone_surface, STONE_COLOR, 
                          (STONE_RADIUS, STONE_RADIUS), STONE_RADIUS)
        return stone_surface
        
    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > STONE_LIFETIME:
            self.kill()
            return
        
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        self.rect.center = self.pos
        
        for enemy in self.game.enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.kill()  
                return  
                
        if (self.pos.x < 0 or self.pos.x > WIDTH or
            self.pos.y < 0 or self.pos.y > HEIGHT):
            self.kill() 