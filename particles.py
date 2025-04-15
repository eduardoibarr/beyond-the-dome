import pygame
import random
import math
from settings import *

class BloodParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BLOOD_PARTICLE_SIZE
        self.color = BLOOD_PARTICLE_COLOR
        self.lifetime = BLOOD_PARTICLE_LIFETIME
        self.created_at = pygame.time.get_ticks()
        
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * BLOOD_PARTICLE_SPEED
        self.vy = math.sin(angle) * BLOOD_PARTICLE_SPEED

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1

    def is_dead(self):
        return pygame.time.get_ticks() - self.created_at > self.lifetime

    def draw(self, screen):
        elapsed_time = pygame.time.get_ticks() - self.created_at
        lifetime_fraction = max(0, 1 - (elapsed_time / self.lifetime))
        
        alpha = max(0, min(255, int(255 * lifetime_fraction)))
        
        if alpha > 0:
            color = (*self.color, alpha)
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (self.size, self.size), self.size)
            screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))

class BloodParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particles(self, x, y):
        for _ in range(BLOOD_PARTICLE_COUNT):
            self.particles.append(BloodParticle(x, y))

    def update(self):
        self.particles = [p for p in self.particles if not p.is_dead()]
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)