import pygame
import random
import math
from core.settings import (
    BLOOD_PARTICLE_SIZE,
    BLOOD_PARTICLE_COLOR,
    BLOOD_PARTICLE_LIFETIME,
    BLOOD_PARTICLE_SPEED,
    BLOOD_PARTICLE_COUNT,
    RAD_PARTICLE_SPEED,
    RAD_PARTICLE_LIFETIME,
    WATER_HIGHLIGHT
)

class BloodParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BLOOD_PARTICLE_SIZE
        self.color = BLOOD_PARTICLE_COLOR
        self.lifetime = BLOOD_PARTICLE_LIFETIME
        self.created_at = pygame.time.get_ticks()

        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(BLOOD_PARTICLE_SPEED*0.5, BLOOD_PARTICLE_SPEED*1.5)
        self.vx = math.cos(angle)*speed
        self.vy = math.sin(angle)*speed
        self.gravity = 0.1

    def update(self, dt):
        self.vy += self.gravity * dt * 60
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60

    def is_dead(self):
        return pygame.time.get_ticks() - self.created_at > self.lifetime

    def get_alpha(self):
        elapsed = pygame.time.get_ticks() - self.created_at
        frac = max(0.0, 1.0 - elapsed/self.lifetime)
        return int(255*frac) if self.lifetime>0 else 0

    def draw(self, screen, camera):
        alpha = self.get_alpha()
        if alpha<=0: return

        rect = pygame.Rect(int(self.x), int(self.y), self.size*2, self.size*2)
        screen_rect = camera.apply(rect)
        if not screen_rect.colliderect(screen.get_rect()): return

        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        draw_color = (*self.color[:3], alpha)
        pygame.draw.circle(surf, draw_color, (self.size, self.size), self.size)
        screen.blit(surf, screen_rect.topleft)

class BloodParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particles(self, x, y, count=BLOOD_PARTICLE_COUNT):
        for _ in range(count):
            self.particles.append(BloodParticle(x, y))

    def update(self, dt):
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen, camera):
        for p in self.particles: p.draw(screen, camera)

class RadiationParticle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)

        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(RAD_PARTICLE_SPEED*0.5, RAD_PARTICLE_SPEED*1.5)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.uniform(RAD_PARTICLE_LIFETIME*0.5, RAD_PARTICLE_LIFETIME)
        self.age = 0.0
        self.size = random.randint(1, 3)

    def update(self, dt):
        self.pos += self.vel * dt
        self.age += dt

    def is_dead(self):
        return self.age >= self.life

    def draw(self, screen, camera):
        alpha = max(0, 255 * (1 - self.age/self.life))
        if alpha<=0: return

        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0,255,0,int(alpha)), (self.size, self.size), self.size)

        rect = pygame.Rect(
            int(self.pos.x-self.size),
            int(self.pos.y-self.size),
            self.size*2, self.size*2
        )
        screen.blit(surf, camera.apply(rect).topleft)

class RadiationSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=10):
        for _ in range(count):
            self.particles.append(RadiationParticle(x, y))

    def update(self, dt):
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen, camera):
        for p in self.particles: p.draw(screen, camera)

class WaterRippleSystem:
    def __init__(self):
        self.ripples = []
        self.max_ripples = 10

    def add_ripple(self, x, y):

        if len(self.ripples) >= self.max_ripples:
            return

        size = random.uniform(8, 15)
        duration = random.uniform(0.6, 1.0)
        max_radius = random.uniform(20, 35)

        self.ripples.append({
            'x': x,
            'y': y,
            'radius': size,
            'max_radius': max_radius,
            'duration': duration,
            'age': 0,
            'color': WATER_HIGHLIGHT
        })

    def update(self, dt):

        for ripple in self.ripples[:]:
            ripple['age'] += dt

            progress = ripple['age'] / ripple['duration']

            ripple['radius'] = ripple['max_radius'] * progress

            if ripple['age'] >= ripple['duration']:
                self.ripples.remove(ripple)

    def draw(self, screen, camera):
        if not camera:
            return

        for ripple in self.ripples:

            alpha = int(255 * (1 - ripple['age'] / ripple['duration']))

            screen_x, screen_y = camera.apply_pos((ripple['x'], ripple['y']))

            surf = pygame.Surface((ripple['radius'] * 2, ripple['radius'] * 2), pygame.SRCALPHA)

            color_with_alpha = (*ripple['color'][:3], alpha)
            pygame.draw.circle(surf, color_with_alpha, (ripple['radius'], ripple['radius']), ripple['radius'], 1)

            screen.blit(surf, (screen_x - ripple['radius'], screen_y - ripple['radius']))
