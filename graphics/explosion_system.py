import pygame
import random
import math
from core.settings import *

class ExplosionParticle:

    def __init__(self, x, y, explosion_type="normal"):
        self.x = x
        self.y = y
        self.explosion_type = explosion_type

        angle = random.uniform(0, 2 * math.pi)
        if explosion_type == "grenade":
            speed = random.uniform(50, 200)
            self.size = random.randint(2, 6)
            self.lifetime = random.uniform(0.5, 1.5)
        elif explosion_type == "fuel":
            speed = random.uniform(30, 150)
            self.size = random.randint(3, 8)
            self.lifetime = random.uniform(1.0, 2.5)
        else:
            speed = random.uniform(40, 180)
            self.size = random.randint(2, 5)
            self.lifetime = random.uniform(0.3, 1.2)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.age = 0.0
        self.gravity = random.uniform(20, 50)

        if explosion_type == "grenade":
            self.start_color = (255, 255, 100)
            self.end_color = (255, 100, 0)
        elif explosion_type == "fuel":
            self.start_color = (255, 150, 0)
            self.end_color = (150, 50, 0)
        else:
            self.start_color = (255, 200, 100)
            self.end_color = (200, 50, 0)

    def update(self, dt):
        self.age += dt

        self.vy += self.gravity * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        friction = 0.95
        self.vx *= friction
        self.vy *= friction

    def is_dead(self):
        return self.age >= self.lifetime

    def get_color(self):
        if self.lifetime <= 0:
            return self.end_color

        progress = min(1.0, self.age / self.lifetime)

        r = int(self.start_color[0] + (self.end_color[0] - self.start_color[0]) * progress)
        g = int(self.start_color[1] + (self.end_color[1] - self.start_color[1]) * progress)
        b = int(self.start_color[2] + (self.end_color[2] - self.start_color[2]) * progress)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def get_alpha(self):
        if self.lifetime <= 0:
            return 0

        progress = self.age / self.lifetime
        return int(255 * (1 - progress))

    def draw(self, screen, camera):
        alpha = self.get_alpha()
        if alpha <= 0:
            return

        screen_x, screen_y = camera.apply_pos((self.x, self.y))

        if (screen_x < -self.size or screen_x > WIDTH + self.size or
            screen_y < -self.size or screen_y > HEIGHT + self.size):
            return

        size = max(1, int(self.size * (1 - self.age / self.lifetime)))
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        color = self.get_color()
        color_with_alpha = (*color, alpha)

        pygame.draw.circle(surf, color_with_alpha, (size, size), size)
        screen.blit(surf, (screen_x - size, screen_y - size))

