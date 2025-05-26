import pygame
import random
import math
from core.settings import *
from utils.drawing import draw_gradient_rect, draw_textured_rect, draw_crack

class Tile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, groups, kind='floor', asset_key=None):
        self.groups = groups
        super().__init__(self.groups)
        self.game = game
        self.kind = kind
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.tile_x = x
        self.tile_y = y
        self.asset_key = asset_key

        self.animation_timer = random.uniform(0, 2 * math.pi)

        if self.asset_key and hasattr(self.game, 'asset_manager'):

            try:
                self.image_base = self.game.asset_manager.get_image(self.asset_key).copy()

                if self.image_base.get_width() != TILE_SIZE or self.image_base.get_height() != TILE_SIZE:
                    self.image_base = pygame.transform.scale(self.image_base, (TILE_SIZE, TILE_SIZE))
            except Exception as e:
                print(f"Erro ao carregar asset {self.asset_key}: {e}")
                self.image_base = self._create_tile_image()
        else:

            self.image_base = self._create_tile_image()

        self.image = self.image_base.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def _create_tile_image(self):

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        width, height = TILE_SIZE, TILE_SIZE
        rect = surf.get_rect()

        if self.kind == 'grass':

            draw_gradient_rect(surf, rect, GRASS_LIGHT, GRASS_COLOR)

            draw_textured_rect(surf, rect, GRASS_COLOR, GRASS_DARK, GRASS_LIGHT, density=40, point_size=(1, 3))

            if DETAIL_LEVEL >= 3:
                for _ in range(10):
                    x_start = random.randint(0, width - 1)
                    y_start = random.randint(height // 2, height - 1)
                    leaf_len = random.randint(3, 8)
                    angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
                    end_x = x_start + math.cos(angle) * leaf_len
                    end_y = y_start + math.sin(angle) * leaf_len

                    end_x = max(0, min(width - 1, end_x))
                    end_y = max(0, min(height - 1, end_y))
                    pygame.draw.line(surf, GRASS_LIGHT, (x_start, y_start), (int(end_x), int(end_y)), 1)

        elif self.kind == 'dirt':

            draw_gradient_rect(surf, rect, DIRT_LIGHT, DIRT_COLOR)

            draw_textured_rect(surf, rect, DIRT_COLOR, DIRT_DARK, DIRT_LIGHT, density=50, point_size=(1, 4))

            if DETAIL_LEVEL >= 3:
                for _ in range(random.randint(3, 7)):
                    x_pos = random.randint(3, width - 4)
                    y_pos = random.randint(3, height - 4)
                    size = random.randint(2, 4)

                    stone_color = (max(0, min(255, 150 + random.randint(-25, 25))),
                                   max(0, min(255, 150 + random.randint(-25, 25))),
                                   max(0, min(255, 150 + random.randint(-25, 25))))
                    stone_dark = (max(0, stone_color[0]-30), max(0, stone_color[1]-30), max(0, stone_color[2]-30))

                    if ENABLE_SHADOWS:
                         shadow_color = (*DIRT_DARK, 100)
                         shadow_offset_x = 1
                         shadow_offset_y = 1
                         pygame.draw.circle(surf, shadow_color, (x_pos + shadow_offset_x, y_pos + shadow_offset_y), size)

                    pygame.draw.circle(surf, stone_dark, (x_pos, y_pos), size)
                    pygame.draw.circle(surf, stone_color, (x_pos, y_pos-1), size-1)

        elif self.kind == 'concrete' or self.kind == 'concrete_oil_stain':

            draw_gradient_rect(surf, rect, CONCRETE_LIGHT, CONCRETE_COLOR)

            draw_textured_rect(surf, rect, CONCRETE_COLOR, CONCRETE_DARK, CONCRETE_LIGHT, density=45, point_size=(1, 5))

            if DETAIL_LEVEL >= 2:
                for _ in range(random.randint(0, 2)):
                    start_x = random.randint(5, width - 6)
                    start_y = random.randint(5, height - 6)
                    crack_len = random.randint(width // 4, width * 2 // 3)
                    draw_crack(surf, (start_x, start_y), crack_len, CONCRETE_DARK, 1)

            if DETAIL_LEVEL >= 3 and random.random() < 0.15:
                if random.random() < 0.5:
                    joint_y = random.randint(height // 4, 3 * height // 4)
                    pygame.draw.line(surf, CONCRETE_DARK, (0, joint_y), (width, joint_y), 2)
                    pygame.draw.line(surf, CONCRETE_LIGHT, (0, joint_y+1), (width, joint_y+1), 1)
                else:
                    joint_x = random.randint(width // 4, 3 * width // 4)
                    pygame.draw.line(surf, CONCRETE_DARK, (joint_x, 0), (joint_x, height), 2)
                    pygame.draw.line(surf, CONCRETE_LIGHT, (joint_x+1, 0), (joint_x+1, height), 1)

            if self.kind == 'concrete_oil_stain':
                stain_radius = random.randint(width // 5, width // 2)
                stain_x = width // 2 + random.randint(-width//5, width//5)
                stain_y = height // 2 + random.randint(-height//5, height//5)

                for i in range(3):
                    r_outer = stain_radius * (1.0 - i*0.2)
                    r_inner = stain_radius * (0.6 - i*0.2)
                    alpha_outer = int(OIL_STAIN_COLOR[3] * 0.6 * (1.0 - i*0.3))
                    alpha_inner = int(OIL_STAIN_COLOR[3] * (1.0 - i*0.2))

                    for r in range(int(r_outer), 0, -1):
                        if r > r_inner:
                            alpha = int(alpha_outer * ( (r - r_inner) / (r_outer - r_inner) )**0.5)
                        else:
                            alpha = int(alpha_inner * (r / r_inner)**1.5)

                        alpha = max(0, min(255, alpha))
                        if alpha > 0:
                            pygame.draw.circle(surf, (*OIL_STAIN_COLOR[:3], alpha), (stain_x, stain_y), r)

        elif self.kind == 'water':

            draw_gradient_rect(surf, rect, WATER_HIGHLIGHT, WATER_COLOR)

            draw_textured_rect(surf, rect, WATER_COLOR, WATER_DARK, WATER_HIGHLIGHT, density=25, point_size=(1, 2))

        else:
            surf.fill(RED)
            pygame.draw.line(surf, WHITE, (0, 0), (width, height), 2)
            pygame.draw.line(surf, WHITE, (width, 0), (0, height), 2)

            try:
                font = pygame.font.Font(None, TILE_SIZE // 2)
                text_surf = font.render(f"{self.kind[:4]}?", True, WHITE)
                text_rect = text_surf.get_rect(center=rect.center)
                surf.blit(text_surf, text_rect)
            except Exception:
                pass

        return surf

    def update(self, dt):

        if self.kind == 'water' and not self.asset_key:

            self.animation_timer += dt * 1.5

            ripple = (math.sin(self.animation_timer + self.tile_x * 0.5 + self.tile_y * 0.3) + 1) / 2

            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            highlight_alpha = int(60 * ripple)
            dark_alpha = int(40 * (1 - ripple))

            overlay.fill((*WATER_HIGHLIGHT[:3], highlight_alpha), special_flags=pygame.BLEND_RGBA_ADD)
            overlay.fill((*WATER_DARK[:3], dark_alpha), special_flags=pygame.BLEND_RGBA_SUB)

            self.image = self.image_base.copy()
            self.image.blit(overlay, (0, 0))

        elif self.kind == 'water' and self.asset_key:

            self.animation_timer += dt * 1.5
            ripple = (math.sin(self.animation_timer + self.tile_x * 0.5 + self.tile_y * 0.3) + 1) / 2

            self.image = self.image_base.copy()

            highlight = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            highlight_color = (255, 255, 255, int(25 * ripple))
            highlight.fill(highlight_color, special_flags=pygame.BLEND_RGBA_ADD)
            self.image.blit(highlight, (0, 0))
