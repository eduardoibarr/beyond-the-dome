import pygame
from core.settings import WIDTH, HEIGHT, TILE_SIZE, CAMERA_LERP_FACTOR

# --- Constantes ---
# CAMERA_LERP_FACTOR = 0.08  # Quão rápido a câmera segue o jogador (menor = mais suave)

class Camera:
    """
    Gerencia a visão da câmera com rolagem. Rastreia uma posição e aplica deslocamentos às entidades.
    """
    def __init__(self, map_width, map_height):
        """
        Inicializa a câmera com as dimensões do mapa.
        
        Args:
            map_width (int): Largura total do mapa do jogo em pixels.
            map_height (int): Altura total do mapa do jogo em pixels.
        """
        self.camera = pygame.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height
        
        # Posição flutuante da câmera para movimento suave
        self.x = 0.0
        self.y = 0.0

    def apply(self, entity):
        """
        Aplica o deslocamento da câmera a uma entidade ou rect.
        
        Args:
            entity: Um objeto pygame.sprite.Sprite ou pygame.Rect.
            
        Returns:
            pygame.Rect: O retângulo da entidade ajustado para o deslocamento da câmera.
        """
        # Usa a parte inteira da posição flutuante da câmera para aplicar o deslocamento
        offset_x = int(self.x)
        offset_y = int(self.y)

        # Lida com objetos sprite e objetos rect
        if hasattr(entity, 'rect'):
            return entity.rect.move(offset_x, offset_y)
        else:  # Assume que já é um Rect
            return entity.move(offset_x, offset_y)

    def update(self, target):
        """
        Atualiza a posição da câmera suavemente para manter o alvo centralizado.
        
        Args:
            target (pygame.sprite.Sprite): O sprite que a câmera deve seguir (geralmente o jogador).
        """
        # Calcula o canto superior esquerdo desejado da visão da câmera (posição do alvo)
        # Queremos que o centro do alvo esteja no centro da tela
        target_x = -target.rect.centerx + WIDTH // 2
        target_y = -target.rect.centery + HEIGHT // 2

        # --- Interpolação Suave (Lerp) ---
        # Move a posição flutuante da câmera em direção à posição do alvo
        self.x += (target_x - self.x) * CAMERA_LERP_FACTOR
        self.y += (target_y - self.y) * CAMERA_LERP_FACTOR

        # --- Limitação (Clamping) ---
        # Limita as coordenadas *flutuantes* da câmera para evitar mostrar áreas fora do mapa
        self.x = min(0.0, self.x)  # Não rolar além da borda esquerda (x=0)
        self.y = min(0.0, self.y)  # Não rolar além da borda superior (y=0)
        self.x = max(-(self.map_width - WIDTH), self.x)  # Não rolar além da borda direita
        self.y = max(-(self.map_height - HEIGHT), self.y)  # Não rolar além da borda inferior

        # Atualiza o Rect real da câmera usado para aplicar deslocamentos (usando a parte inteira)
        self.camera.x = int(self.x)
        self.camera.y = int(self.y)

    def screen_to_world(self, screen_pos):
        """
        Converte coordenadas da tela para coordenadas do mundo.
        
        Args:
            screen_pos (tuple): As coordenadas (x, y) da tela para converter.
            
        Returns:
            tuple: As coordenadas (x, y) do mundo correspondentes.
        """
        # Usa a parte inteira da posição flutuante da câmera
        return (screen_pos[0] - int(self.x), screen_pos[1] - int(self.y))

    def apply_coords(self, x, y):
        """
        Converte coordenadas do mundo para coordenadas da tela.
        
        Args:
            x (int): A coordenada x do mundo.
            y (int): A coordenada y do mundo.
            
        Returns:
            tuple: As coordenadas (x, y) da tela correspondentes.
        """
        # Usa a parte inteira da posição flutuante da câmera
        return (x + int(self.x), y + int(self.y)) 