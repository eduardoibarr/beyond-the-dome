import pygame
import math
import random
from settings import *
from items.item import Item
from particles import ParticleSystem

class Ammo(Item):
    """
    Ammo pickup that gives player ammunition when collected.
    """
    def __init__(self, game, x, y, ammo_amount=20, ammo_type="standard", groups=None):
        """
        Initialize an ammo pickup.
        
        Args:
            game: Reference to the main game object
            x (int): X position in world coordinates
            y (int): Y position in world coordinates
            ammo_amount (int): Amount of ammo to give when collected
            ammo_type (str): Type of ammunition ("standard", "shotgun", etc.)
            groups (list): List of pygame.sprite.Group to add this sprite to
        """
        super().__init__(game, x, y, item_type='ammo', groups=groups)
        
        # Ammo properties
        self.ammo_amount = ammo_amount
        self.ammo_type = ammo_type
        
        # Visual properties
        self.color = (180, 180, 60)  # Yellow for ammo
        self.size = 12
        self.shadow_offset = 3
        
        # Set up animation properties
        self.rotate_speed = random.uniform(0.5, 1.5)
        self.rotation = random.uniform(0, 360)
        
        # Determine appearance based on ammo type
        if ammo_type == "shotgun":
            self.color = (200, 70, 20)  # Orange-red for shotgun shells
            self.shape = "shell"
        elif ammo_type == "energy":
            self.color = (20, 180, 240)  # Blue for energy ammo
            self.shape = "cell"
        elif ammo_type == "explosive":
            self.color = (200, 20, 20)  # Red for explosive ammo
            self.shape = "grenade"
        else:
            self.shape = "box"  # Default is box for standard ammo
    
    def _create_collection_particles(self):
        """Create particles when ammo is collected."""
        if not hasattr(self.game, 'particles'):
            return
            
        particle_count = min(30, max(15, int(self.ammo_amount * 0.5)))
        
        # Create particle system based on ammo type
        colors = []
        if self.ammo_type == "shotgun":
            colors = [(200, 100, 20), (220, 120, 40), (240, 140, 60)]
        elif self.ammo_type == "energy":
            colors = [(40, 120, 240), (60, 140, 255), (80, 160, 255)]
        elif self.ammo_type == "explosive":
            colors = [(200, 50, 50), (220, 70, 70), (240, 90, 90)]
        else:
            colors = [(180, 180, 40), (200, 200, 60), (220, 220, 80)]
        
        ammo_particles = ParticleSystem(
            position=(self.x, self.y),
            particle_count=particle_count,
            min_speed=20,
            max_speed=60,
            min_lifetime=0.3,
            max_lifetime=0.8,
            min_size=2,
            max_size=4,
            colors=colors,
            gravity=20,
            fade_out=True
        )
        
        self.game.particles.add(ammo_particles)
        
    def collect(self):
        """Collect the ammo and give it to the player."""
        if self.collected:
            return False
            
        if not hasattr(self.game, 'player'):
            return super().collect()
            
        # Give ammo to player if they exist
        player = self.game.player
        ammo_added = False
        
        # Try different methods based on player implementation
        if hasattr(player, 'add_ammo'):
            ammo_added = player.add_ammo(self.ammo_type, self.ammo_amount)
        elif hasattr(player, 'ammo') and isinstance(player.ammo, dict):
            # If player has an ammo dictionary, add to it
            if self.ammo_type not in player.ammo:
                player.ammo[self.ammo_type] = 0
            
            # Check for max ammo (if applicable)
            max_ammo = float('inf')
            if hasattr(player, 'max_ammo') and isinstance(player.max_ammo, dict):
                if self.ammo_type in player.max_ammo:
                    max_ammo = player.max_ammo[self.ammo_type]
            
            # Add ammo up to max
            old_ammo = player.ammo[self.ammo_type]
            player.ammo[self.ammo_type] = min(old_ammo + self.ammo_amount, max_ammo)
            ammo_added = player.ammo[self.ammo_type] > old_ammo
        
        # Only proceed if ammo was actually added
        if not ammo_added:
            return False
        
        # Create particles
        self._create_collection_particles()
        
        # Play pickup sound
        if hasattr(self.game, 'sounds') and 'ammo_pickup' in self.game.sounds:
            self.game.sounds['ammo_pickup'].play()
        
        # Update HUD
        if hasattr(self.game, 'hud'):
            self.game.hud.show_pickup(f"+{self.ammo_amount} {self.ammo_type.capitalize()} Ammo")
            
        return super().collect()
        
    def render(self, screen, camera):
        """
        Render the ammo with appropriate shape based on ammo_type.
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for calculating screen position
        """
        if self.collected:
            return
            
        # Calculate position with bobbing and rotation
        pos = camera.apply_point((self.x, self.y - self.bob_offset - self.bounce_height))
        
        # Update rotation
        self.rotation += self.rotate_speed
        
        # Draw shadow
        shadow_pos = (pos[0] + self.shadow_offset, pos[1] + self.shadow_offset)
        
        # Draw based on shape type
        if self.shape == "box":
            # Draw shadow
            pygame.draw.rect(
                screen,
                (20, 20, 20, 100),
                pygame.Rect(shadow_pos[0] - self.size//2, shadow_pos[1] - self.size//2, self.size, self.size),
                border_radius=2
            )
            
            # Draw box
            pygame.draw.rect(
                screen,
                self.color,
                pygame.Rect(pos[0] - self.size//2, pos[1] - self.size//2, self.size, self.size),
                border_radius=2
            )
            
            # Draw detail lines to indicate ammo box
            line_offset = self.size // 3
            pygame.draw.line(
                screen,
                (50, 50, 50),
                (pos[0] - line_offset, pos[1] - line_offset),
                (pos[0] + line_offset, pos[1] - line_offset),
                1
            )
            pygame.draw.line(
                screen,
                (50, 50, 50),
                (pos[0] - line_offset, pos[1]),
                (pos[0] + line_offset, pos[1]),
                1
            )
            pygame.draw.line(
                screen,
                (50, 50, 50),
                (pos[0] - line_offset, pos[1] + line_offset),
                (pos[0] + line_offset, pos[1] + line_offset),
                1
            )
            
        elif self.shape == "shell":
            # Draw a shotgun shell
            shell_width = self.size // 2
            shell_height = self.size
            
            # Draw shadow
            pygame.draw.rect(
                screen,
                (20, 20, 20, 100),
                pygame.Rect(
                    shadow_pos[0] - shell_width//2,
                    shadow_pos[1] - shell_height//2,
                    shell_width,
                    shell_height
                ),
                border_radius=1
            )
            
            # Draw shell body
            pygame.draw.rect(
                screen,
                self.color,
                pygame.Rect(
                    pos[0] - shell_width//2,
                    pos[1] - shell_height//2,
                    shell_width,
                    shell_height
                ),
                border_radius=1
            )
            
            # Draw shell primer (bottom)
            pygame.draw.rect(
                screen,
                (100, 100, 100),
                pygame.Rect(
                    pos[0] - shell_width//2,
                    pos[1] + shell_height//4,
                    shell_width,
                    shell_height//4
                ),
                border_radius=1
            )
            
        elif self.shape == "cell":
            # Draw an energy cell as a hexagon
            radius = self.size // 2
            points = []
            for i in range(6):
                angle = math.radians(self.rotation + i * 60)
                points.append((
                    pos[0] + int(radius * math.cos(angle)),
                    pos[1] + int(radius * math.sin(angle))
                ))
                
            # Draw shadow
            shadow_points = [(p[0] + self.shadow_offset, p[1] + self.shadow_offset) for p in points]
            pygame.draw.polygon(screen, (20, 20, 20, 100), shadow_points)
            
            # Draw cell
            pygame.draw.polygon(screen, self.color, points)
            
            # Draw center dot
            pygame.draw.circle(screen, (255, 255, 255), pos, radius // 3)
            
        elif self.shape == "grenade":
            # Draw grenade (circle with a top)
            radius = self.size // 2
            
            # Draw shadow
            pygame.draw.circle(screen, (20, 20, 20, 100), shadow_pos, radius)
            
            # Draw grenade body
            pygame.draw.circle(screen, self.color, pos, radius)
            
            # Draw top part
            top_height = radius // 2
            pygame.draw.rect(
                screen,
                (80, 80, 80),
                pygame.Rect(
                    pos[0] - radius//3,
                    pos[1] - radius - top_height,
                    radius//1.5,
                    top_height
                ),
                border_radius=1
            )
            
            # Draw highlight
            pygame.draw.circle(screen, (255, 255, 255, 150), 
                              (pos[0] - radius//3, pos[1] - radius//3), 
                              radius//4)
        
        # Draw outline for all shapes
        if self.shape == "box":
            pygame.draw.rect(
                screen,
                (50, 50, 50),
                pygame.Rect(pos[0] - self.size//2, pos[1] - self.size//2, self.size, self.size),
                width=1,
                border_radius=2
            )
        elif self.shape == "shell":
            shell_width = self.size // 2
            shell_height = self.size
            pygame.draw.rect(
                screen,
                (50, 50, 50),
                pygame.Rect(
                    pos[0] - shell_width//2,
                    pos[1] - shell_height//2,
                    shell_width,
                    shell_height
                ),
                width=1,
                border_radius=1
            )
        elif self.shape == "cell":
            radius = self.size // 2
            points = []
            for i in range(6):
                angle = math.radians(self.rotation + i * 60)
                points.append((
                    pos[0] + int(radius * math.cos(angle)),
                    pos[1] + int(radius * math.sin(angle))
                ))
            pygame.draw.polygon(screen, (50, 50, 50), points, width=1)
        elif self.shape == "grenade":
            pygame.draw.circle(screen, (50, 50, 50), pos, self.size // 2, width=1) 