import pygame
import random
import math
from settings import *
from utils.drawing import draw_gradient_rect, draw_textured_rect, draw_crack

class Tile(pygame.sprite.Sprite):
    """Base class for all static map tiles."""
    def __init__(self, game, x, y, groups, kind='floor'):
        """
        Initializes a Tile sprite.
        Args:
            game: Reference to the main game object.
            x (int): Tile column index.
            y (int): Tile row index.
            groups (pygame.sprite.Group): Sprite group(s) to add this tile to.
            kind (str): The type of tile (e.g., 'floor', 'grass', 'wall').
        """
        self.groups = groups
        super().__init__(self.groups) # Initialize Sprite
        self.game = game
        self.kind = kind
        self.x = x * TILE_SIZE # World position in pixels
        self.y = y * TILE_SIZE # World position in pixels
        self.tile_x = x # Grid position
        self.tile_y = y # Grid position

        # Cache the generated image - generate only once
        self.image = self._create_tile_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def _create_tile_image(self):
        """
        Creates the pygame.Surface for the tile based on its kind and detail level.
        Returns:
            pygame.Surface: The rendered image for the tile.
        """
        # Create a surface with transparency support
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        width, height = TILE_SIZE, TILE_SIZE
        rect = surf.get_rect()

        # --- Grass Tile ---
        if self.kind == 'grass':
            # Base gradient
            draw_gradient_rect(surf, rect, GRASS_LIGHT, GRASS_COLOR)
            # Texture variations
            draw_textured_rect(surf, rect, GRASS_COLOR, GRASS_DARK, GRASS_LIGHT, density=40, point_size=(1, 3))
            # Leaf details (Detail Level 3+)
            if DETAIL_LEVEL >= 3:
                for _ in range(10):
                    x_start = random.randint(0, width - 1)
                    y_start = random.randint(height // 2, height - 1) # Start lower down
                    leaf_len = random.randint(3, 8)
                    angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2) # Point upwards mostly
                    end_x = x_start + math.cos(angle) * leaf_len
                    end_y = y_start + math.sin(angle) * leaf_len
                    # Clamp to bounds
                    end_x = max(0, min(width - 1, end_x))
                    end_y = max(0, min(height - 1, end_y))
                    pygame.draw.line(surf, GRASS_LIGHT, (x_start, y_start), (int(end_x), int(end_y)), 1)

        # --- Dirt Tile ---
        elif self.kind == 'dirt':
            # Base gradient
            draw_gradient_rect(surf, rect, DIRT_LIGHT, DIRT_COLOR)
            # Texture variations
            draw_textured_rect(surf, rect, DIRT_COLOR, DIRT_DARK, DIRT_LIGHT, density=50, point_size=(1, 4))
            # Pebbles (Detail Level 3+)
            if DETAIL_LEVEL >= 3:
                for _ in range(random.randint(3, 7)):
                    x_pos = random.randint(3, width - 4)
                    y_pos = random.randint(3, height - 4)
                    size = random.randint(2, 4)
                    # Randomize pebble color slightly
                    stone_color = (max(0, min(255, 150 + random.randint(-25, 25))),
                                   max(0, min(255, 150 + random.randint(-25, 25))),
                                   max(0, min(255, 150 + random.randint(-25, 25))))
                    stone_dark = (max(0, stone_color[0]-30), max(0, stone_color[1]-30), max(0, stone_color[2]-30))
                    # Simple shadow (if enabled)
                    if ENABLE_SHADOWS:
                         shadow_color = (*DIRT_DARK, 100) # Use alpha for transparency
                         shadow_offset_x = 1
                         shadow_offset_y = 1
                         pygame.draw.circle(surf, shadow_color, (x_pos + shadow_offset_x, y_pos + shadow_offset_y), size)
                    # Draw pebble with slight gradient/highlight
                    pygame.draw.circle(surf, stone_dark, (x_pos, y_pos), size)
                    pygame.draw.circle(surf, stone_color, (x_pos, y_pos-1), size-1) # Highlight top

        # --- Concrete Tile ---
        elif self.kind == 'concrete' or self.kind == 'concrete_oil_stain':
            # Base gradient
            draw_gradient_rect(surf, rect, CONCRETE_LIGHT, CONCRETE_COLOR)
            # Variations/Stains
            draw_textured_rect(surf, rect, CONCRETE_COLOR, CONCRETE_DARK, CONCRETE_LIGHT, density=45, point_size=(1, 5))
            # Cracks (Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                for _ in range(random.randint(0, 2)): # 0 to 2 cracks
                    start_x = random.randint(5, width - 6)
                    start_y = random.randint(5, height - 6)
                    crack_len = random.randint(width // 4, width * 2 // 3)
                    draw_crack(surf, (start_x, start_y), crack_len, CONCRETE_DARK, 1)
            # Expansion Joints (Detail Level 3+)
            if DETAIL_LEVEL >= 3 and random.random() < 0.15: # Less chance
                if random.random() < 0.5: # Horizontal
                    joint_y = random.randint(height // 4, 3 * height // 4)
                    pygame.draw.line(surf, CONCRETE_DARK, (0, joint_y), (width, joint_y), 2)
                    pygame.draw.line(surf, CONCRETE_LIGHT, (0, joint_y+1), (width, joint_y+1), 1) # Highlight below
                else: # Vertical
                    joint_x = random.randint(width // 4, 3 * width // 4)
                    pygame.draw.line(surf, CONCRETE_DARK, (joint_x, 0), (joint_x, height), 2)
                    pygame.draw.line(surf, CONCRETE_LIGHT, (joint_x+1, 0), (joint_x+1, height), 1) # Highlight right

            # Oil Stains (Applied visually if marked by generator)
            if self.kind == 'concrete_oil_stain':
                stain_radius = random.randint(width // 5, width // 2)
                stain_x = width // 2 + random.randint(-width//5, width//5)
                stain_y = height // 2 + random.randint(-height//5, height//5)
                # Draw multiple layers for a deeper stain effect
                for i in range(3):
                    r_outer = stain_radius * (1.0 - i*0.2)
                    r_inner = stain_radius * (0.6 - i*0.2)
                    alpha_outer = int(OIL_STAIN_COLOR[3] * 0.6 * (1.0 - i*0.3))
                    alpha_inner = int(OIL_STAIN_COLOR[3] * (1.0 - i*0.2))

                    for r in range(int(r_outer), 0, -1):
                        if r > r_inner: # Outer, fainter part
                            alpha = int(alpha_outer * ( (r - r_inner) / (r_outer - r_inner) )**0.5) # Fade out
                        else: # Inner, darker part
                            alpha = int(alpha_inner * (r / r_inner)**1.5) # Fade in towards center

                        alpha = max(0, min(255, alpha))
                        if alpha > 0:
                            pygame.draw.circle(surf, (*OIL_STAIN_COLOR[:3], alpha), (stain_x, stain_y), r)
        
        # --- Default/Unknown Tile ---
        else:
            surf.fill(RED) # Fill with red to indicate an unknown type
            pygame.draw.line(surf, WHITE, (0, 0), (width, height), 2)
            pygame.draw.line(surf, WHITE, (width, 0), (0, height), 2)
            # Try adding text for the unknown kind
            try:
                font = pygame.font.Font(None, TILE_SIZE // 2) # Basic font
                text_surf = font.render(f"{self.kind[:4]}?", True, WHITE)
                text_rect = text_surf.get_rect(center=rect.center)
                surf.blit(text_surf, text_rect)
            except Exception: # Ignore font errors
                pass

        return surf 