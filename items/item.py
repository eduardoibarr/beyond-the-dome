import pygame
import math
from abc import ABC
from core.settings import *

class Item(pygame.sprite.Sprite, ABC):
    """Classe base para todos os itens coletáveis no jogo.
    
    Esta classe abstrata define a estrutura básica para todos os itens do jogo:
    - Sistema de posicionamento e colisão
    - Animação de flutuação e spawn
    - Detecção de proximidade do jogador
    - Coleta automática
    - Sistema de renderização básico
    
    As subclasses devem implementar:
    - Renderização específica do item
    - Efeitos de coleta personalizados
    - Lógica adicional específica do tipo de item
    """
    def __init__(self, game, x, y, item_type='generic', groups=None):
        """Inicializa um item base.
        
        Args:
            game: Referência para o objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            item_type (str): Tipo de item para identificação
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        # Configura os grupos de sprites
        groups = groups or []
        if hasattr(game, 'items_group'):
            groups.append(game.items_group)
        if hasattr(game, 'all_sprites'):
            groups.append(game.all_sprites)
        super().__init__(*groups)

        # Armazena referência para o jogo
        self.game = game
        
        # Sistema de posicionamento
        self.x = x
        self.y = y
        self.z = 0  # Para efeitos 3D ou ordem de desenho
        
        # Sistema de colisão
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
        
        # Estado de descoberta (usado por itens especiais)
        self.discovered = False
        
        # Sistema de animação
        self.bounce_height = 0
        self.spawn_animation_time = 0.5
        self.spawn_time = 0
        
        # Configura componentes específicos do item
        self.setup()
        
    def setup(self):
        """Método para configuração adicional do item.
        
        As subclasses devem sobrescrever este método para:
        - Configurar propriedades específicas
        - Inicializar componentes adicionais
        - Preparar recursos visuais
        """
        pass
    
    def update(self, dt):
        """Atualiza o estado e comportamento do item.
        
        Este método implementa:
        1. Animação de flutuação
        2. Animação de spawn
        3. Detecção de proximidade do jogador
        4. Coleta automática
        
        Args:
            dt (float): Delta de tempo em segundos
        """
        if self.collected:
            return
            
        # Atualiza o tempo de vida do item
        self.age += dt
        
        # Animação de flutuação
        self.bob_offset += self.bob_direction * self.bob_speed * dt
        if abs(self.bob_offset) >= self.bob_height:
            self.bob_direction *= -1
            self.bob_offset = self.bob_height if self.bob_offset > 0 else -self.bob_height
            
        # Animação de spawn
        if self.age < self.spawn_animation_time:
            progress = self.age / self.spawn_animation_time
            self.bounce_height = 20 * (1 - progress) ** 2
        else:
            self.bounce_height = 0
            
        # Verifica proximidade do jogador
        if hasattr(self.game, 'player') and not self.collected:
            player_center = (
                self.game.player.rect.centerx,
                self.game.player.rect.centery
            )
            item_center = (self.rect.centerx, self.rect.centery)
            
            dx = player_center[0] - item_center[0]
            dy = player_center[1] - item_center[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Coleta automática quando o jogador está próximo
            if distance < ITEM_COLLECT_RADIUS:
                self.collect()
    
    def collect(self):
        """Processa a coleta do item.
        
        Este método:
        1. Marca o item como coletado
        2. Toca o som de coleta
        3. Adiciona ao inventário
        4. Retorna o status da coleta
        
        Retorna:
            bool: True se o item foi coletado com sucesso, False caso contrário
        """
        if self.collected:
            return False
            
        self.collected = True
        
        # Efeito sonoro de coleta
        if hasattr(self.game, 'sounds') and 'pickup' in self.game.sounds:
            self.game.sounds['pickup'].play()
            
        # Adiciona ao inventário
        if hasattr(self.game, 'inventory'):
            self.game.inventory.add_item(self.item_type)
            
        return True
        
    def render(self, screen, camera):
        """Renderiza o item na tela.
        
        Implementa a renderização básica do item:
        1. Calcula a posição considerando animações
        2. Desenha uma representação simples
        3. Prepara para renderização específica nas subclasses
        
        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição na tela
        """
        if self.collected:
            return
            
        # Calcula a posição com animações
        item_pos = camera.apply(pygame.Rect(
            self.x - 8,
            self.y - 8 - self.bob_offset - self.bounce_height,
            16, 16
        ))
        
        # Renderização básica do item
        pygame.draw.rect(screen, WHITE, item_pos)