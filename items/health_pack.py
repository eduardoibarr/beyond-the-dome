import pygame
import math
from settings import *
from items.item import Item
from particles import ParticleSystem

class HealthPack(Item):
    """
    Health pack item that restores player health when collected.
    Displays as a red cross with a pulsing glow effect.
    """
    def __init__(self, game, x, y, health_amount=25, groups=None):
        """
        Initialize a health pack.
        
        Args:
            game: Reference to the main game object
            x (int): X position in world coordinates
            y (int): Y position in world coordinates
            health_amount (int): Amount of health to restore when collected
            groups (list): List of pygame.sprite.Group to add this sprite to
        """
        super().__init__(game, x, y, item_type='health', groups=groups)
        
        # Health pack properties
        self.health_amount = health_amount
        
        # Visual properties
        self.color = (220, 50, 50)  # Red for health
        self.glow_color = (255, 100, 100, 100)  # Semi-transparent red
        self.size = 14  # Base size of health pack
        self.glow_size = 28  # Size of glow effect
        self.pulse_rate = 2.0  # Pulse rate in Hz
        
        # Calculate cross dimensions based on size
        self.cross_width = int(self.size * 0.8)
        self.cross_height = int(self.size * 0.8)
        self.cross_thickness = max(3, int(self.size * 0.2))
    
    def _create_healing_particles(self):
        """
        Create healing particles based on amount of health restored.
        """
        if not hasattr(self.game, 'particles'):
            return
            
        # Calculate number of particles based on health amount
        particle_count = min(50, max(20, int(self.health_amount * 0.8)))
        
        # Create particle system for healing effect
        healing_particles = ParticleSystem(
            position=(self.x, self.y),
            particle_count=particle_count,
            min_speed=10,
            max_speed=40,
            min_lifetime=0.5,
            max_lifetime=1.2,
            min_size=2,
            max_size=6,
            colors=[(255, 100, 100), (255, 150, 150), (255, 200, 200)],
            gravity=-50,  # Particles float upward
            fade_out=True
        )
        
        self.game.particles.add(healing_particles)
        
    def collect(self):
        """
        Collect the health pack and restore player health.
        """
        if self.collected:
            return False
            
        if not hasattr(self.game, 'player'):
            return super().collect()
            
        # Calculate health to restore (prevent overhealing)
        player = self.game.player
        current_health = player.health if hasattr(player, 'health') else 0
        max_health = player.max_health if hasattr(player, 'max_health') else 100
        health_needed = max_health - current_health
        health_to_restore = min(self.health_amount, health_needed)
        
        # Only collect if player needs health
        if health_to_restore <= 0:
            return False
            
        # Restore health
        if hasattr(player, 'add_health'):
            player.add_health(health_to_restore)
        elif hasattr(player, 'health'):
            player.health = min(player.health + health_to_restore, max_health)
        
        # Create healing particles effect
        self._create_healing_particles()
        
        # Play healing sound
        if hasattr(self.game, 'sounds') and 'heal' in self.game.sounds:
            self.game.sounds['heal'].play()
        
        # Update HUD with healing amount
        if hasattr(self.game, 'hud'):
            self.game.hud.show_healing(health_to_restore)
            
        return super().collect()
        
    def render(self, screen, camera):
        """
        Render the health pack with glowing effect.
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for calculating screen position
        """
        if self.collected:
            return
            
        # Calculate position with bobbing
        pos = camera.apply_point((self.x, self.y - self.bob_offset - self.bounce_height))
        
        # Calculate pulse scale based on time
        pulse = 0.2 * math.sin(self.age * self.pulse_rate * math.pi * 2) + 1.0
        
        # Draw glow effect (if supported)
        try:
            # Create a surface for the glow with per-pixel alpha
            glow_size = int(self.glow_size * pulse)
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # Draw radial gradient
            for radius in range(glow_size, 0, -1):
                alpha = int(100 * (radius / glow_size))
                pygame.draw.circle(
                    glow_surf, 
                    (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha),
                    (glow_size, glow_size),
                    radius
                )
                
            # Draw glow on screen
            screen.blit(glow_surf, (pos[0] - glow_size, pos[1] - glow_size))
        except:
            # Fallback if alpha blending not supported
            pygame.draw.circle(
                screen,
                self.glow_color[:3],
                pos,
                int(self.glow_size * pulse * 0.5)
            )
        
        # Draw health pack cross
        cross_horizontal = pygame.Rect(
            pos[0] - self.cross_width // 2,
            pos[1] - self.cross_thickness // 2,
            self.cross_width,
            self.cross_thickness
        )
        
        cross_vertical = pygame.Rect(
            pos[0] - self.cross_thickness // 2,
            pos[1] - self.cross_height // 2,
            self.cross_thickness,
            self.cross_height
        )
        
        # Draw the cross
        pygame.draw.rect(screen, self.color, cross_horizontal)
        pygame.draw.rect(screen, self.color, cross_vertical)
        
        # Draw highlight
        pygame.draw.rect(screen, (255, 255, 255), cross_horizontal, width=1)
        pygame.draw.rect(screen, (255, 255, 255), cross_vertical, width=1) 