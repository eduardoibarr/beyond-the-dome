import pygame
import random
import math
from settings import *
from entities.tile import Tile
from utils.drawing import draw_gradient_rect

class RadioactiveZone(Tile):
    """
    Class for tiles representing radioactive zones.
    Inherits from Tile. Player takes radiation damage while inside.
    Adds itself to the game's radioactive zone group.
    """
    def __init__(self, game, x, y, groups):
        """
        Initializes a RadioactiveZone tile.
        Args:
            game: Reference to the main game object.
            x (int): Tile column index.
            y (int): Tile row index.
            groups (pygame.sprite.Group): Sprite group(s) to add this tile to.
        """
        super().__init__(game, x, y, groups, 'radioactive')
        # Add this sprite to the game's radioactive zone group
        if hasattr(game, 'radioactive_zones') and isinstance(game.radioactive_zones, pygame.sprite.Group):
            game.radioactive_zones.add(self)
        else:
            print(f"Warning: Game object missing or has invalid 'radioactive_zones' group when creating RadioactiveZone at ({x},{y})")
        
        # Registrar no sistema de partículas
        if hasattr(game, 'particle_systems') and hasattr(game.particle_systems, 'radioactive'):
            game.particle_systems.radioactive.register_zone(self)
            # Criar partículas iniciais nesta zona
            game.particle_systems.radioactive.add_particles(
                self.rect.centerx, self.rect.centery, count=8, parent_zone=self
            )
    
    def _create_tile_image(self):
        """
        Sobrescreve o método da classe base para criar uma névoa radioativa.
        Returns:
            pygame.Surface: The rendered image for the radioactive zone.
        """
        # Criar superfície com transparência
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base com gradiente mais transparente
        base_color_with_alpha = (*RADIOACTIVE_BASE, 70)  # Verde escuro com transparência
        light_color_with_alpha = (*RADIOACTIVE_BASE_LIGHT, 100)  # Verde mais claro com transparência
        
        # Retângulo base com gradiente
        rect = surf.get_rect()
        draw_gradient_rect(surf, rect, light_color_with_alpha, base_color_with_alpha)
        
        # Adicionar símmbolo de radioativo
        symbol_radius = TILE_SIZE // 3
        symbol_center = (TILE_SIZE // 2, TILE_SIZE // 2)
        
        # Desenhar o símbolo radioativo (três pás)
        for angle in range(0, 360, 120):
            rad_angle = math.radians(angle)
            end_x = symbol_center[0] + math.cos(rad_angle) * symbol_radius
            end_y = symbol_center[1] + math.sin(rad_angle) * symbol_radius
            pygame.draw.line(surf, RADIOACTIVE_SYMBOL, symbol_center, (end_x, end_y), 2)
        
        # Desenhar o círculo central
        pygame.draw.circle(surf, RADIOACTIVE_SYMBOL, symbol_center, symbol_radius // 3)
        
        # Adicionar névoa/fumaça
        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        for i in range(3):
            radius = TILE_SIZE // 2 - i * 4
            alpha = 100 - i * 20
            glow_color = (*RADIOACTIVE_GLOW, alpha)
            # Desenhar vários círculos com opacidade variável para criar efeito de névoa
            for _ in range(3):
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)
                size_var = random.randint(-2, 2)
                pygame.draw.circle(surf, glow_color, 
                                 (center[0] + offset_x, center[1] + offset_y), 
                                 radius + size_var)
        
        return surf
    
    def update(self, dt):
        """
        Updates the radioactive zone. Apply radiation effect to player if overlapping.
        Args:
            dt (float): Delta time in seconds.
        """
        # Opcional: Verificar sobreposição com o jogador para aplicar dano de radiação
        if hasattr(self.game, 'player') and self.rect.colliderect(self.game.player.rect):
            # Implementação de dano por radiação pode ser adicionada aqui
            pass
            
    def kill(self):
        """Remove a zona radioativa e desregistra do sistema de partículas."""
        # Desregistrar do sistema de partículas antes de remover
        if hasattr(self.game, 'particle_systems') and hasattr(self.game.particle_systems, 'radioactive'):
            self.game.particle_systems.radioactive.unregister_zone(self)
        super().kill()  # Chamar o método kill da classe base 