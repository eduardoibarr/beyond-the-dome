import pygame
import math
import random
from core.settings import *
from items.item import Item
# from graphics.particles import ParticleSystem # Comentado - Causa ImportError

class HealthPack(Item):
    """Pacote de saúde - Item de cura do jogo.
    
    Este item restaura a vida do jogador quando coletado. Possui características especiais:
    - Efeito visual de cruz vermelha com brilho pulsante
    - Sistema de partículas de cura ao ser coletado
    - Prevenção de cura excessiva (overhealing)
    - Feedback visual e sonoro ao coletar
    """
    def __init__(self, game, x, y, health_amount=25, groups=None):
        """Inicializa um pacote de saúde.
        
        Args:
            game: Referência para o objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            health_amount (int): Quantidade de vida para restaurar
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        super().__init__(game, x, y, item_type='health', groups=groups)
        
        # Propriedades de cura
        self.health_amount = health_amount
        
        # Propriedades visuais
        self.color = (220, 50, 50)  # Vermelho para o pacote de saúde
        self.glow_color = (255, 100, 100, 100)  # Vermelho semi-transparente para o brilho
        self.size = 14  # Tamanho base do pacote
        self.glow_size = 28  # Tamanho do efeito de brilho
        self.pulse_rate = 2.0  # Frequência da pulsação em Hz
        
        # Dimensões da cruz
        self.cross_width = int(self.size * 0.8)
        self.cross_height = int(self.size * 0.8)
        self.cross_thickness = max(3, int(self.size * 0.2))
    
    def _create_healing_particles(self):
        """Cria o sistema de partículas para o efeito de cura.
        
        O sistema de partículas:
        - Quantidade proporcional à cura fornecida
        - Movimento ascendente (gravidade negativa)
        - Cores em tons de vermelho
        - Efeito de fade out
        """
        if not hasattr(self.game, 'particles'):
            return
            
        particle_count = min(50, max(20, int(self.health_amount * 0.8)))
        
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
            gravity=-50,  # Partículas flutuam para cima
            fade_out=True
        )
        
        self.game.particles.add(particulas_de_cura)
        
    def collect(self):
        """Processa a coleta do pacote de saúde.
        
        Este método:
        1. Verifica se o jogador precisa de cura
        2. Calcula a quantidade de cura necessária
        3. Aplica a cura ao jogador
        4. Cria efeitos visuais e sonoros
        5. Atualiza o HUD
        
        Retorna:
            bool: True se o pacote foi coletado com sucesso, False caso contrário
        """
        if self.collected:
            return False
            
        if not hasattr(self.game, 'player'):
            return super().collect()
            
        # Calcula a cura necessária (previne overhealing)
        player = self.game.player
        current_health = player.health if hasattr(player, 'health') else 0
        max_health = player.max_health if hasattr(player, 'max_health') else 100
        health_needed = max_health - current_health
        health_to_restore = min(self.health_amount, health_needed)
        
        # Só coleta se o jogador precisar de cura
        if health_to_restore <= 0:
            return False
            
        # Aplica a cura
        if hasattr(player, 'add_health'):
            player.add_health(health_to_restore)
        elif hasattr(player, 'health'):
            player.health = min(player.health + health_to_restore, max_health)
        
        # Cria efeitos visuais e sonoros
        self._create_healing_particles()
        
        if hasattr(self.game, 'sounds') and 'heal' in self.game.sounds:
            self.game.sounds['heal'].play()
        
        if hasattr(self.game, 'hud'):
            self.game.hud.show_healing(health_to_restore)
            
        return super().collect()
        
    def render(self, screen, camera):
        """Renderiza o pacote de saúde com efeitos visuais.
        
        Implementa:
        1. Efeito de brilho pulsante
        2. Cruz vermelha com destaque
        3. Gradiente radial para o brilho
        4. Animação de flutuação
        
        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição na tela
        """
        if self.collected:
            return
            
        # Calcula a posição com animação de flutuação
        pos = camera.apply_point((self.x, self.y - self.bob_offset - self.bounce_height))
        
        # Calcula o efeito de pulsação
        pulse = 0.2 * math.sin(self.age * self.pulse_rate * math.pi * 2) + 1.0
        
        # Renderiza o efeito de brilho
        try:
            # Cria superfície para o brilho com canal alpha
            glow_size = int(self.glow_size * pulse) 
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # Desenha gradiente radial
            for radius in range(glow_size, 0, -1):
                alpha = int(100 * (radius / glow_size))
                pygame.draw.circle(
                    glow_surf, 
                    (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha),
                    (glow_size, glow_size),
                    radius
                )
                
            # Aplica o brilho na tela
            screen.blit(glow_surf, (pos[0] - glow_size, pos[1] - glow_size))
        except:
            # Fallback para sistemas sem suporte a alpha por pixel
            pygame.draw.circle(
                screen, 
                self.glow_color[:3],
                pos,
                int(self.glow_size * pulse * 0.5)
            )
        
        # Desenha a cruz do pacote de saúde
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
        
        # Renderiza a cruz principal
        pygame.draw.rect(screen, self.color, cross_horizontal)
        pygame.draw.rect(screen, self.color, cross_vertical)
        
        # Adiciona destaque à cruz
        pygame.draw.rect(screen, (255, 255, 255), cross_horizontal, width=1)
        pygame.draw.rect(screen, (255, 255, 255), cross_vertical, width=1) 