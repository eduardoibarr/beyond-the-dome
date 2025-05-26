import pygame
import random
import math
from core.settings import *
from entities.tile import Tile
from utils.drawing import draw_gradient_rect

class RadioactiveZone(Tile):
    def __init__(self, game, x, y, groups, asset_key=None):
        super().__init__(game, x, y, groups, 'radioactive', asset_key)

        if hasattr(game, 'radioactive_zones') and isinstance(game.radioactive_zones, pygame.sprite.Group):
            game.radioactive_zones.add(self)
        else:
            print(f"Aviso: Objeto do jogo faltando ou com grupo 'radioactive_zones' inválido ao criar RadioactiveZone em ({x},{y})")

        if hasattr(game, 'particle_systems'):

            if hasattr(game.particle_systems, 'radioactive'):
                game.particle_systems.radioactive.register_zone(self)

                game.particle_systems.radioactive.add_particles(
                    self.rect.centerx, self.rect.centery, count=3, parent_zone=self
                )

            if hasattr(game.particle_systems, 'radioactive_fog'):
                game.particle_systems.radioactive_fog.register_zone(self)

                game.particle_systems.radioactive_fog.add_fog_clouds(
                    self.rect.centerx, self.rect.centery,
                    count=4,
                    radius=TILE_SIZE*0.8,
                    parent_zone=self
                )

    def _create_tile_image(self):

        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

        base_color_with_alpha = (*RADIOACTIVE_BASE, 40)
        light_color_with_alpha = (*RADIOACTIVE_BASE_LIGHT, 70)

        rect = surf.get_rect()
        draw_gradient_rect(surf, rect, light_color_with_alpha, base_color_with_alpha)

        symbol_radius = TILE_SIZE // 3
        symbol_center = (TILE_SIZE // 2, TILE_SIZE // 2)

        for angle in range(0, 360, 120):
            rad_angle = math.radians(angle)
            end_x = symbol_center[0] + math.cos(rad_angle) * symbol_radius
            end_y = symbol_center[1] + math.sin(rad_angle) * symbol_radius
            pygame.draw.line(surf, RADIOACTIVE_SYMBOL, symbol_center, (end_x, end_y), 2)

        pygame.draw.circle(surf, RADIOACTIVE_SYMBOL, symbol_center, symbol_radius // 3)

        return surf

    def update(self, dt):

        if hasattr(self.game, 'player') and self.rect.colliderect(self.game.player.rect):

            pass

    def kill(self):

        if hasattr(self.game, 'particle_systems'):

            if hasattr(self.game.particle_systems, 'radioactive'):
                self.game.particle_systems.radioactive.unregister_zone(self)

            if hasattr(self.game.particle_systems, 'radioactive_fog'):
                self.game.particle_systems.radioactive_fog.unregister_zone(self)

        super().kill()
