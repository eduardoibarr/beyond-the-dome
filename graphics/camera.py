import pygame
import random
import math
from core.settings import WIDTH, HEIGHT, CAMERA_LERP_FACTOR

class Camera:
    def __init__(self, map_width, map_height):
        self.camera = pygame.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height

        self.x = 0.0
        self.y = 0.0

        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def add_shake(self, intensity, duration):
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)
        self.shake_timer = self.shake_duration

    def update_shake(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt

            shake_factor = self.shake_timer / self.shake_duration if self.shake_duration > 0 else 0
            current_intensity = self.shake_intensity * shake_factor

            angle = random.uniform(0, 2 * math.pi)
            self.shake_offset_x = math.cos(angle) * current_intensity
            self.shake_offset_y = math.sin(angle) * current_intensity
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
            self.shake_intensity = 0.0
            self.shake_duration = 0.0

    def apply(self, entity):
        offset_x = int(self.x + self.shake_offset_x)
        offset_y = int(self.y + self.shake_offset_y)

        if hasattr(entity, 'rect'):
            return entity.rect.move(offset_x, offset_y)
        else:
            return entity.move(offset_x, offset_y)

    def apply_pos(self, pos):
        return (pos[0] + int(self.x + self.shake_offset_x),
                pos[1] + int(self.y + self.shake_offset_y))

    def update(self, target):

        self.update_shake(1/60)

        target_x = -target.rect.centerx + WIDTH // 2
        target_y = -target.rect.centery + HEIGHT // 2

        self.x += (target_x - self.x) * CAMERA_LERP_FACTOR
        self.y += (target_y - self.y) * CAMERA_LERP_FACTOR

        self.x = min(0.0, self.x)
        self.y = min(0.0, self.y)
        self.x = max(-(self.map_width - WIDTH), self.x)
        self.y = max(-(self.map_height - HEIGHT), self.y)

        self.camera.x = int(self.x)
        self.camera.y = int(self.y)

    def screen_to_world(self, screen_pos):
        return (screen_pos[0] - int(self.x + self.shake_offset_x),
                screen_pos[1] - int(self.y + self.shake_offset_y))

    def apply_coords(self, x, y):
        return (x + int(self.x + self.shake_offset_x),
                y + int(self.y + self.shake_offset_y))

    def is_rect_visible(self, rect):
        visible_area = pygame.Rect(-self.camera.x, -self.camera.y, WIDTH, HEIGHT)
        return rect.colliderect(visible_area)
