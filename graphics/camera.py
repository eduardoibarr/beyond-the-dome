import pygame
from settings import WIDTH, HEIGHT, TILE_SIZE, CAMERA_LERP_FACTOR

# --- Constantes ---
# CAMERA_LERP_FACTOR = 0.08  # Quão rápido a câmera segue o jogador (menor = mais suave)

class Camera:
    """
    Manages the scrolling camera view. Tracks a position and applies offsets to entities.
    """
    def __init__(self, map_width, map_height):
        """
        Initializes the camera with the map dimensions.
        
        Args:
            map_width (int): Total width of the game map in pixels.
            map_height (int): Total height of the game map in pixels.
        """
        self.camera = pygame.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height
        
        # Float camera position for smooth movement
        self.x = 0.0
        self.y = 0.0

    def apply(self, entity):
        """
        Applies the camera offset to an entity or rect.
        
        Args:
            entity: A pygame.sprite.Sprite or pygame.Rect object.
            
        Returns:
            pygame.Rect: The entity's rectangle adjusted for camera offset.
        """
        # Use the integer part of the camera's float position for applying offset
        offset_x = int(self.x)
        offset_y = int(self.y)

        # Handle both sprite objects and rect objects
        if hasattr(entity, 'rect'):
            return entity.rect.move(offset_x, offset_y)
        else:  # Assume it's already a Rect
            return entity.move(offset_x, offset_y)

    def update(self, target):
        """
        Updates the camera's position smoothly to keep the target centered.
        
        Args:
            target (pygame.sprite.Sprite): The sprite the camera should follow (usually the player).
        """
        # Calculate the desired top-left corner of the camera view (target position)
        # We want the target's center to be at the screen's center
        target_x = -target.rect.centerx + WIDTH // 2
        target_y = -target.rect.centery + HEIGHT // 2

        # --- Smooth Interpolation (Lerp) ---
        # Move the camera's float position towards the target position
        self.x += (target_x - self.x) * CAMERA_LERP_FACTOR
        self.y += (target_y - self.y) * CAMERA_LERP_FACTOR

        # --- Clamping ---
        # Clamp the *float* camera coordinates to prevent showing areas outside the map
        self.x = min(0.0, self.x)  # Don't scroll past the left edge (x=0)
        self.y = min(0.0, self.y)  # Don't scroll past the top edge (y=0)
        self.x = max(-(self.map_width - WIDTH), self.x)  # Don't scroll past the right edge
        self.y = max(-(self.map_height - HEIGHT), self.y)  # Don't scroll past the bottom edge

        # Update the actual camera Rect used for applying offsets (using integer part)
        self.camera.x = int(self.x)
        self.camera.y = int(self.y)

    def screen_to_world(self, screen_pos):
        """
        Converts screen coordinates to world coordinates.
        
        Args:
            screen_pos (tuple): The (x, y) screen coordinates to convert.
            
        Returns:
            tuple: The corresponding (x, y) world coordinates.
        """
        # Use the integer part of the camera's float position
        return (screen_pos[0] - int(self.x), screen_pos[1] - int(self.y))

    def apply_coords(self, x, y):
        """
        Converts world coordinates to screen coordinates.
        
        Args:
            x (int): The world x coordinate.
            y (int): The world y coordinate.
            
        Returns:
            tuple: The corresponding (x, y) screen coordinates.
        """
        # Use the integer part of the camera's float position
        return (x + int(self.x), y + int(self.y)) 