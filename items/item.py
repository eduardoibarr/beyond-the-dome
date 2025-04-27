import pygame
import math
from abc import ABC
from settings import *

class Item(pygame.sprite.Sprite, ABC):
    """
    Base class for all collectible items in the game.
    
    This is an abstract class that should be inherited by specific item types.
    """
    def __init__(self, game, x, y, item_type='generic', groups=None):
        """
        Initialize an item.
        
        Args:
            game: Reference to the main game object
            x (int): X position in world coordinates
            y (int): Y position in world coordinates
            item_type (str): Type of item for identification
            groups (list): List of pygame.sprite.Group to add this sprite to
        """
        # Call parent constructor with appropriate groups
        groups = groups or []
        if hasattr(game, 'items_group'):
            groups.append(game.items_group)
        if hasattr(game, 'all_sprites'):
            groups.append(game.all_sprites)
        super().__init__(*groups)
        
        # Store reference to game
        self.game = game
        
        # Set position
        self.x = x
        self.y = y
        self.z = 0  # For potential 3D effects or drawing order
        
        # Create rect for collision detection
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.hitbox = self.rect.copy()
        
        # Item properties
        self.item_type = item_type
        self.collected = False
        self.age = 0
        self.bob_offset = 0
        self.bob_direction = 1
        self.bob_height = 4
        self.bob_speed = 1.5
        
        # Whether item has been discovered (for filter modules)
        self.discovered = False
        
        # For drawing
        self.bounce_height = 0
        self.spawn_animation_time = 0.5
        self.spawn_time = 0
        
        # Setup any child components
        self.setup()
        
    def setup(self):
        """
        Override this in subclasses to set up item-specific components.
        """
        pass
    
    def update(self, dt):
        """
        Update item state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if self.collected:
            return
            
        # Update age
        self.age += dt
        
        # Bobbing animation
        self.bob_offset += self.bob_direction * self.bob_speed * dt
        if abs(self.bob_offset) >= self.bob_height:
            self.bob_direction *= -1
            self.bob_offset = self.bob_height if self.bob_offset > 0 else -self.bob_height
            
        # Handle spawn animation
        if self.age < self.spawn_animation_time:
            progress = self.age / self.spawn_animation_time
            self.bounce_height = 20 * (1 - progress) ** 2
        else:
            self.bounce_height = 0
            
        # Check proximity to player if player exists
        if hasattr(self.game, 'player') and not self.collected:
            # Calculate distance to player
            player_center = (
                self.game.player.rect.centerx,
                self.game.player.rect.centery
            )
            item_center = (self.rect.centerx, self.rect.centery)
            
            dx = player_center[0] - item_center[0]
            dy = player_center[1] - item_center[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Auto-collect if player is close enough
            if distance < ITEM_COLLECT_RADIUS:
                self.collect()
    
    def collect(self):
        """
        Mark the item as collected and trigger effects.
        Override in subclasses to add specific effects.
        """
        if self.collected:
            return False
            
        self.collected = True
        
        # Play generic pickup sound
        if hasattr(self.game, 'sounds') and 'pickup' in self.game.sounds:
            self.game.sounds['pickup'].play()
            
        # Add to inventory if it exists
        if hasattr(self.game, 'inventory'):
            self.game.inventory.add_item(self.item_type)
            
        return True
        
    def render(self, screen, camera):
        """
        Render the item on the screen.
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for calculating screen position
        """
        if self.collected:
            return
            
        # Calculate position with bobbing
        item_pos = camera.apply(pygame.Rect(
            self.x - 8,
            self.y - 8 - self.bob_offset - self.bounce_height,
            16, 16
        ))
        
        # Draw a simple shape representing the item
        pygame.draw.rect(screen, WHITE, item_pos)
        
        # Item specific rendering should be implemented in subclasses 