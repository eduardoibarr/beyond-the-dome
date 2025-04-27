# Importação da biblioteca Pygame
import pygame

# Classe para gerenciar spritesheets
class Spritesheet:
    """Classe para gerenciar spritesheets"""
    def __init__(self, filename):
        # Carrega o arquivo de spritesheet
        try:
            self.sheet = pygame.image.load(filename)
        except pygame.error as e:
            print(f"Não foi possível carregar o spritesheet: {filename}")
            print(e)
            raise SystemExit(e)
    
    def get_image(self, x, y, width, height, scale=1, colorkey=None):
        """Extrai uma imagem da spritesheet
        
        Args:
            x, y: Posição da imagem na spritesheet
            width, height: Dimensões da imagem
            scale: Fator de escala (padrão 1)
            colorkey: Cor para transparência (None para usar canal alpha)
        """
        # Cria uma nova superfície com os tamanhos especificados
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Copia a parte da spritesheet para a nova superfície
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        
        # Escala a imagem se necessário
        if scale != 1:
            image = pygame.transform.scale(image, 
                                          (int(width * scale), int(height * scale)))
        
        # Aplica a cor de transparência se especificada
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
            
        return image
    
    def load_strip(self, rect, image_count, colorkey=None):
        """Carrega uma sequência de imagens horizontalmente
        
        Args:
            rect: (x, y, width, height) da primeira imagem
            image_count: Número de imagens na sequência
            colorkey: Cor para transparência
        """
        # Lista para armazenar os frames
        frames = []
        x, y, width, height = rect
        
        # Carrega cada frame da sequência
        for i in range(image_count):
            frames.append(self.get_image(x + i * width, y, width, height, colorkey=colorkey))
            
        return frames
    
    def load_grid(self, rect, cols, rows, colorkey=None):
        """Carrega uma grade de imagens
        
        Args:
            rect: (x, y, width, height) da primeira imagem
            cols: Número de colunas
            rows: Número de linhas
            colorkey: Cor para transparência
        """
        # Lista para armazenar os frames
        frames = []
        x, y, width, height = rect
        
        # Carrega cada frame da grade
        for row in range(rows):
            for col in range(cols):
                frames.append(self.get_image(
                    x + col * width, 
                    y + row * height, 
                    width, height, 
                    colorkey=colorkey
                ))
                
        return frames 