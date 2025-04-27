# Importação das bibliotecas necessárias
import pygame
import math
from core.settings import * # Assumindo que settings.py está no mesmo diretório

# Classe da Bala (projétil)
class Bullet(pygame.sprite.Sprite):
    """Representa um projétil de bala disparado pelo jogador."""
    def __init__(self, game, start_pos, direction, speed):
        """
        Inicializa o sprite da Bala.
        Args:
            game (Game): Referência ao objeto principal do jogo.
            start_pos (tuple or pygame.math.Vector2): Posição inicial (x, y) nas coordenadas do mundo.
            direction (pygame.math.Vector2): Vetor de direção normalizado para a bala.
            speed (float): A velocidade da bala em pixels por segundo.
        """
        # self._layer = 4 # Camada do projétil
        self.groups = game.all_sprites, game.bullets # Usa um novo grupo para balas
        super().__init__(self.groups)
        self.game = game

        # --- Posição e Movimento ---
        self.pos = pygame.math.Vector2(start_pos)
        if direction.length_squared() > 0:
             self.direction = direction.normalize()
        else:
             self.direction = pygame.math.Vector2(1, 0) # Direção padrão

        # Armazena o ângulo para rotação
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))

        self.speed = speed
        self.velocity = self.direction * self.speed
        self.spawn_time = pygame.time.get_ticks()

        # --- Aparência ---
        # Cria uma imagem base (retângulo horizontal)
        self.base_image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        self.base_image.fill(BULLET_COLOR)
        # Rotaciona a imagem base de acordo com a direção
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        # --- Combate ---
        self.damage = BULLET_DAMAGE

    def update(self, dt):
        """
        Atualiza a posição da bala e verifica tempo de vida/limites/colisões.
        Args:
            dt (float): Delta time em segundos.
        """
        # --- Verificação de Tempo de Vida ---
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
            return

        # --- Movimento ---
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # --- Verificação de Limites (Limites do Mapa) ---
        buffer = TILE_SIZE
        if (self.pos.x < -buffer or self.pos.x > MAP_WIDTH + buffer or
            self.pos.y < -buffer or self.pos.y > MAP_HEIGHT + buffer):
            self.kill()
            return

        # --- Tratamento de Colisões (Verifica contra obstáculos e inimigos) ---
        self.check_collisions()

    def check_collisions(self):
        """Verifica colisões com obstáculos e inimigos."""
        # Verifica obstáculos primeiro
        obstacle_hits = pygame.sprite.spritecollide(self, self.game.obstacles, False)
        if obstacle_hits:
            self.kill() # Bala atinge uma parede
            # TODO: Adicionar efeito/som de impacto?
            return

        # Verifica inimigos
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in enemy_hits:
            if hasattr(enemy, 'take_damage'):
                enemy.take_damage(self.damage)
            self.kill() # Bala é destruída ao atingir
            # TODO: Adicionar efeito/som de acerto?
            return # Sai após o primeiro acerto
