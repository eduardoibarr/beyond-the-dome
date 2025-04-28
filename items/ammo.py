import pygame
import math
import random
from core.settings import *
from items.item import Item
# from graphics.particles import ParticleSystem # Comentado - Causa ImportError

class Ammo(Item):
    """Classe que implementa o sistema de munição do jogo.
    
    Esta classe gerencia diferentes tipos de munição que podem ser coletados pelo jogador:
    - Munição padrão (box): Caixas de munição convencional
    - Munição de espingarda (shell): Cartuchos de espingarda
    - Munição de energia (cell): Células de energia para armas futuristas
    - Munição explosiva (grenade): Granadas e munição explosiva
    
    Cada tipo tem sua própria aparência visual e efeitos de partículas quando coletado.
    """
    def __init__(self, game, x, y, ammo_amount=20, ammo_type="standard", groups=None):
        """Inicializa um coletável de munição.
        
        Parâmetros:
            game: Referência para o objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            ammo_amount (int): Quantidade de munição para fornecer quando coletado
            ammo_type (str): Tipo de munição ("standard", "shotgun", "energy", "explosive")
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        super().__init__(game, x, y, item_type='ammo', groups=groups)
        
        # Propriedades da munição
        self.ammo_amount = ammo_amount
        self.ammo_type = ammo_type
        
        # Propriedades visuais e de animação
        self.color = (180, 180, 60)  # Amarelo para munição padrão
        self.size = 12
        self.shadow_offset = 3
        self.rotate_speed = random.uniform(0.5, 1.5)
        self.rotation = random.uniform(0, 360)

        # Define a aparência baseada no tipo de munição
        if ammo_type == "shotgun":
            self.color = (200, 70, 20)  # Laranja-avermelhado para cartuchos
            self.shape = "shell"
        elif ammo_type == "energy":
            self.color = (20, 180, 240)  # Azul para células de energia
            self.shape = "cell"
        elif ammo_type == "explosive":
            self.color = (200, 20, 20)  # Vermelho para munição explosiva
            self.shape = "grenade"
        else:
            self.shape = "box"  # Caixa para munição padrão
    
    def _create_collection_particles(self):
        """Cria um sistema de partículas quando a munição é coletada.
        
        O sistema de partículas varia de acordo com o tipo de munição:
        - Munição padrão: Partículas amarelas
        - Cartuchos: Partículas laranja-avermelhadas
        - Células de energia: Partículas azuis
        - Munição explosiva: Partículas vermelhas
        
        A quantidade de partículas é proporcional à quantidade de munição coletada.
        """
        if not hasattr(self.game, 'particles'):
            return
            
        particle_count = min(30, max(15, int(self.ammo_amount * 0.5)))

        # Define as cores das partículas baseado no tipo de munição
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
        """Processa a coleta da munição pelo jogador.
        
        Este método:
        1. Verifica se o jogador pode receber mais munição
        2. Adiciona a munição ao inventário do jogador
        3. Cria efeitos visuais e sonoros
        4. Atualiza o HUD com a quantidade coletada
        
        Retorna:
            bool: True se a munição foi coletada com sucesso, False caso contrário
        """
        if self.collected:
            return False
            
        if not hasattr(self.game, 'player'):
            return super().collect()
            
        player = self.game.player
        ammo_added = False
        
        # Tenta diferentes métodos de adicionar munição baseado na implementação do jogador
        if hasattr(player, 'add_ammo'):
            ammo_added = player.add_ammo(self.ammo_type, self.ammo_amount)
        elif hasattr(player, 'ammo') and isinstance(player.ammo, dict):
            if self.ammo_type not in player.ammo:
                player.ammo[self.ammo_type] = 0
            
            # Verifica o limite máximo de munição
            max_ammo = float('inf')
            if hasattr(player, 'max_ammo') and isinstance(player.max_ammo, dict):
                if self.ammo_type in player.max_ammo:
                    max_ammo = player.max_ammo[self.ammo_type]
            
            old_ammo = player.ammo[self.ammo_type]
            player.ammo[self.ammo_type] = min(old_ammo + self.ammo_amount, max_ammo)
            ammo_added = player.ammo[self.ammo_type] > old_ammo

        if not ammo_added:
            return False
        
        # Cria efeitos visuais e sonoros
        self._create_collection_particles()
        
        if hasattr(self.game, 'sounds') and 'ammo_pickup' in self.game.sounds:
            self.game.sounds['ammo_pickup'].play()
        
        if hasattr(self.game, 'hud'):
            self.game.hud.show_pickup(f"+{self.ammo_amount} {self.ammo_type.capitalize()} Ammo")
            
        return super().collect()
        
    def render(self, tela, camera):
        """Renderiza a munição na tela com efeitos visuais.
        
        Este método implementa:
        1. Animação de flutuação e rotação
        2. Sombras dinâmicas
        3. Renderização específica para cada tipo de munição
        4. Efeitos visuais de destaque
        
        Parâmetros:
            tela (pygame.Surface): Superfície onde a munição será desenhada
            camera (Camera): Sistema de câmera para posicionamento correto na tela
        """
        if self.collected:
            return
            
        # Calcula a posição com efeitos de animação
        pos = camera.apply_point((self.x, self.y - self.bob_offset - self.bounce_height))
        self.rotation += self.rotate_speed
        
        # Desenha a sombra
        shadow_pos = (pos[0] + self.shadow_offset, pos[1] + self.shadow_offset)
        
        # Renderiza baseado no tipo de munição
        if self.shape == "box":
            # Desenha a sombra da caixa
            pygame.draw.rect(
                tela,
                (20, 20, 20, 100),
                pygame.Rect(shadow_pos[0] - self.size//2, shadow_pos[1] - self.size//2, self.size, self.size),
                border_radius=2
            )
            
            # Desenha a caixa de munição
            pygame.draw.rect(
                tela,
                self.color,
                pygame.Rect(pos[0] - self.size//2, pos[1] - self.size//2, self.size, self.size),
                border_radius=2
            )
            
            # Adiciona detalhes visuais para indicar o conteúdo
            line_offset = self.size // 3
            for y_offset in [-line_offset, 0, line_offset]:
                pygame.draw.line(
                    tela,
                    (50, 50, 50),
                    (pos[0] - line_offset, pos[1] + y_offset),
                    (pos[0] + line_offset, pos[1] + y_offset),
                    1
                )
            
        elif self.shape == "shell":
            # Desenha um cartucho de espingarda
            shell_width = self.size // 2
            shell_height = self.size
            
            # Sombra do cartucho
            pygame.draw.rect(
                tela,
                (20, 20, 20, 100),
                pygame.Rect(
                    shadow_pos[0] - shell_width//2,
                    shadow_pos[1] - shell_height//2,
                    shell_width,
                    shell_height
                ),
                border_radius=2
            )
            
            # Corpo do cartucho
            pygame.draw.rect(
                tela,
                self.color,
                pygame.Rect(
                    pos[0] - shell_width//2,
                    pos[1] - shell_height//2,
                    shell_width,
                    shell_height
                ),
                border_radius=2
            )
            
            # Base metálica do cartucho
            base_height = shell_height // 4
            pygame.draw.rect(
                tela,
                (100, 100, 100),
                pygame.Rect(
                    pos[0] - shell_width//2,
                    pos[1] + shell_height//2 - base_height,
                    shell_width,
                    base_height
                ),
                border_radius=1
            )
            
        elif self.shape == "cell":
            # Desenha uma célula de energia
            cell_size = self.size
            
            # Sombra da célula
            pygame.draw.circle(
                tela,
                (20, 20, 20, 100),
                shadow_pos,
                cell_size // 2
            )
            
            # Corpo da célula
            pygame.draw.circle(
                tela,
                self.color,
                pos,
                cell_size // 2
            )
            
            # Símbolo de energia
            energy_size = cell_size // 3
            pygame.draw.polygon(
                tela,
                (255, 255, 100),
                [
                    (pos[0], pos[1] - energy_size),
                    (pos[0] + energy_size//2, pos[1]),
                    (pos[0], pos[1] + energy_size),
                    (pos[0] - energy_size//2, pos[1])
                ]
            )
            
        elif self.shape == "grenade":
            # Desenha uma granada
            grenade_radius = self.size // 2
            
            # Sombra da granada
            pygame.draw.circle(
                tela,
                (20, 20, 20, 100),
                shadow_pos,
                grenade_radius
            )
            
            # Corpo da granada
            pygame.draw.circle(
                tela,
                self.color,
                pos,
                grenade_radius
            )
            
            # Pino da granada
            pin_offset = grenade_radius // 2
            pygame.draw.rect(
                tela,
                (100, 100, 100),
                pygame.Rect(
                    pos[0] - pin_offset//2,
                    pos[1] - grenade_radius - pin_offset,
                    pin_offset,
                    pin_offset
                )
            )

        # Adiciona contorno para todos os tipos
        if self.shape == "box":
            pygame.draw.rect(
                tela,
                (50, 50, 50),
                pygame.Rect(pos[0] - self.size//2, pos[1] - self.size//2, self.size, self.size),
                width=1,
                border_radius=2
            )
        elif self.shape == "shell":
            shell_width = self.size // 2
            shell_height = self.size
            pygame.draw.rect(
                tela,
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
            pygame.draw.polygon(tela, (50, 50, 50), points, width=1)
        elif self.shape == "grenade":
            pygame.draw.circle(tela, (50, 50, 50), pos, self.size // 2, width=1)