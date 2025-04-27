# Importação das bibliotecas necessárias
import pygame
import random
from enum import Enum
from settings import *

# Definição do vetor para cálculos de posição
vec = pygame.math.Vector2

# Enumeração dos estados possíveis da IA
class AIState(Enum):
    IDLE = 1      # Estado de repouso - inimigo parado
    PATROL = 2    # Estado de patrulha - movendo-se entre pontos aleatórios
    CHASE = 3     # Estado de perseguição - seguindo o jogador
    ATTACK = 4    # Estado de ataque - tentando causar dano ao jogador
    SEARCH = 5    # Estado de busca - procurando o jogador após perdê-lo de vista

# Classe base do controlador de IA
class AIController:
    def __init__(self, enemy_sprite):
        # Inicialização do controlador
        self.enemy = enemy_sprite
        self.game = enemy_sprite.game
        self.state = AIState.PATROL  # Estado inicial é patrulha
        self.target_position = None  # Posição atual do alvo
        self.last_known_player_pos = None  # Última posição conhecida do jogador
        self.patrol_center = vec(self.enemy.pos)  # Centro da área de patrulha
        self.last_attack_time = 0  # Tempo do último ataque
        self.search_start_time = 0  # Tempo de início da busca
        self.set_new_patrol_target()  # Define primeiro alvo de patrulha

    def alert_damage(self, player_pos):
        # Reação ao receber dano do jogador
        if self.state != AIState.ATTACK and self.state != AIState.CHASE:
            print(f"Inimigo em {self.enemy.pos} alertado sobre dano, mudando para CHASE")
            self.state = AIState.CHASE  # Muda para estado de perseguição
            self.last_known_player_pos = player_pos  # Atualiza última posição conhecida
            self.target_position = player_pos  # Define jogador como alvo

    def set_new_patrol_target(self):
        # Define um novo alvo aleatório para patrulha
        angle = random.uniform(0, 2 * 3.14159)  # Ângulo aleatório em radianos
        radius = random.uniform(0, ENEMY_PATROL_RADIUS)  # Distância aleatória do centro
        # Calcula nova posição baseada no ângulo e raio
        self.target_position = self.patrol_center + vec(radius * pygame.math.Vector2(1, 0).rotate_rad(angle))

    def move_towards_target(self, target_pos, speed):
        # Movimenta o inimigo em direção ao alvo
        if not target_pos:
            return False

        # Calcula direção e distância ao alvo
        direction = target_pos - self.enemy.pos
        dist_sq = direction.length_squared()
        threshold_sq = speed * speed * 1.1  # Distância mínima para considerar que chegou

        # Se estiver próximo o suficiente, retorna True
        if dist_sq < threshold_sq:
            return True
        else:
            # Move o inimigo na direção do alvo
            move_vec = direction.normalize() * speed
            self.enemy.move(move_vec.x, move_vec.y)
            return False

    def update(self):
        # Atualização do estado da IA
        now = pygame.time.get_ticks()
        player_pos = vec(self.game.player.rect.center)
        enemy_pos = self.enemy.pos
        distance_to_player = enemy_pos.distance_to(player_pos)

        # Verifica se o inimigo pode ver o jogador
        can_see_player = distance_to_player < ENEMY_DETECT_RADIUS

        # Lógica de estados
        if self.state == AIState.PATROL:
            # Se avistar o jogador durante patrulha, começa a perseguição
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            # Se chegou ao alvo de patrulha, define novo alvo
            elif self.move_towards_target(self.target_position, self.enemy.speed * 0.5):
                self.set_new_patrol_target()

        elif self.state == AIState.SEARCH:
            # Se encontrar o jogador durante busca, começa perseguição
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            # Se tempo de busca expirou, volta a patrulhar
            elif now > self.search_start_time + ENEMY_SEARCH_DURATION:
                self.state = AIState.PATROL
                self.patrol_center = vec(self.enemy.pos)
                self.set_new_patrol_target()
            # Se chegou ao último local conhecido, volta a patrulhar
            elif self.move_towards_target(self.target_position, self.enemy.speed * 0.75):
                self.state = AIState.PATROL
                self.patrol_center = vec(self.enemy.pos)
                self.set_new_patrol_target()

        elif self.state == AIState.CHASE:
            # Se perder o jogador de vista, começa busca
            if not can_see_player:
                self.state = AIState.SEARCH
                self.target_position = self.last_known_player_pos
                self.search_start_time = now
            # Se chegar perto o suficiente, começa ataque
            elif distance_to_player < ENEMY_ATTACK_RADIUS:
                self.state = AIState.ATTACK
            else:
                # Continua perseguindo o jogador
                self.last_known_player_pos = player_pos
                self.move_towards_target(player_pos, self.enemy.speed)

        elif self.state == AIState.ATTACK:
            # Se jogador se afastar, volta a perseguir
            if distance_to_player > ENEMY_ATTACK_RADIUS * 1.1:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            # Se cooldown do ataque acabou, tenta atacar
            elif now > self.last_attack_time + ENEMY_ATTACK_COOLDOWN:
                if enemy_pos.distance_to(player_pos) < ENEMY_ATTACK_RADIUS * 1.1:
                    self.game.player.take_damage(self.enemy.damage)
                    self.last_attack_time = now
                else:
                    self.state = AIState.CHASE
                    self.last_known_player_pos = player_pos

