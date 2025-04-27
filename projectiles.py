# Importação das bibliotecas necessárias
import pygame
import math
from settings import *

# Classe da Pedra (projétil)
class Stone(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, direction, speed):
        # Inicialização do sprite da pedra
        self._layer = 1
        self.groups = game.all_sprites, game.stones
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Configuração da posição e movimento
        self.pos = pygame.math.Vector2(start_pos)
        self.direction = direction.normalize()
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        self.speed = speed
        self.velocity = self.direction * speed
        self.spawn_time = pygame.time.get_ticks()
        
        # Criação da imagem e retângulo da pedra
        self.image = self.create_stone_image()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        # Configuração do dano
        self.damage = STONE_DAMAGE
        
    def create_stone_image(self):
        # Cria a imagem circular da pedra
        size = STONE_RADIUS * 2
        stone_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        stone_surface.fill((0, 0, 0, 0))
        
        pygame.draw.circle(stone_surface, STONE_COLOR, 
                          (STONE_RADIUS, STONE_RADIUS), STONE_RADIUS)
        return stone_surface
        
    def update(self):
        # Verifica se a pedra expirou
        if pygame.time.get_ticks() - self.spawn_time > STONE_LIFETIME:
            self.kill()
            return
        
        # Atualiza a posição da pedra
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        self.rect.center = self.pos
        
        # Verifica colisão com inimigos
        for enemy in self.game.enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.kill()  
                return  
                
        # Verifica se a pedra saiu da tela
        if (self.pos.x < 0 or self.pos.x > WIDTH or
            self.pos.y < 0 or self.pos.y > HEIGHT):
            self.kill() 