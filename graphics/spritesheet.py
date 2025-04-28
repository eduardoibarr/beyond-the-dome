import pygame

class Spritesheet:
    """Sistema de gerenciamento de folhas de sprites.
    
    Esta classe implementa:
    - Carregamento de spritesheets
    - Extração de sprites individuais
    - Carregamento de sequências de animação
    - Suporte a escala e transparência
    - Otimização de memória através de reutilização
    """
    def __init__(self, filename):
        """Inicializa o gerenciador de spritesheet.
        
        Args:
            filename (str): Caminho do arquivo da folha de sprites
            
        Raises:
            SystemExit: Se não for possível carregar o arquivo
        """
        # Carrega o arquivo de folha de sprites.
        try:
            self.sheet = pygame.image.load(filename)
        except pygame.error as e:
            print(f"Não foi possível carregar a folha de sprites: {filename}")
            print(e)
            raise SystemExit(e)
    
    def get_image(self, x, y, width, height, scale=1, colorkey=None):
        """Extrai uma única imagem da folha de sprites.
        
        Este método:
        1. Cria uma nova superfície com canal alpha
        2. Extrai a região especificada da spritesheet
        3. Aplica escala se necessário
        4. Configura a transparência
        
        Args:
            x, y (int): Posição do sprite na folha
            width, height (int): Dimensões do sprite
            scale (float): Fator de escala (1 = tamanho original)
            colorkey (tuple): Cor RGB para transparência
            
        Returns:
            pygame.Surface: Imagem extraída e processada
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
        """Carrega uma sequência horizontal de sprites.
        
        Útil para:
        - Animações de movimento
        - Sequências de ações
        - Sprites com múltiplos estados
        
        Args:
            rect (tuple): (x, y, width, height) do primeiro sprite
            image_count (int): Número de sprites na sequência
            colorkey (tuple): Cor RGB para transparência
            
        Returns:
            list: Lista de pygame.Surface com os sprites extraídos
        """
        # Lista para armazenar os quadros (frames).
        frames = []
        x, y, width, height = rect
        
        # Carrega cada frame da sequência
        for i in range(image_count):
            frames.append(self.get_image(x + i * width, y, width, height, colorkey=colorkey))
            
        return frames
    
    def load_grid(self, rect, cols, rows, colorkey=None):
        """Carrega uma grade de sprites.
        
        Ideal para:
        - Conjuntos completos de animações
        - Tilesets
        - Múltiplas direções de movimento
        
        Args:
            rect (tuple): (x, y, width, height) do primeiro sprite
            cols (int): Número de colunas na grade
            rows (int): Número de linhas na grade
            colorkey (tuple): Cor RGB para transparência
            
        Returns:
            list: Lista de pygame.Surface com todos os sprites da grade
        """
        # Lista para armazenar os quadros (frames).
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