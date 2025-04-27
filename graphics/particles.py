# Importação das bibliotecas necessárias
import pygame
import random
import math
from core.settings import *

# Classe da partícula de sangue
class BloodParticle:
    """Representa um único efeito de partícula de sangue."""
    def __init__(self, x, y):
        """
        Inicializa uma partícula de sangue em uma determinada posição.
        Args:
            x (float): Coordenada x inicial (coordenadas do mundo).
            y (float): Coordenada y inicial (coordenadas do mundo).
        """
        self.x = x
        self.y = y
        self.size = BLOOD_PARTICLE_SIZE
        self.color = BLOOD_PARTICLE_COLOR
        self.lifetime = BLOOD_PARTICLE_LIFETIME # Milissegundos
        self.created_at = pygame.time.get_ticks() # Momento da criação

        # Define um vetor de velocidade inicial aleatório
        angle = random.uniform(0, 2 * math.pi) # Direção aleatória
        # Usa uma velocidade aleatória dentro de um pequeno intervalo para variação
        speed = random.uniform(BLOOD_PARTICLE_SPEED * 0.5, BLOOD_PARTICLE_SPEED * 1.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        # Efeito simples de gravidade
        self.gravity = 0.1 # Pixels por quadro^2 (ajuste conforme necessário)

    def update(self, dt): # Passa o delta time para independência da taxa de quadros
        """
        Atualiza a posição da partícula e aplica a gravidade.
        Args:
             dt (float): Delta time em segundos.
        """
        # Atualiza a velocidade com a gravidade (escalada por dt)
        # O efeito da gravidade precisa de escalonamento cuidadoso com dt.
        # Uma abordagem simples: aplicar uma aceleração constante para baixo.
        # Física mais precisa envolveria escalar a aceleração por dt^2, mas
        # para partículas simples, escalar a mudança de velocidade por dt é frequentemente suficiente.
        self.vy += self.gravity * (dt * 60) # Escala o efeito da gravidade aproximadamente baseado na meta de 60 FPS

        # Atualiza a posição com base na velocidade (escalada por dt)
        self.x += self.vx * (dt * 60) # Escala a velocidade por dt * fps_alvo
        self.y += self.vy * (dt * 60)

    def is_dead(self):
        """Verifica se o tempo de vida da partícula expirou."""
        return pygame.time.get_ticks() - self.created_at > self.lifetime

    def get_alpha(self):
        """
        Calcula o alfa (transparência) da partícula com base em seu tempo de vida restante.
        Retorna:
            int: Valor alfa (0-255).
        """
        elapsed_time = pygame.time.get_ticks() - self.created_at
        # Garante que o tempo de vida não seja zero para evitar erro de divisão
        if self.lifetime <= 0:
            return 0
        # Calcula a fração de tempo de vida restante
        lifetime_fraction = max(0.0, 1.0 - (elapsed_time / self.lifetime))
        # Desvanece linearmente
        return int(255 * lifetime_fraction)

    def draw(self, screen, camera):
        """
        Desenha a partícula na tela, ajustada pela câmera.
        Args:
            screen (pygame.Surface): A superfície para desenhar.
            camera (Camera): O objeto da câmera do jogo para ajuste de posição.
        """
        alpha = self.get_alpha()
        if alpha > 0:
            # Cria um Rect temporário para a posição da partícula no mundo
            # Usa coordenadas inteiras para o Rect
            particle_rect = pygame.Rect(int(self.x), int(self.y), self.size * 2, self.size * 2)
            # Aplica o deslocamento da câmera para obter o Rect da tela
            screen_rect = camera.apply(particle_rect)

            # Culling básico: Usa o screen_rect para culling
            if screen_rect.colliderect(screen.get_rect()):
                try:
                    # Cria uma superfície temporária para mistura alfa
                    surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                    # Garante que a cor tenha 3 componentes antes de adicionar alfa
                    if len(self.color) == 3:
                         draw_color = (*self.color, alpha)
                    else: # Assume que a cor já tem alfa, apenas o atualiza
                         draw_color = (*self.color[:3], alpha)

                    # Desenha o círculo centralizado na superfície temporária
                    pygame.draw.circle(surface, draw_color, (self.size, self.size), self.size)
                    # Blita a superfície temporária na tela principal usando o canto superior esquerdo do screen_rect
                    screen.blit(surface, screen_rect.topleft)
                except ValueError as e:
                    print(f"Erro ao desenhar partícula: {e}, Cor: {self.color}, Alpha: {alpha}")
                except TypeError as e:
                     print(f"Erro ao desenhar partícula: {e}, screen_x: {screen_rect.x}, screen_y: {screen_rect.y}")


# Sistema de partículas de sangue
class BloodParticleSystem:
    """Gerencia uma coleção de objetos BloodParticle."""
    def __init__(self):
        """Inicializa o sistema de partículas."""
        self.particles = []

    def add_particles(self, x, y, count=BLOOD_PARTICLE_COUNT):
        """
        Adiciona um número especificado de novas partículas de sangue em uma determinada posição.
        Args:
            x (float): Coordenada X para emissão da partícula (coordenadas do mundo).
            y (float): Coordenada Y para emissão da partícula (coordenadas do mundo).
            count (int): Número de partículas a adicionar.
        """
        for _ in range(count):
            self.particles.append(BloodParticle(x, y))

    def update(self, dt): # Passa o delta time
        """Atualiza todas as partículas ativas e remove as mortas."""
        # Atualiza as partículas primeiro
        for particle in self.particles:
            particle.update(dt)
        # Remove partículas mortas usando compreensão de lista para eficiência
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen, camera):
        """
        Desenha todas as partículas ativas na tela, ajustadas pela câmera.
        Args:
            screen (pygame.Surface): A superfície para desenhar.
            camera (Camera): O objeto da câmera do jogo.
        """
        for particle in self.particles:
            particle.draw(screen, camera) # O método draw da partícula lida com o ajuste da câmera

