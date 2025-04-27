import pygame
import math
import random
# from settings import * # Replaced with explicit imports
from settings import (
    TILE_SIZE, ITEM_COLLECT_RADIUS, BLACK, WHITE, GREY, CYAN, LIGHTBLUE,
    DETAIL_LEVEL
    # Add other necessary constants from settings if used
)
from items.item import Item

class FilterModule(Item):
    """
    A filter module item that players collect to repair their dome's air filtration system.
    This is a key collectible in the game's main objective.
    """
    def __init__(self, game, x, y, groups=None):
        """
        Initialize a filter module item.
        
        Args:
            game: Reference to the main game object
            x (int): X position in world coordinates
            y (int): Y position in world coordinates
            groups (list): List of pygame.sprite.Group to add this sprite to
        """
        super().__init__(game, x, y, item_type='filter_module', groups=groups)
        
        # Special properties
        self.bob_height = 8  # Enhanced bobbing effect for important items
        self.bob_speed = 1.5
        self.pulse_rate = 0.8  # Controls how fast the item pulses
        self.glow_intensity = 0.8  # How bright the glow effect is
        
        # Gameplay properties
        self.module_id = random.randint(1000, 9999)  # Unique ID for this module
        self.discovered = False  # If this module has been detected on scanners
    
    def update(self, dt):
        """
        Update filter module's animation and behavior.
        
        Args:
            dt (float): Time since last frame in seconds
        """
        # Call the base class update for basic animations
        super().update(dt)
        
        # Check if player is nearby for a hint effect
        if not self.collected and hasattr(self.game, 'player'):
            player_dist = math.sqrt(
                (self.rect.centerx - self.game.player.rect.centerx) ** 2 +
                (self.rect.centery - self.game.player.rect.centery) ** 2
            )
            
            # If player is close enough, mark as discovered
            if player_dist < 300 and not self.discovered:
                self.discovered = True
                # Trigger scanner alert if game has a UI/HUD system
                if hasattr(self.game, 'hud'):
                    self.game.hud.show_message("Filter module detected nearby!")
                # Optional: Add a directional indicator to guide the player
    
    def render(self, screen, camera):
        """
        Render the filter module with enhanced effects.
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for calculating screen position
        """
        # Enhanced glow effect for filter modules
        if DETAIL_LEVEL >= 2 and not self.collected:
            # Pulse effect based on time
            pulse = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(self.age * self.pulse_rate * math.pi))
            
            # Outer glow
            glow_size = int(48 * pulse)
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Draw layered glows with decreasing opacity
            for i in range(3):
                alpha = int(60 * self.glow_intensity * (1 - i * 0.3) * pulse)
                size = int(glow_size * (1 - i * 0.25))
                glow_color = (*CYAN, alpha)
                
                pygame.draw.circle(
                    glow_surf, 
                    glow_color, 
                    (glow_size//2, glow_size//2), 
                    size//2
                )
            
            # Draw inner bright core
            core_size = int(16 * pulse)
            pygame.draw.circle(
                glow_surf,
                (*LIGHTBLUE, 120), 
                (glow_size//2, glow_size//2), 
                core_size//2
            )
            
            # Positioned on screen accounting for camera
            glow_rect = glow_surf.get_rect(center=camera.apply(self.rect).center)
            screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_ADD)
            
            # If player is close, draw a subtle connection line
            if self.discovered and hasattr(self.game, 'player'):
                player_dist = math.sqrt(
                    (self.rect.centerx - self.game.player.rect.centerx) ** 2 +
                    (self.rect.centery - self.game.player.rect.centery) ** 2
                )
                
                if player_dist < 300:
                    player_screen_pos = camera.apply(self.game.player).center
                    item_screen_pos = camera.apply(self).center
                    
                    # Calculate alpha based on distance (fainter when further)
                    alpha = int(150 * (1 - player_dist / 300))
                    line_color = (*CYAN, alpha)
                    
                    # Draw dashed line to item
                    dash_length = 5
                    gap_length = 3
                    dash_pattern = dash_length + gap_length
                    
                    # Calculate direction vector
                    dx = item_screen_pos[0] - player_screen_pos[0]
                    dy = item_screen_pos[1] - player_screen_pos[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance > 0:
                        dx, dy = dx / distance, dy / distance
                        
                        # Draw dashed line
                        steps = int(distance / dash_pattern)
                        for i in range(steps):
                            start_x = player_screen_pos[0] + dx * i * dash_pattern
                            start_y = player_screen_pos[1] + dy * i * dash_pattern
                            end_x = start_x + dx * dash_length
                            end_y = start_y + dy * dash_length
                            pygame.draw.line(screen, line_color, (start_x, start_y), (end_x, end_y), 1)
        
        # Call parent render method for basic effects
        super().render(screen, camera) 