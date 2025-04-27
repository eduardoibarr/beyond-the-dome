import pygame
import math
import random
from core.settings import *
from items.item import Item
from particles import ParticleSystem

class Ammo(Item):
    """Coletável de munição que fornece munição ao jogador quando coletado."""
    def __init__(self, game, x, y, ammo_amount=20, ammo_type="standard", groups=None):
        """Inicializa um coletável de munição.
        
        Parâmetros:
            game: Referência para o objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            ammo_amount (int): Quantidade de munição para fornecer quando coletado
            ammo_type (str): Tipo de munição ("standard", "shotgun", etc.)
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        super().__init__(game, x, y, item_type='ammo', groups=groups)
        
        # Propriedades da munição
        self.ammo_amount = ammo_amount
        self.ammo_type = ammo_type
        
        # Propriedades visuais
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
        """Cria partículas quando a munição é coletada."""
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
        
        # Tenta diferentes métodos com base na implementação do jogador
        if hasattr(player, 'add_ammo'):
            ammo_added = player.add_ammo(self.ammo_type, self.ammo_amount)
        elif hasattr(player, 'ammo') and isinstance(player.ammo, dict):
            # If player has an ammo dictionary, add to it
            if self.ammo_type not in player.ammo:
                player.ammo[self.ammo_type] = 0
            
            # Verifica a munição máxima (se aplicável)
            max_ammo = float('inf')
            if hasattr(player, 'max_ammo') and isinstance(player.max_ammo, dict):
                if self.ammo_type in player.max_ammo:
                    max_ammo = player.max_ammo[self.ammo_type]
            
            # Adiciona munição até o máximo
            old_ammo = player.ammo[self.ammo_type]
            player.ammo[self.ammo_type] = min(old_ammo + self.ammo_amount, max_ammo)
            ammo_added = player.ammo[self.ammo_type] > old_ammo

        # Só prossegue se a munição foi realmente adicionada
        if not ammo_added:
            return False
        
        # Cria partículas
        self._create_collection_particles()
        
        # Toca o som de coleta
        if hasattr(self.game, 'sounds') and 'ammo_pickup' in self.game.sounds:
            self.game.sounds['ammo_pickup'].play()
        
        # Update HUD
        if hasattr(self.game, 'hud'):
            self.game.hud.show_pickup(f"+{self.ammo_amount} {self.ammo_type.capitalize()} Ammo")
            
        return super().collect()
        
    def render(self, tela, camera):
        """Renderiza a munição com a forma apropriada com base no ammo_type.
        
        Parâmetros:
            tela (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição na tela
        """
        if self.collected:
            return
            
        # Calcula a posição com oscilação e rotação
        pos = camera.apply_point((self.x, self.y - self.bob_offset - self.bounce_height))
        # Atualiza a rotação
        self.rotation += self.rotate_speed
        
        # Desenha a sombra
        shadow_pos = (pos[0] + self.shadow_offset, pos[1] + self.shadow_offset)
        
        # Draw based on shape type
        if self.shape == "box":
            # Draw shadow
            pygame.draw.rect(
                screen,
                (20, 20, 20, 100), # Cor de sombra mais escura
                pygame.Rect(shadow_pos[0] - self.size//2, shadow_pos[1] - self.size//2, self.size, self.size),
                border_radius=2
            )
            
            # Desenha a caixa
            pygame.draw.rect(
                tela,
                self.color, # Cor da caixa
                pygame.Rect(pos[0] - self.size//2, pos[1] - self.size//2, self.size, self.size),
                border_radius=2
            )
            
            # Desenha linhas de detalhe para indicar a caixa de munição
            line_offset = self.size // 3
            pygame.draw.line(
                tela,
                (50, 50, 50), # Cor das linhas de detalhe
                (pos[0] - line_offset, pos[1] - line_offset),
                (pos[0] + line_offset, pos[1] - line_offset),
                1
            )
            pygame.draw.line(
                tela,
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
            # Desenha uma munição de espingarda
            shell_width = self.size // 2
            shell_height = self.size
            
            # Desenha a sombra
            pygame.draw.rect(
                screen,
                (20, 20, 20, 100), # Cor de sombra mais escura
                pygame.Rect(
                    shadow_pos[0] - shell_width//2,
                    shadow_pos[1] - shell_height//2,
                    shell_width,
                    shell_height
                ),
                border_radius=1 # Borda redonda
            )
            
            # Desenha o corpo da munição
            pygame.draw.rect(
                tela,
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
            # Desenha uma célula de energia como um hexágono
            radius = self.size // 2
            points = []
            for i in range(6): # Hexagono tem 6 lados
                angle = math.radians(self.rotation + i * 60)
                points.append((
                    pos[0] + int(radius * math.cos(angle)),
                    pos[1] + int(radius * math.sin(angle))
                ))
                
            # Draw shadow
            shadow_points = [(p[0] + self.shadow_offset, p[1] + self.shadow_offset) for p in points] # Pontos sombreados
            pygame.draw.polygon(screen, (20, 20, 20, 100), shadow_points)
            
            # Desenha a célula
            pygame.draw.polygon(tela, self.color, points)
            
            # Desenha o ponto central
            pygame.draw.circle(tela, (255, 255, 255), pos, radius // 3)
            
        elif self.shape == "grenade":
            # Desenha a granada (círculo com uma parte superior)
            radius = self.size // 2
            
            # Desenha a sombra
            pygame.draw.circle(screen, (20, 20, 20, 100), shadow_pos, radius)
            
            # Desenha o corpo da granada
            pygame.draw.circle(tela, self.color, pos, radius)
            
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
            
            # Desenha o destaque
            pygame.draw.circle(tela, (255, 255, 255, 150), 
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
                width=1, # Borda
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
            pygame.draw.polygon(tela, (50, 50, 50), points, width=1)
        elif self.shape == "grenade":
            pygame.draw.circle(tela, (50, 50, 50), pos, self.size // 2, width=1)