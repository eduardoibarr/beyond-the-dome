from entities.tile import Tile
import pygame
import random
import math
from settings import (
    TILE_SIZE, DETAIL_LEVEL,
    METAL_COLOR, METAL_DARK, METAL_LIGHT, METAL_RUST, # Wall/Barrier
    BLACK, YELLOW, DARKGREY, # Barrier
    TREE_TRUNK, TREE_TRUNK_DARK, TREE_TRUNK_LIGHT, # Tree Trunk
    TREE_LEAVES_DARK, TREE_LEAVES_LIGHT, # Tree Leaves
    BUILDING_COLOR, BUILDING_DARK, BUILDING_LIGHT, # Building
    WATER_COLOR, WATER_HIGHLIGHT # Water
    # Add other necessary constants like WATER_*, etc., if used elsewhere in Obstacle
)
from utils.drawing import draw_gradient_rect, draw_textured_rect, draw_crack

class Obstacle(Tile):
    """
    Class for tiles that act as obstacles and block movement.
    Inherits from Tile. Adds itself to the game's obstacle group.
    """
    def __init__(self, game, x, y, groups, kind='wall'):
        """
        Initializes an Obstacle tile.
        Args:
            game: Reference to the main game object.
            x (int): Tile column index.
            y (int): Tile row index.
            groups (pygame.sprite.Group): Sprite group(s) to add this tile to.
            kind (str): The type of obstacle tile.
        """
        # Initialize the Tile part
        super().__init__(game, x, y, groups, kind)
        # Add this sprite to the game's obstacle group for collision detection
        if hasattr(game, 'obstacles') and isinstance(game.obstacles, pygame.sprite.Group):
            game.obstacles.add(self)
        else:
            print(f"Warning: Game object missing or has invalid 'obstacles' group when creating Obstacle {kind} at ({x},{y})")

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

        # --- Wall Tile (Industrial Metal) ---
        if self.kind == 'wall':
            # Base gradient
            draw_gradient_rect(surf, rect, METAL_LIGHT, METAL_COLOR)
            # Horizontal panels
            panel_height = max(4, height // 4)
            for i in range(panel_height, height, panel_height): # Draw lines between panels
                pygame.draw.line(surf, METAL_DARK, (0, i), (width, i), 2) # Main line
                pygame.draw.line(surf, METAL_LIGHT, (0, i+1), (width, i+1), 1) # Highlight below
            # Vertical seam (optional)
            if random.random() < 0.2:
                seam_x = width // 2 + random.randint(-width//8, width//8)
                pygame.draw.line(surf, METAL_DARK, (seam_x, 0), (seam_x, height), 1)

            # Rivets on edges (Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                rivet_spacing = max(6, TILE_SIZE // 4)
                rivet_size = max(1, TILE_SIZE // 16)
                highlight_size = max(1, rivet_size // 2)
                offset = 3
                for i in range(rivet_spacing // 2, height, rivet_spacing):
                     # Left rivets
                     pygame.draw.circle(surf, METAL_DARK, (offset, i), rivet_size)
                     if DETAIL_LEVEL >= 3: pygame.draw.circle(surf, METAL_LIGHT, (offset - 1, i - 1), highlight_size)
                     # Right rivets
                     pygame.draw.circle(surf, METAL_DARK, (width - offset, i), rivet_size)
                     if DETAIL_LEVEL >= 3: pygame.draw.circle(surf, METAL_LIGHT, (width - offset - 1, i - 1), highlight_size)

            # Rust stains (Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                for _ in range(random.randint(1, 4)):
                    rust_x = random.randint(6, width - 7)
                    rust_y = random.randint(6, height - 7)
                    rust_size = random.randint(max(3, TILE_SIZE // 8), max(6, TILE_SIZE // 4))
                    # Draw rust stain with decreasing alpha towards edges
                    for r in range(rust_size, 0, -1):
                        alpha = int(180 * (r / rust_size)**1.8) # More intense in center, sharper falloff
                        alpha = max(0, min(255, alpha))
                        if alpha > 0:
                            pygame.draw.circle(surf, (*METAL_RUST, alpha), (rust_x, rust_y), r)

        # --- Barrier Tile ---
        elif self.kind == 'barrier':
            surf.fill(DARKGREY) # Base color
            # Diagonal yellow/black stripes
            stripe_width = max(6, TILE_SIZE // 4) # Visual width of the stripe
            num_stripes = (width + height) // stripe_width * 2 # Estimate needed stripes
            for i in range(-num_stripes // 2, num_stripes // 2):
                stripe_color = YELLOW if i % 2 == 0 else BLACK
                # Define points for a diagonal polygon stripe
                p1 = (i * stripe_width, 0)
                p2 = ((i + 1) * stripe_width, 0)
                p3 = ((i - 1) * stripe_width + width, height) # Adjusted for better coverage
                p4 = ((i - 2) * stripe_width + width, height) # Adjusted for better coverage
                pygame.draw.polygon(surf, stripe_color, [p1, p2, p3, p4])
            # Metal edges with gradient
            edge_rect_top = pygame.Rect(0, 0, width, 3)
            edge_rect_bottom = pygame.Rect(0, height - 3, width, 3)
            draw_gradient_rect(surf, edge_rect_top, METAL_LIGHT, METAL_COLOR)
            draw_gradient_rect(surf, edge_rect_bottom, METAL_COLOR, METAL_DARK)
            # Decorative rivets (Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                rivet_size = max(1, TILE_SIZE // 16)
                for i in range(stripe_width // 2, height, stripe_width * 2): # Fewer rivets
                    pygame.draw.circle(surf, METAL_DARK, (3, i), rivet_size)
                    pygame.draw.circle(surf, METAL_DARK, (width - 3, i), rivet_size)

        # --- Tree Tile ---
        elif self.kind == 'tree':
            surf.fill((0, 0, 0, 0)) # Transparent background
            # Trunk
            trunk_width = max(4, width // 5)
            trunk_height = height
            trunk_x = (width - trunk_width) // 2
            trunk_rect = pygame.Rect(trunk_x, 0, trunk_width, trunk_height)
            # Trunk gradient and texture
            draw_gradient_rect(surf, trunk_rect, TREE_TRUNK_LIGHT, TREE_TRUNK)
            if DETAIL_LEVEL >= 2:
                draw_textured_rect(surf, trunk_rect, TREE_TRUNK, TREE_TRUNK_DARK, TREE_TRUNK_LIGHT, density=15, point_size=(1,2))
                # Vertical lines for bark
                for i in range(trunk_width // 3):
                     line_x = trunk_x + random.randint(1, trunk_width - 2)
                     pygame.draw.line(surf, TREE_TRUNK_DARK, (line_x, 0), (line_x, height), 1)

            # Canopy (multiple layers for volume, irregular shape)
            canopy_center_x = width // 2
            canopy_base_y = height * 0.4
            base_radius = width // 2 + random.randint(-width//8, width//8)

            # Draw canopy layers from back to front with offsets
            num_layers = 3 if DETAIL_LEVEL >= 2 else 2
            leaf_colors = [TREE_LEAVES_DARK, TREE_LEAVES_LIGHT, TREE_LEAVES_DARK]

            for i in range(num_layers):
                layer_radius = int(base_radius * (1.0 - i * 0.2))
                layer_color = leaf_colors[i % len(leaf_colors)]
                offset_x = random.randint(-width//10, width//10)
                offset_y = random.randint(-height//10, height//10) - i * 3
                center = (canopy_center_x + offset_x, int(canopy_base_y + offset_y))

                # Draw multiple circles per layer for irregular shape
                num_blobs = random.randint(5, 10)
                for _ in range(num_blobs):
                    blob_radius = random.randint(layer_radius // 2, layer_radius)
                    blob_offset_x = random.randint(-layer_radius//3, layer_radius//3)
                    blob_offset_y = random.randint(-layer_radius//3, layer_radius//3)
                    blob_center = (center[0] + blob_offset_x, center[1] + blob_offset_y)
                    alpha_color = (*layer_color, 180 + random.randint(-20, 20))
                    pygame.draw.circle(surf, alpha_color, blob_center, blob_radius)

            # Leaf highlights (Detail Level 3+)
            if DETAIL_LEVEL >= 3:
                for _ in range(15):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(0, base_radius * 0.8)
                    detail_x = int(canopy_center_x + dist * math.cos(angle))
                    detail_y = int(canopy_base_y + dist * math.sin(angle) * 0.7)
                    detail_color = (*TREE_LEAVES_LIGHT, 200)
                    pygame.draw.circle(surf, detail_color, (detail_x, detail_y), random.randint(1, 2))

        # --- Building Tile (Industrial/Urban Brick/Concrete) ---
        elif self.kind == 'building':
            # Base gradient
            draw_gradient_rect(surf, rect, BUILDING_LIGHT, BUILDING_COLOR)
            # Brick/Panel pattern (Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                brick_h = max(4, TILE_SIZE // 6)
                brick_w = max(8, TILE_SIZE // 3)
                mortar_color = BUILDING_DARK
                for y_row in range(0, height, brick_h):
                    # Draw horizontal mortar lines
                    pygame.draw.line(surf, mortar_color, (0, y_row), (width, y_row), 1)
                    # Draw vertical mortar lines (offset every other row)
                    offset = (y_row // brick_h) % 2 * (brick_w // 2)
                    for x_col in range(-offset, width + brick_w, brick_w): # Extend range slightly
                        pygame.draw.line(surf, mortar_color, (x_col + offset, y_row), (x_col + offset, y_row + brick_h), 1)
                # Add subtle color variation to bricks
                if DETAIL_LEVEL >= 3:
                    for y_row in range(0, height, brick_h):
                         for x_col in range(0, width, brick_w):
                             if random.random() < 0.1:
                                 brick_rect = pygame.Rect(x_col+1, y_row+1, brick_w-2, brick_h-2)
                                 var_color = (max(0, BUILDING_COLOR[0]+random.randint(-10,10)),
                                              max(0, BUILDING_COLOR[1]+random.randint(-10,10)),
                                              max(0, BUILDING_COLOR[2]+random.randint(-10,10)),
                                              50) # Low alpha overlay
                                 pygame.draw.rect(surf, var_color, brick_rect)

            # Windows (Randomly placed, Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                if random.random() < 0.25: # Higher chance of window
                    win_w = random.randint(width // 4, width // 2)
                    win_h = random.randint(height // 4, height // 2)
                    win_x = random.randint(2, width - win_w - 3)
                    win_y = random.randint(2, height - win_h - 3)
                    win_rect = pygame.Rect(win_x, win_y, win_w, win_h)
                    # Window frame
                    pygame.draw.rect(surf, BUILDING_DARK, win_rect, 2)
                    # Glass pane (dark blue/grey)
                    glass_color = (40, 50, 60)
                    glare_color = (100, 110, 120, 100)
                    pygame.draw.rect(surf, glass_color, (win_x+1, win_y+1, win_w-2, win_h-2))
                    if DETAIL_LEVEL >= 3: # Glare
                        pygame.draw.line(surf, glare_color, (win_x+2, win_y+2), (win_x+win_w-3, win_y+win_h-3), 1)
                        pygame.draw.line(surf, glare_color, (win_x+win_w-3, win_y+2), (win_x+2, win_y+win_h-3), 1)

            # Door (Less frequent, Detail Level 2+)
            if DETAIL_LEVEL >= 2:
                 if random.random() < 0.1: # Lower chance for a door
                    door_w = max(6, width // 3)
                    door_h = max(10, height * 2 // 3)
                    # Ensure door is at bottom edge
                    door_x = random.randint(2, width - door_w - 3)
                    door_y = height - door_h - 1 # Align with bottom
                    door_rect = pygame.Rect(door_x, door_y, door_w, door_h)
                    # Door frame
                    pygame.draw.rect(surf, BUILDING_DARK, door_rect, 2)
                    # Door panel
                    door_panel_color = (BUILDING_DARK[0]+20, BUILDING_DARK[1]+20, BUILDING_DARK[2]+20)
                    pygame.draw.rect(surf, door_panel_color, (door_x+1, door_y+1, door_w-2, door_h-2))
                    if DETAIL_LEVEL >= 3: # Door knob
                        knob_x = door_x + door_w - 4
                        knob_y = door_y + door_h // 2
                        pygame.draw.circle(surf, METAL_COLOR, (knob_x, knob_y), max(1, TILE_SIZE // 16))
                        pygame.draw.circle(surf, METAL_LIGHT, (knob_x-1, knob_y-1), max(1, TILE_SIZE // 32))

            # Roof edge/details (Detail Level 3+)
            if DETAIL_LEVEL >= 3:
                pygame.draw.rect(surf, BUILDING_DARK, (0, 0, width, 3)) # Top edge shadow
                pygame.draw.rect(surf, BUILDING_LIGHT, (0, 1, width, 1)) # Top edge highlight

        # General code for other types of obstacles would be here
        # ...

        # --- Default/Unknown Tile ---
        else:
            # If not a specific obstacle kind, use the parent Tile's rendering
            return super()._create_tile_image()

        return surf

class Water(Obstacle):
    """
    Class for water tiles, which are also obstacles.
    Inherits from Obstacle (which inherits from Tile).
    """
    def __init__(self, game, x, y, groups):
        """
        Initializes a Water tile.
        Args:
            game: Reference to the main game object.
            x (int): Tile column index.
            y (int): Tile row index.
            groups (pygame.sprite.Group): Sprite group(s) to add this tile to.
        """
        super().__init__(game, x, y, groups, 'water')

    def _create_tile_image(self):
        """
        Creates the pygame.Surface for the water tile with animated effects.
        Returns:
            pygame.Surface: The rendered image for the water tile.
        """
        # Create a surface with transparency support
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        width, height = TILE_SIZE, TILE_SIZE
        rect = surf.get_rect()

        # Base gradient
        draw_gradient_rect(surf, rect, WATER_HIGHLIGHT, WATER_COLOR)
        
        # Waves/Ripples (Detail Level 2+)
        if DETAIL_LEVEL >= 2:
            center = (width // 2, height // 2)
            
            # Draw concentric circles for ripples
            for i in range(3):
                ripple_radius = (i + 1) * width // 6
                alpha = int(100 * (1 - i/3))  # Fade out
                ripple_color = (*WATER_HIGHLIGHT, alpha)
                pygame.draw.circle(surf, ripple_color, center, ripple_radius, 1)
            
            # Add random wave lines
            for _ in range(5):
                wave_y = random.randint(0, height)
                wave_amplitude = random.randint(1, 3)
                wave_length = random.randint(width // 4, width // 2)
                points = []
                for x in range(0, width + 1, 2):
                    y_offset = int(wave_amplitude * math.sin(x / wave_length * math.pi))
                    points.append((x, wave_y + y_offset))
                pygame.draw.lines(surf, WATER_HIGHLIGHT, False, points, 1)

        return surf 