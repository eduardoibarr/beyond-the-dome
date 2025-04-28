import pygame
import random
import math
from core.settings import (
    BLOOD_PARTICLE_SIZE,
    BLOOD_PARTICLE_COLOR,
    BLOOD_PARTICLE_LIFETIME,
    BLOOD_PARTICLE_SPEED,
    BLOOD_PARTICLE_COUNT,
    RAD_PARTICLE_SPEED,
    RAD_PARTICLE_LIFETIME
)

class BloodParticle:
    """Representa uma partícula de sangue no jogo.
    
    Cada partícula de sangue possui propriedades físicas como posição,
    velocidade, gravidade e tempo de vida. É usada para criar efeitos
    visuais de sangramento quando personagens são feridos.
    
    Attributes:
        x (float): Posição X da partícula
        y (float): Posição Y da partícula
        size (int): Tamanho da partícula em pixels
        color (tuple): Cor RGB da partícula
        lifetime (int): Tempo de vida em milissegundos
        created_at (int): Momento de criação em milissegundos
        vx (float): Velocidade horizontal
        vy (float): Velocidade vertical
        gravity (float): Força da gravidade aplicada
    """
    def __init__(self, x, y):
        """Inicializa uma nova partícula de sangue.
        
        Args:
            x (float): Posição X inicial
            y (float): Posição Y inicial
        """
        self.x = x
        self.y = y
        self.size = BLOOD_PARTICLE_SIZE
        self.color = BLOOD_PARTICLE_COLOR
        self.lifetime = BLOOD_PARTICLE_LIFETIME
        self.created_at = pygame.time.get_ticks()
        
        # Define direção e velocidade aleatórias
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(BLOOD_PARTICLE_SPEED*0.5, BLOOD_PARTICLE_SPEED*1.5)
        self.vx = math.cos(angle)*speed
        self.vy = math.sin(angle)*speed
        self.gravity = 0.1

    def update(self, dt):
        """Atualiza a posição e velocidade da partícula.
        
        Aplica gravidade e atualiza a posição baseado na velocidade.
        
        Args:
            dt (float): Delta time desde a última atualização
        """
        self.vy += self.gravity * dt * 60
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60

    def is_dead(self):
        """Verifica se a partícula deve ser removida.
        
        Returns:
            bool: True se a partícula excedeu seu tempo de vida
        """
        return pygame.time.get_ticks() - self.created_at > self.lifetime

    def get_alpha(self):
        """Calcula a transparência atual da partícula.
        
        A transparência diminui gradualmente conforme a partícula
        se aproxima do fim de seu tempo de vida.
        
        Returns:
            int: Valor de alpha entre 0 e 255
        """
        elapsed = pygame.time.get_ticks() - self.created_at
        frac = max(0.0, 1.0 - elapsed/self.lifetime)
        return int(255*frac) if self.lifetime>0 else 0

    def draw(self, screen, camera):
        """Renderiza a partícula na tela.
        
        Args:
            screen (pygame.Surface): Superfície de renderização
            camera (Camera): Objeto câmera para ajuste de posição
        """
        alpha = self.get_alpha()
        if alpha<=0: return
        
        # Aplica transformação da câmera
        rect = pygame.Rect(int(self.x), int(self.y), self.size*2, self.size*2)
        screen_rect = camera.apply(rect)
        if not screen_rect.colliderect(screen.get_rect()): return
        
        # Cria superfície para a partícula
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        draw_color = (*self.color[:3], alpha)
        pygame.draw.circle(surf, draw_color, (self.size, self.size), self.size)
        screen.blit(surf, screen_rect.topleft)

