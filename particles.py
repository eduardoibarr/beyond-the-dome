# Importação das bibliotecas necessárias
import pygame
import random
import math
from settings import *

# Classe da partícula de sangue
class BloodParticle:
    def __init__(self, x, y):
        # Inicialização da partícula
        self.x = x
        self.y = y
        self.size = BLOOD_PARTICLE_SIZE
        self.color = BLOOD_PARTICLE_COLOR
        self.lifetime = BLOOD_PARTICLE_LIFETIME
        self.created_at = pygame.time.get_ticks()
        
        # Define direção aleatória para a partícula
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * BLOOD_PARTICLE_SPEED
        self.vy = math.sin(angle) * BLOOD_PARTICLE_SPEED

    def update(self):
        # Atualiza a posição da partícula (com gravidade)
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1

    def is_dead(self):
        # Verifica se a partícula expirou
        return pygame.time.get_ticks() - self.created_at > self.lifetime

    def draw(self, screen):
        # Desenha a partícula com fade out
        elapsed_time = pygame.time.get_ticks() - self.created_at
        lifetime_fraction = max(0, 1 - (elapsed_time / self.lifetime))
        
        # Calcula a transparência baseada no tempo de vida
        alpha = max(0, min(255, int(255 * lifetime_fraction)))
        
        if alpha > 0:
            color = (*self.color, alpha)
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (self.size, self.size), self.size)
            screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))

# Sistema de partículas de sangue
class BloodParticleSystem:
    def __init__(self):
        # Inicialização do sistema de partículas
        self.particles = []

    def add_particles(self, x, y):
        # Adiciona novas partículas na posição especificada
        for _ in range(BLOOD_PARTICLE_COUNT):
            self.particles.append(BloodParticle(x, y))

    def update(self):
        # Atualiza todas as partículas e remove as mortas
        self.particles = [p for p in self.particles if not p.is_dead()]
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        # Desenha todas as partículas
        for particle in self.particles:
            particle.draw(screen)