import pygame
import math
from core.settings import *
from items.item import Item
from particles import ParticleSystem

class HealthPack(Item):
    """Pacote de saúde que restaura a vida do jogador quando coletado.
    É exibido como uma cruz vermelha com um efeito de brilho pulsante.
    """
    def __init__(self, game, x, y, health_amount=25, groups=None):
        """Inicializa um pacote de saúde.
        
        Argumentos:
            game: Referência para o objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            health_amount (int): Quantidade de vida para restaurar quando coletado
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        super().__init__(game, x, y, item_type='health', groups=groups)
        
        # Propriedades do pacote de saúde
        self.health_amount = health_amount
        
        # Visual properties
        self.color = (220, 50, 50)  # Red for health
        self.glow_color = (255, 100, 100, 100)  # Semi-transparent red
        self.size = 14  # Base size of health pack
        self.glow_size = 28  # Size of glow effect
        self.pulse_rate = 2.0  # Pulse rate in Hz
        
        # Calcula as dimensões da cruz com base no tamanho
        self.cross_width = int(self.size * 0.8)
        self.cross_height = int(self.size * 0.8)
        self.cross_thickness = max(3, int(self.size * 0.2))
    
    def _create_healing_particles(self):
        """Cria partículas de cura com base na quantidade de vida restaurada.
        """

        if not hasattr(self.game, 'particles'):
            return
            
        # Calculate number of particles based on health amount
        particle_count = min(50, max(20, int(self.health_amount * 0.8)))
        
        # Create particle system for healing effect
        particulas_de_cura = ParticleSystem(
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
        
        self.game.particles.add(particulas_de_cura)
        
    def collect(self):
        """Coleta o pacote de saúde e restaura a vida do jogador.
        """

        if self.collected:
            return False #Já foi coletado
            
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
        
        # Cria o efeito de partículas de cura
        self._create_healing_particles()
        
        # Toca o som de cura
        if hasattr(self.game, 'sounds') and 'heal' in self.game.sounds:
            self.game.sounds['heal'].play()
        
        # Atualiza o HUD com a quantidade de cura
        if hasattr(self.game, 'hud'):
            self.game.hud.show_healing(health_to_restore)
            
        return super().collect()
        
    def render(self, screen, camera):
        """Renderiza o pacote de saúde com efeito de brilho.
        
        Argumentos:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for calculating screen position
        """
        if self.collected:
            return
            
        # Calculate position with bobbing
        pos = camera.apply_point((self.x, self.y - self.bob_offset - self.bounce_height)) # calcula a posição com o balanço
        
        # Calcula a escala do pulso com base no tempo
        pulse = 0.2 * math.sin(self.age * self.pulse_rate * math.pi * 2) + 1.0
        
        # Draw glow effect (if supported)
        try:
            # Cria uma superfície para o brilho com alpha por pixel
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
                
            # Desenha o brilho na tela
            screen.blit(glow_surf, (pos[0] - glow_size, pos[1] - glow_size))
        except:
            # Alternativa se a mistura alfa não for suportada
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
        
        # Desenha a cruz
        pygame.draw.rect(screen, self.color, cross_horizontal)
        pygame.draw.rect(screen, self.color, cross_vertical)
        
        # Desenha o destaque
        pygame.draw.rect(screen, (255, 255, 255), cross_horizontal, width=1)
        pygame.draw.rect(screen, (255, 255, 255), cross_vertical, width=1) 