class BloodParticleSystem:
    """Gerenciador de partículas de sangue.
    
    Controla a criação, atualização e renderização de múltiplas
    partículas de sangue, criando efeitos visuais de sangramento.
    
    Attributes:
        particles (list): Lista de partículas ativas
    """
    def __init__(self):
        """Inicializa o sistema de partículas."""
        self.particles = []

    def add_particles(self, x, y, count=BLOOD_PARTICLE_COUNT):
        """Adiciona novas partículas de sangue.
        
        Args:
            x (float): Posição X do efeito
            y (float): Posição Y do efeito
            count (int): Número de partículas a criar
        """
        for _ in range(count):
            self.particles.append(BloodParticle(x, y))

    def update(self, dt):
        """Atualiza todas as partículas ativas.
        
        Args:
            dt (float): Delta time desde a última atualização
        """
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen, camera):
        """Renderiza todas as partículas ativas.
        
        Args:
            screen (pygame.Surface): Superfície de renderização
            camera (Camera): Objeto câmera para ajuste de posição
        """
        for p in self.particles: p.draw(screen, camera)


class RadiationParticle:
    """Representa uma partícula de radiação no jogo.
    
    Cada partícula de radiação possui propriedades físicas como posição,
    velocidade e tempo de vida. É usada para criar efeitos visuais
    de áreas radioativas.
    
    Attributes:
        pos (pygame.Vector2): Posição da partícula
        vel (pygame.Vector2): Vetor velocidade
        life (float): Tempo de vida em segundos
        age (float): Idade atual em segundos
        size (int): Tamanho da partícula em pixels
    """
    def __init__(self, x, y):
        """Inicializa uma nova partícula de radiação.
        
        Args:
            x (float): Posição X inicial
            y (float): Posição Y inicial
        """
        self.pos = pygame.Vector2(x, y)
        # Define direção e velocidade aleatórias
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(RAD_PARTICLE_SPEED*0.5, RAD_PARTICLE_SPEED*1.5)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.uniform(RAD_PARTICLE_LIFETIME*0.5, RAD_PARTICLE_LIFETIME)
        self.age = 0.0
        self.size = random.randint(1, 3)

    def update(self, dt):
        """Atualiza a posição e idade da partícula.
        
        Args:
            dt (float): Delta time desde a última atualização
        """
        self.pos += self.vel * dt
        self.age += dt

    def is_dead(self):
        """Verifica se a partícula deve ser removida.
        
        Returns:
            bool: True se a partícula excedeu seu tempo de vida
        """
        return self.age >= self.life

    def draw(self, screen, camera):
        """Renderiza a partícula na tela.
        
        Args:
            screen (pygame.Surface): Superfície de renderização
            camera (Camera): Objeto câmera para ajuste de posição
        """
        alpha = max(0, 255 * (1 - self.age/self.life))
        if alpha<=0: return
        
        # Cria superfície para a partícula
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0,255,0,int(alpha)), (self.size, self.size), self.size)
        
        # Aplica transformação da câmera
        rect = pygame.Rect(
            int(self.pos.x-self.size),
            int(self.pos.y-self.size),
            self.size*2, self.size*2
        )
        screen.blit(surf, camera.apply(rect).topleft)

class RadiationSystem:
    """Gerenciador de partículas de radiação.
    
    Controla a criação, atualização e renderização de múltiplas
    partículas de radiação, criando efeitos visuais de áreas
    radioativas.
    
    Attributes:
        particles (list): Lista de partículas ativas
    """
    def __init__(self):
        """Inicializa o sistema de partículas."""
        self.particles = []

    def emit(self, x, y, count=10):
        """Adiciona novas partículas de radiação.
        
        Args:
            x (float): Posição X do efeito
            y (float): Posição Y do efeito
            count (int): Número de partículas a criar
        """
        for _ in range(count):
            self.particles.append(RadiationParticle(x, y))

    def update(self, dt):
        """Atualiza todas as partículas ativas.
        
        Args:
            dt (float): Delta time desde a última atualização
        """
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen, camera):
        """Renderiza todas as partículas ativas.
        
        Args:
            screen (pygame.Surface): Superfície de renderização
            camera (Camera): Objeto câmera para ajuste de posição
        """
        for p in self.particles: p.draw(screen, camera)