# Função auxiliar para aplicação da câmera (adicionar à classe Camera ou tornar independente)
# Isso assume que a classe Camera tem um método como este ou lógica similar
def apply_coords(camera, world_x, world_y):
    """Aplica o deslocamento da câmera às coordenadas do mundo."""
    return world_x + camera.camera.x, world_y + camera.camera.y

# Adicione este método à sua classe Camera em level.py:
# class Camera:
#     ... (outros métodos) ...
#     def apply_coords(self, world_x, world_y):
#         """Aplica o deslocamento da câmera às coordenadas do mundo."""
#         return world_x + self.camera.x, world_y + self.camera.y

# Classe da partícula radioativa
class RadioactiveParticle:
    """Representa uma partícula de radiação que flutua em zonas radioativas."""
    def __init__(self, x, y, parent_zone=None):
        """
        Inicializa uma partícula radioativa.
        Args:
            x (float): Posição X inicial da partícula (coordenadas do mundo).
            y (float): Posição Y inicial da partícula (coordenadas do mundo).
            parent_zone: Referência opcional à zona radioativa que gerou esta partícula.
        """
        self.x = x
        self.y = y
        self.parent_zone = parent_zone
        
        # Propriedades visuais
        self.radius = random.randint(1, 3)
        self.alpha = random.randint(100, 200)
        self.color = RADIOACTIVE_GLOW
        
        # Propriedades de movimento
        self.lifetime = random.randint(2000, 5000)  # milissegundos
        self.born_time = pygame.time.get_ticks()
        self.drift_x = random.uniform(-0.5, 0.5)
        self.drift_y = random.uniform(-0.5, 0.5)
        self.oscillation_speed = random.uniform(0.001, 0.005)
        self.oscillation_distance = random.uniform(5, 15)
        
        # Posição base para oscilação
        self.base_x = x
        self.base_y = y
    
    def get_lifetime_ratio(self):
        """Retorna um valor entre 0 e 1 representando o tempo de vida restante da partícula."""
        current_time = pygame.time.get_ticks()
        age = current_time - self.born_time
        if age >= self.lifetime:
            return 0
        return 1.0 - (age / self.lifetime)
    
    def is_dead(self):
        """Verifica se o tempo de vida da partícula expirou."""
        return self.get_lifetime_ratio() <= 0
    
    def update(self, dt):
        """
        Atualiza a posição e aparência da partícula.
        Args:
            dt (float): Delta time em segundos.
        """
        # Movimento de deriva (escalado pelo dt)
        self.base_x += self.drift_x * (dt * 60)
        self.base_y += self.drift_y * (dt * 60)
        
        # Movimento de oscilação
        current_time = pygame.time.get_ticks()
        oscillation_x = math.sin(current_time * self.oscillation_speed) * self.oscillation_distance
        oscillation_y = math.cos(current_time * self.oscillation_speed * 0.7) * self.oscillation_distance
        
        # Posição final
        self.x = self.base_x + oscillation_x
        self.y = self.base_y + oscillation_y
    
    def get_alpha(self):
        """Calcula o valor alpha (transparência) com base no tempo de vida restante."""
        return int(self.alpha * self.get_lifetime_ratio())
    
    def draw(self, screen, camera):
        """
        Desenha a partícula na tela, ajustada pela câmera.
        Args:
            screen (pygame.Surface): A superfície para desenhar.
            camera (Camera): O objeto da câmera do jogo para ajuste de posição.
        """
        alpha = self.get_alpha()
        if alpha > 0:
            # Cria um Rect temporário para a posição da partícula no mundo
            particle_rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), 
                                       self.radius * 2, self.radius * 2)
            # Aplica o offset da câmera para obter o Rect na tela
            screen_rect = camera.apply(particle_rect)
            
            # Culling básico: Use o screen_rect para culling
            if screen_rect.colliderect(screen.get_rect()):
                try:
                    # Cria uma superfície temporária para blending alpha
                    surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                    
                    # Cor com componente alpha
                    draw_color = (*self.color, alpha)
                    
                    # Desenha o círculo centralizado na superfície temporária
                    pygame.draw.circle(surface, draw_color, (self.radius, self.radius), self.radius)
                    
                    # Adicionar um pequeno brilho
                    if self.radius > 1:
                        glow_color = (255, 255, 255, alpha // 2)
                        pygame.draw.circle(surface, glow_color, (self.radius, self.radius), self.radius // 2)
                    
                    # Blita a superfície temporária na tela principal usando o topo-esquerdo do screen_rect
                    screen.blit(surface, screen_rect.topleft)
                except (ValueError, TypeError) as e:
                    print(f"Erro ao desenhar partícula radioativa: {e}")

# Sistema de partículas radioativas
class RadioactiveParticleSystem:
    """Gerencia uma coleção de objetos RadioactiveParticle."""
    def __init__(self):
        """Inicializa o sistema de partículas."""
        self.particles = []
        self.zones = []  # Referências para zonas radioativas ativas
    
    def register_zone(self, zone):
        """Registra uma zona radioativa para geração de partículas."""
        if zone not in self.zones:
            self.zones.append(zone)
    
    def unregister_zone(self, zone):
        """Remove uma zona radioativa do registro."""
        if zone in self.zones:
            self.zones.remove(zone)
    
    def add_particle(self, x, y, parent_zone=None):
        """Adiciona uma única partícula radioativa."""
        self.particles.append(RadioactiveParticle(x, y, parent_zone))
    
    def add_particles(self, x, y, count=5, parent_zone=None):
        """
        Adiciona várias partículas radioativas em uma posição.
        Args:
            x (float): Coordenada X para emissão da partícula (coordenadas do mundo).
            y (float): Coordenada Y para emissão da partícula (coordenadas do mundo).
            count (int): Número de partículas para adicionar.
            parent_zone: Referência opcional à zona radioativa que gerou estas partículas.
        """
        for _ in range(count):
            offset_x = random.randint(-12, 12)
            offset_y = random.randint(-12, 12)
            self.add_particle(x + offset_x, y + offset_y, parent_zone)
    
    def update(self, dt):
        """
        Atualiza todas as partículas ativas e remove as mortas.
        Também gera novas partículas das zonas registradas.
        """
        # Atualiza as partículas existentes
        for particle in self.particles:
            particle.update(dt)
        
        # Remove partículas mortas
        self.particles = [p for p in self.particles if not p.is_dead()]
        
        # Gera novas partículas das zonas registradas (chance aleatória)
        for zone in self.zones:
            if random.random() < 0.02:  # 2% de chance por quadro
                zone_rect = zone.rect
                x = zone_rect.centerx + random.randint(-16, 16)
                y = zone_rect.centery + random.randint(-16, 16)
                self.add_particle(x, y, zone)
    
    def draw(self, screen, camera):
        """
        Desenha todas as partículas ativas na tela, ajustadas pela câmera.
        Args:
            screen (pygame.Surface): A superfície para desenhar.
            camera (Camera): O objeto da câmera do jogo.
        """
        for particle in self.particles:
            particle.draw(screen, camera)