# Controlador de IA específico para o Saqueador
class RaiderAIController(AIController):
    def __init__(self, enemy_sprite):
        # Inicialização do controlador do Saqueador
        super().__init__(enemy_sprite)
        self.enemy = enemy_sprite
        self.speed = ENEMY_RAIDER_SPEED  # Velocidade específica do Saqueador
        
    def update(self, player):
        # Atualização do estado do Saqueador
        now = pygame.time.get_ticks()
        player_pos = vec(player.rect.center)
        enemy_pos = vec(self.enemy.rect.center)
        distance_to_player = enemy_pos.distance_to(player_pos)
        
        dx, dy = 0, 0  # Deslocamento em x e y
        should_attack = False  # Flag para indicar se deve atacar
        
        # Verifica se pode ver o jogador
        can_see_player = distance_to_player < ENEMY_DETECT_RADIUS
        
        # Lógica de estados específica do Saqueador
        if self.state == AIState.PATROL:
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            elif self.target_position:
                # Calcula direção para o alvo de patrulha
                direction = self.target_position - enemy_pos
                if direction.length_squared() > self.speed * self.speed:
                    direction = direction.normalize() * self.speed
                    dx, dy = direction.x, direction.y
                else:
                    self.set_new_patrol_target()
                    
        elif self.state == AIState.SEARCH:
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            elif now > self.search_start_time + ENEMY_SEARCH_DURATION:
                self.state = AIState.PATROL
                self.patrol_center = vec(enemy_pos)
                self.set_new_patrol_target()
            elif self.target_position:
                # Move-se em direção ao último local conhecido do jogador
                direction = self.target_position - enemy_pos
                if direction.length_squared() > self.speed * self.speed:
                    direction = direction.normalize() * self.speed * 0.75
                    dx, dy = direction.x, direction.y
                else:
                    self.state = AIState.PATROL
                    self.patrol_center = vec(enemy_pos)
                    self.set_new_patrol_target()
                    
        elif self.state == AIState.CHASE:
            if not can_see_player:
                self.state = AIState.SEARCH
                self.target_position = self.last_known_player_pos
                self.search_start_time = now
            elif distance_to_player < ENEMY_ATTACK_RADIUS:
                self.state = AIState.ATTACK
            else:
                # Persegue o jogador
                self.last_known_player_pos = player_pos
                direction = player_pos - enemy_pos
                direction = direction.normalize() * self.speed
                dx, dy = direction.x, direction.y
                
        elif self.state == AIState.ATTACK:
            if distance_to_player > ENEMY_ATTACK_RADIUS * 1.1:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            elif now > self.last_attack_time + ENEMY_ATTACK_COOLDOWN:
                if distance_to_player < ENEMY_ATTACK_RADIUS * 1.1:
                    should_attack = True
                    self.last_attack_time = now
                else:
                    self.state = AIState.CHASE
                    self.last_known_player_pos = player_pos
                    
        return dx, dy, should_attack

# Controlador de IA específico para o Cão Selvagem
class WildDogAIController(AIController):
     def __init__(self, enemy_sprite):
        # Inicialização do controlador do Cão Selvagem
        super().__init__(enemy_sprite)
