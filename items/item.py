import pygame
import math
from abc import ABC
from core.settings import *

class Item(pygame.sprite.Sprite, ABC):
    """Classe base para todos os itens coletáveis no jogo.

    Esta é uma classe abstrata que deve ser herdada por tipos de itens específicos.
    """
    def __init__(self, game, x, y, item_type='generic', groups=None):
        """Inicializa um item.

        Args:
            game: Referência para o objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            item_type (str): Tipo de item para identificação
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        # Chama o construtor pai com os grupos apropriados
        groups = groups or []
        if hasattr(game, 'items_group'):
            groups.append(game.items_group)
        if hasattr(game, 'all_sprites'):
            groups.append(game.all_sprites)
        super().__init__(*groups)

        # Armazena referência para o jogo
        self.game = game
        
        # Set position
        self.x = x
        self.y = y
        self.z = 0  # For potential 3D effects or drawing order
        
        # Create rect for collision detection
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.hitbox = self.rect.copy()
        
        # Propriedades do item
        self.item_type = item_type
        self.collected = False
        self.age = 0
        self.bob_offset = 0
        self.bob_direction = 1
        self.bob_height = 4
        self.bob_speed = 1.5 
        
        # Se o item foi descoberto (para módulos de filtro)
        self.discovered = False
        
        # Para desenho
        self.bounce_height = 0
        self.spawn_animation_time = 0.5
        self.spawn_time = 0
        
        # Configura quaisquer componentes filhos
        self.setup()
        
    def setup(self):
        """Substitua isso nas subclasses para configurar componentes específicos do item."""
        pass
    
    def update(self, dt):
        """Atualiza o estado do item.

        Args:
            dt (float): Delta de tempo em segundos
        """
        if self.collected:
            return
            
        # Atualiza a idade
        self.age += dt
        
        # Animação de balanço
        self.bob_offset += self.bob_direction * self.bob_speed * dt
        if abs(self.bob_offset) >= self.bob_height:
            self.bob_direction *= -1
            self.bob_offset = self.bob_height if self.bob_offset > 0 else -self.bob_height
            
        # Manipula a animação de spawn
        if self.age < self.spawn_animation_time:
            progress = self.age / self.spawn_animation_time
            self.bounce_height = 20 * (1 - progress) ** 2
        else:
            self.bounce_height = 0
            
        # Verifica a proximidade do jogador se o jogador existir
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
            
            # Coleta automática se o jogador estiver próximo o suficiente
            if distance < ITEM_COLLECT_RADIUS:
                self.collect()
    
    def collect(self):
        """Marca o item como coletado e aciona efeitos.
        Substitua nas subclasses para adicionar efeitos específicos.
        """
        if self.collected:
            return False
            
        self.collected = True
        
        # Toca o som genérico de coleta
        if hasattr(self.game, 'sounds') and 'pickup' in self.game.sounds:
            self.game.sounds['pickup'].play()
            
        # Adiciona ao inventário se existir
        if hasattr(self.game, 'inventory'):
            self.game.inventory.add_item(self.item_type)
            
        return True
        
    def render(self, screen, camera):
        """Renderiza o item na tela.

        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição na tela
        """
        if self.collected:
            return
            
        # Calcula a posição com o balanço
        item_pos = camera.apply(pygame.Rect(
            self.x - 8,
            self.y - 8 - self.bob_offset - self.bounce_height,
            16, 16
        ))
        
        # Desenha uma forma simples representando o item
        pygame.draw.rect(screen, WHITE, item_pos)
        
        # A renderização específica do item deve ser implementada nas subclasses