class ShockWave:

    def __init__(self, x, y, max_radius=100, duration=0.5, explosion_type="normal"):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.duration = duration
        self.age = 0.0
        self.explosion_type = explosion_type

        if explosion_type == "grenade":
            self.color = (255, 255, 150)
            self.thickness = 3
        elif explosion_type == "fuel":
            self.color = (255, 100, 0)
            self.thickness = 4
        else:
            self.color = (255, 200, 100)
            self.thickness = 2

    def update(self, dt):
        self.age += dt

    def is_dead(self):
        return self.age >= self.duration

    def get_radius(self):
        if self.duration <= 0:
            return self.max_radius

        progress = min(1.0, self.age / self.duration)
        return self.max_radius * progress

    def get_alpha(self):
        if self.duration <= 0:
            return 0

        progress = self.age / self.duration
        return int(255 * (1 - progress))

    def draw(self, screen, camera):
        alpha = self.get_alpha()
        if alpha <= 0:
            return

        radius = self.get_radius()
        if radius <= 0:
            return

        screen_x, screen_y = camera.apply_pos((self.x, self.y))

        if (screen_x + radius < 0 or screen_x - radius > WIDTH or
            screen_y + radius < 0 or screen_y - radius > HEIGHT):
            return

        surf_size = int(radius * 2 + self.thickness * 2)
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

        color_with_alpha = (*self.color, alpha)
        center = (surf_size // 2, surf_size // 2)

        pygame.draw.circle(surf, color_with_alpha, center, int(radius), self.thickness)

        screen.blit(surf, (screen_x - surf_size // 2, screen_y - surf_size // 2))

class ExplosionFlash:

    def __init__(self, x, y, max_radius=50, duration=0.2, explosion_type="normal"):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.duration = duration
        self.age = 0.0
        self.explosion_type = explosion_type

        if explosion_type == "grenade":
            self.color = (255, 255, 255)
        elif explosion_type == "fuel":
            self.color = (255, 200, 100)
        else:
            self.color = (255, 255, 200)

    def update(self, dt):
        self.age += dt

    def is_dead(self):
        return self.age >= self.duration

    def get_radius(self):
        if self.duration <= 0:
            return 0

        progress = self.age / self.duration

        if progress < 0.3:
            return self.max_radius * (progress / 0.3)
        else:
            return self.max_radius * (1 - (progress - 0.3) / 0.7)

    def get_alpha(self):
        if self.duration <= 0:
            return 0

        progress = self.age / self.duration
        return int(255 * (1 - progress))

    def draw(self, screen, camera):
        alpha = self.get_alpha()
        radius = self.get_radius()

        if alpha <= 0 or radius <= 0:
            return

        screen_x, screen_y = camera.apply_pos((self.x, self.y))

        if (screen_x + radius < 0 or screen_x - radius > WIDTH or
            screen_y + radius < 0 or screen_y - radius > HEIGHT):
            return

        surf_size = int(radius * 2)
        if surf_size <= 0:
            return

        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

        color_with_alpha = (*self.color, alpha)
        center = (surf_size // 2, surf_size // 2)

        pygame.draw.circle(surf, color_with_alpha, center, int(radius))

        screen.blit(surf, (screen_x - surf_size // 2, screen_y - surf_size // 2))

class Explosion:

    def __init__(self, x, y, explosion_type="normal", intensity=1.0):
        self.x = x
        self.y = y
        self.explosion_type = explosion_type
        self.intensity = intensity
        self.age = 0.0

        if explosion_type == "grenade":
            particle_count = int(30 * intensity)
            max_radius = int(80 * intensity)
            flash_radius = int(40 * intensity)
            self.duration = 2.0
        elif explosion_type == "fuel":
            particle_count = int(50 * intensity)
            max_radius = int(120 * intensity)
            flash_radius = int(60 * intensity)
            self.duration = 3.0
        else:
            particle_count = int(25 * intensity)
            max_radius = int(60 * intensity)
            flash_radius = int(30 * intensity)
            self.duration = 1.5

        self.particles = []
        for _ in range(particle_count):
            self.particles.append(ExplosionParticle(x, y, explosion_type))

        self.shock_wave = ShockWave(x, y, max_radius, 0.8, explosion_type)
        self.flash = ExplosionFlash(x, y, flash_radius, 0.3, explosion_type)

        self.secondary_explosions = []
        if explosion_type == "fuel":

            for _ in range(int(3 * intensity)):
                offset_x = random.uniform(-50, 50)
                offset_y = random.uniform(-50, 50)
                delay = random.uniform(0.2, 1.0)
                self.secondary_explosions.append({
                    'x': x + offset_x,
                    'y': y + offset_y,
                    'delay': delay,
                    'triggered': False,
                    'explosion': None
                })

    def update(self, dt):
        self.age += dt

        for particle in self.particles[:]:
            particle.update(dt)
            if particle.is_dead():
                self.particles.remove(particle)

        if self.shock_wave and not self.shock_wave.is_dead():
            self.shock_wave.update(dt)
        elif self.shock_wave:
            self.shock_wave = None

        if self.flash and not self.flash.is_dead():
            self.flash.update(dt)
        elif self.flash:
            self.flash = None

        for secondary in self.secondary_explosions:
            if not secondary['triggered'] and self.age >= secondary['delay']:
                secondary['triggered'] = True
                secondary['explosion'] = Explosion(
                    secondary['x'], secondary['y'],
                    "normal", 0.3
                )
            elif secondary['explosion']:
                secondary['explosion'].update(dt)

    def is_dead(self):
        if self.age < self.duration:
            return False

        if self.particles or self.shock_wave or self.flash:
            return False

        for secondary in self.secondary_explosions:
            if secondary['explosion'] and not secondary['explosion'].is_dead():
                return False

        return True

    def draw(self, screen, camera):

        if self.flash:
            self.flash.draw(screen, camera)

        for particle in self.particles:
            particle.draw(screen, camera)

        if self.shock_wave:
            self.shock_wave.draw(screen, camera)

        for secondary in self.secondary_explosions:
            if secondary['explosion']:
                secondary['explosion'].draw(screen, camera)

class ExplosionSystem:

    def __init__(self, game):
        self.game = game
        self.explosions = []

        self.explosion_sounds = {}

    def create_explosion(self, x, y, explosion_type="normal", intensity=1.0, play_sound=True):
        explosion = Explosion(x, y, explosion_type, intensity)
        self.explosions.append(explosion)

        if play_sound and hasattr(self.game, 'audio_manager'):
            sound_key = f"explosion_{explosion_type}"
            self.game.audio_manager.play(sound_key, volume=min(1.0, intensity))

        self._apply_area_damage(x, y, explosion_type, intensity)

        if hasattr(self.game, 'camera'):
            shake_intensity = min(20, int(10 * intensity))
            self.game.camera.add_shake(shake_intensity, 0.5)

        return explosion

    def _apply_area_damage(self, x, y, explosion_type, intensity):

        if explosion_type == "grenade":
            damage = int(50 * intensity)
            radius = int(80 * intensity)
        elif explosion_type == "fuel":
            damage = int(75 * intensity)
            radius = int(120 * intensity)
        else:
            damage = int(40 * intensity)
            radius = int(60 * intensity)

        if hasattr(self.game, 'entities'):
            for entity in self.game.entities:
                if hasattr(entity, 'take_damage') and hasattr(entity, 'x') and hasattr(entity, 'y'):
                    distance = math.sqrt((entity.x - x) ** 2 + (entity.y - y) ** 2)
                    if distance <= radius:

                        damage_factor = 1.0 - (distance / radius)
                        actual_damage = int(damage * damage_factor)
                        if actual_damage > 0:
                            entity.take_damage(actual_damage)

    def update(self, dt):
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if explosion.is_dead():
                self.explosions.remove(explosion)

    def draw(self, screen, camera):
        for explosion in self.explosions:
            explosion.draw(screen, camera)

    def clear_all(self):
        self.explosions.clear()

def create_grenade_explosion(explosion_system, x, y, intensity=1.0):
    return explosion_system.create_explosion(x, y, "grenade", intensity)

def create_fuel_explosion(explosion_system, x, y, intensity=1.0):
    return explosion_system.create_explosion(x, y, "fuel", intensity)

def create_impact_explosion(explosion_system, x, y, intensity=0.5):
    return explosion_system.create_explosion(x, y, "normal", intensity)
