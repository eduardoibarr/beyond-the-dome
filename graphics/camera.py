import pygame
from core.settings import WIDTH, HEIGHT, CAMERA_LERP_FACTOR

class Camera:
    """Sistema de câmera do jogo.
    
    Esta classe implementa:
    - Rolagem suave da câmera seguindo o jogador
    - Sistema de coordenadas do mundo para a tela
    - Interpolação linear (lerp) para movimento suave
    - Limitação de bordas do mapa
    - Culling de objetos fora da tela
    """
    def __init__(self, map_width, map_height):
        """Inicializa o sistema de câmera.
        
        Args:
            map_width (int): Largura total do mapa em pixels
            map_height (int): Altura total do mapa em pixels
        """
        self.camera = pygame.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height
        
        # Posição com precisão de ponto flutuante para movimento suave
        self.x = 0.0
        self.y = 0.0

    def apply(self, entity):
        """Converte a posição de uma entidade do mundo para coordenadas da tela.
        
        Este método:
        1. Aplica o deslocamento da câmera à entidade
        2. Suporta tanto sprites quanto retângulos
        3. Usa a posição precisa da câmera
        
        Args:
            entity: Um objeto pygame.sprite.Sprite ou pygame.Rect
            
        Returns:
            pygame.Rect: Retângulo com a posição ajustada para a tela
        """
        offset_x = int(self.x)
        offset_y = int(self.y)

        if hasattr(entity, 'rect'):
            return entity.rect.move(offset_x, offset_y)
        else:
            return entity.move(offset_x, offset_y)

    def update(self, target):
        """Atualiza a posição da câmera para seguir o alvo.
        
        Implementa:
        1. Centralização suave no alvo
        2. Interpolação linear para movimento fluido
        3. Limitação às bordas do mapa
        
        Args:
            target (pygame.sprite.Sprite): Sprite a ser seguido (geralmente o jogador)
        """
        # Calcula a posição desejada (centralizada no alvo)
        target_x = -target.rect.centerx + WIDTH // 2
        target_y = -target.rect.centery + HEIGHT // 2

        # Interpolação linear para movimento suave
        self.x += (target_x - self.x) * CAMERA_LERP_FACTOR
        self.y += (target_y - self.y) * CAMERA_LERP_FACTOR

        # Limita a câmera às bordas do mapa
        self.x = min(0.0, self.x)  # Borda esquerda
        self.y = min(0.0, self.y)  # Borda superior
        self.x = max(-(self.map_width - WIDTH), self.x)  # Borda direita
        self.y = max(-(self.map_height - HEIGHT), self.y)  # Borda inferior

        # Atualiza o retângulo da câmera
        self.camera.x = int(self.x)
        self.camera.y = int(self.y)

    def screen_to_world(self, screen_pos):
        """Converte coordenadas da tela para coordenadas do mundo.
        
        Útil para:
        - Posicionamento do mouse no mundo
        - Interação com objetos do mundo
        - Cálculos de colisão
        
        Args:
            screen_pos (tuple): Coordenadas (x, y) na tela
            
        Returns:
            tuple: Coordenadas (x, y) correspondentes no mundo
        """
        return (screen_pos[0] - int(self.x), screen_pos[1] - int(self.y))

    def apply_coords(self, x, y):
        """Converte coordenadas individuais do mundo para a tela.
        
        Útil para:
        - Renderização de efeitos
        - Posicionamento de UI
        - Desenho de partículas
        
        Args:
            x (int): Coordenada x no mundo
            y (int): Coordenada y no mundo
            
        Returns:
            tuple: Coordenadas (x, y) correspondentes na tela
        """
        return (x + int(self.x), y + int(self.y))

    def is_rect_visible(self, rect):
        """Verifica se um retângulo está visível na área da câmera.
        
        Usado para:
        - Culling de objetos fora da tela
        - Otimização de renderização
        - Economia de processamento
        
        Args:
            rect (pygame.Rect): Retângulo a ser verificado
            
        Returns:
            bool: True se visível, False caso contrário
        """
        visible_area = pygame.Rect(-self.camera.x, -self.camera.y, WIDTH, HEIGHT)
        return rect.colliderect(visible_area) 