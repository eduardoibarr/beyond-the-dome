import noise
import random
import numpy as np

class NoiseGenerator:
    def __init__(self, seed=None, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0):
        """
        Inicializa o gerador de ruído com parâmetros configuráveis.
        
        Args:
            seed (int): Semente para geração aleatória. Se None, será gerada aleatoriamente.
            scale (float): Escala do ruído. Valores maiores = mais detalhes.
            octaves (int): Número de camadas de ruído. Mais octaves = mais detalhes.
            persistence (float): Quanto cada octave contribui para o resultado final (0-1).
            lacunarity (float): Quanto cada octave aumenta em frequência.
        """
        self.seed = seed if seed is not None else random.randint(0, 1000)
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        
        # Cache para valores de ruído já calculados
        self.noise_cache = {}
        
    def get_noise_2d(self, x, y):
        """
        Gera um valor de ruído 2D usando Perlin noise.
        
        Args:
            x (float): Coordenada x
            y (float): Coordenada y
            
        Returns:
            float: Valor de ruído entre -1 e 1
        """
        # Tenta usar o cache primeiro
        cache_key = (int(x), int(y))
        if cache_key in self.noise_cache:
            return self.noise_cache[cache_key]
            
        # Calcula o ruído
        value = 0
        amplitude = 1.0
        frequency = 1.0
        
        for _ in range(self.octaves):
            nx = x / self.scale * frequency
            ny = y / self.scale * frequency
            
            # Usa noise.pnoise2 para ruído Perlin 2D
            value += noise.pnoise2(nx, ny, octaves=1, persistence=self.persistence, 
                                 lacunarity=self.lacunarity, repeatx=1024, repeaty=1024, 
                                 base=self.seed) * amplitude
                                 
            amplitude *= self.persistence
            frequency *= self.lacunarity
            
        # Normaliza para -1 a 1
        value = max(-1.0, min(1.0, value))
        
        # Armazena no cache
        self.noise_cache[cache_key] = value
        return value
        
    def get_noise_2d_array(self, width, height, x_offset=0, y_offset=0):
        """
        Gera um array 2D de valores de ruído.
        
        Args:
            width (int): Largura do array
            height (int): Altura do array
            x_offset (float): Deslocamento em x
            y_offset (float): Deslocamento em y
            
        Returns:
            numpy.ndarray: Array 2D de valores de ruído
        """
        noise_array = np.zeros((height, width))
        
        for y in range(height):
            for x in range(width):
                noise_array[y][x] = self.get_noise_2d(x + x_offset, y + y_offset)
                
        return noise_array
        
    def get_terrain_height(self, x, y, min_height=0, max_height=1):
        """
        Gera uma altura de terreno baseada no ruído.
        
        Args:
            x (float): Coordenada x
            y (float): Coordenada y
            min_height (float): Altura mínima
            max_height (float): Altura máxima
            
        Returns:
            float: Altura do terreno
        """
        noise_value = self.get_noise_2d(x, y)
        # Normaliza de -1,1 para min_height,max_height
        return min_height + (noise_value + 1) * (max_height - min_height) / 2
        
    def get_terrain_type(self, x, y, thresholds):
        """
        Determina o tipo de terreno baseado em thresholds de ruído.
        
        Args:
            x (float): Coordenada x
            y (float): Coordenada y
            thresholds (dict): Dicionário com thresholds para cada tipo de terreno
                             Ex: {'water': -0.2, 'sand': 0.0, 'grass': 0.3, 'mountain': 0.7}
                             
        Returns:
            str: Nome do tipo de terreno
        """
        noise_value = self.get_noise_2d(x, y)
        
        # Encontra o tipo de terreno apropriado baseado nos thresholds
        terrain_type = None
        for name, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if noise_value >= threshold:
                terrain_type = name
                break
                
        return terrain_type if terrain_type else list(thresholds.keys())[0] 