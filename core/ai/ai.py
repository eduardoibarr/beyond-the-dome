import pygame
import random
import math
from enum import Enum
from core.settings import *

vec = pygame.math.Vector2

class AIState(Enum):
    IDLE = 1      # Estado de repouso - inimigo parado.
    PATROL = 2    # Estado de patrulha - movendo-se entre pontos aleatórios.
    CHASE = 3     # Estado de perseguição - seguindo o jogador.
    ATTACK = 4    # Estado de ataque - tentando causar dano ao jogador.
    SEARCH = 5    # Estado de busca - procurando o jogador após perdê-lo de vista.

class AIController:
    """Classe base para controlar o comportamento do inimigo usando uma máquina de estados."""
    def __init__(self, enemy_sprite):
        # Inicialização do controlador
        self.enemy = enemy_sprite  # Referência ao sprite do inimigo que esta IA controla
        self.game = enemy_sprite.game  # Referência ao objeto principal do jogo
        self.state = AIState.PATROL    # Estado inicial é patrulha
        self.target_position = None    # Alvo de navegação atual (coordenadas do mundo)
        self.last_known_player_pos = None  # Última posição conhecida do jogador
        # Usa a posição inicial do inimigo como centro para patrulhar
        self.patrol_center = vec(self.enemy.position)
        self.last_attack_time = 0      # Timestamp da última tentativa de ataque
        self.search_start_time = 0     # Timestamp de quando o estado de busca começou
        self.set_new_patrol_target()   # Define o primeiro alvo de patrulha

    def alert_damage(self, source_pos):
        """Reage quando o inimigo sofre dano."""
        # Se não estiver já perseguindo ou atacando, muda para perseguir a fonte do dano
        if self.state not in [AIState.CHASE, AIState.ATTACK]:
            # print(f"Inimigo em {self.enemy.position} foi alertado, mudando para PERSEGUIR em direção a {source_pos}")
            self.state = AIState.CHASE
            self.last_known_player_pos = vec(source_pos)  # Armazena como Vector2
            self.target_position = self.last_known_player_pos

    def set_new_patrol_target(self):
        """Define uma nova posição alvo aleatória dentro do raio de patrulha."""
        try:
            # Gera ângulo e raio aleatórios
            angle = random.uniform(0, 2 * math.pi) # Usa math.pi
            radius = random.uniform(ENEMY_PATROL_RADIUS * 0.2, ENEMY_PATROL_RADIUS)  # Varia o raio
            # Calcula o vetor de deslocamento e adiciona ao centro da patrulha
            offset = vec(radius, 0).rotate_rad(angle)
            self.target_position = self.patrol_center + offset
            # Fixa a posição alvo para ficar dentro dos limites do mapa (opcional, mas boa prática)
            self.target_position.x = max(TILE_SIZE, min(MAP_WIDTH - TILE_SIZE, self.target_position.x))
            self.target_position.y = max(TILE_SIZE, min(MAP_HEIGHT - TILE_SIZE, self.target_position.y))
        except Exception as e:
            print(f"Erro ao definir alvo de patrulha: {e}")
            self.target_position = self.patrol_center  # Define como centro em caso de erro

    def update(self, dt):
        """
        Atualiza a máquina de estados da IA e determina as ações do inimigo.
        Este método deve normalmente definir a velocidade e o estado do inimigo.
        Args:
            dt (float): Tempo delta em segundos.
        """
        now = pygame.time.get_ticks()
        player_pos = vec(self.game.player.position)  # Usa a posição precisa do jogador
        enemy_pos = vec(self.enemy.position)
        distance_sq_to_player = enemy_pos.distance_squared_to(player_pos)  # Usa distância ao quadrado

        # --- Determina a Visibilidade do Jogador ---
        # Checagem básica de distância
        can_see_player = distance_sq_to_player < ENEMY_DETECT_RADIUS**2
        # TODO: Adicionar verificação de linha de visão (raycasting contra obstáculos) para detecção mais realista

        # --- Lógica da Máquina de Estados ---
        new_velocity = vec(0, 0)  # Velocidade a ser definida para o inimigo neste frame
        should_attack = False     # Flag para sinalizar a intenção de ataque

        # == ESTADO DE PATRULHA ==
        if self.state == AIState.PATROL:
            self.enemy.set_animation('walk') # Usa animação de caminhada para patrulha
            # Verifica se o jogador foi detectado
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
                # print(f"Inimigo em {enemy_pos} avistou jogador, mudando para PERSEGUIR.")
            # Move em direção ao alvo de patrulha
            elif self.target_position:
                direction = self.target_position - enemy_pos
                dist_sq_to_target = direction.length_squared()
                patrol_speed = self.enemy.speed * 0.6  # Velocidade de patrulha mais lenta

                if dist_sq_to_target < (patrol_speed * dt * 1.5)**2:  # Verifica se está perto o suficiente
                    self.set_new_patrol_target()  # Chegou, pega um novo alvo
                else:
                    new_velocity = direction.normalize() * patrol_speed
            else:
                # Sem alvo? Pega um.
                self.set_new_patrol_target() 

        # == ESTADO DE BUSCA ==
        elif self.state == AIState.SEARCH:
            self.enemy.set_animation('walk') # Usa animação de caminhada para busca
            # Verifica se o jogador foi reencontrado
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
                # print(f"Inimigo em {enemy_pos} reencontrou jogador, mudando para PERSEGUIR.")
            # Verifica se o tempo de busca expirou
            elif now > self.search_start_time + ENEMY_SEARCH_DURATION:
                self.state = AIState.PATROL
                self.patrol_center = vec(enemy_pos) # Reseta o centro de patrulha
                self.set_new_patrol_target()
                # print(f"Inimigo em {enemy_pos} terminou busca, retornando para PATRULHA.")
            # Move em direção à última posição conhecida do jogador
            elif self.target_position: # Alvo deve ser last_known_player_pos
                direction = self.target_position - enemy_pos
                dist_sq_to_target = direction.length_squared()
                search_speed = self.enemy.speed * 0.8 # Velocidade de busca mais rápida

                if dist_sq_to_target < (search_speed * dt * 1.5)**2:
                    # Chegou na última posição conhecida, desiste e volta a patrulhar
                    self.state = AIState.PATROL
                    self.patrol_center = vec(enemy_pos)
                    self.set_new_patrol_target()
                    # print(f"Inimigo em {enemy_pos} chegou na última posição conhecida, retornando para PATRULHA.")
                else:
                    new_velocity = direction.normalize() * search_speed
            else:
                 # Sem alvo? Deveria ter um (last_known_player_pos). Vai patrulhar.
                 self.state = AIState.PATROL
                 self.patrol_center = vec(enemy_pos)
                 self.set_new_patrol_target()

        # == ESTADO DE PERSEGUIÇÃO ==
        elif self.state == AIState.CHASE:  # Estado de perseguição
            self.enemy.set_animation('walk') # Usa animação de caminhada/corrida para perseguição
            # Verifica se perdeu o jogador
            if not can_see_player:
                self.state = AIState.SEARCH
                # Alvo se torna o último lugar onde o jogador foi visto
                self.target_position = self.last_known_player_pos
                self.search_start_time = now
                # print(f"Inimigo em {enemy_pos} perdeu o jogador, mudando para BUSCA.")
            # Verifica se está perto o suficiente para atacar
            elif distance_sq_to_player < ENEMY_ATTACK_RADIUS**2:
                self.state = AIState.ATTACK # Entra em estado de ataque
                new_velocity = vec(0, 0) # Para de mover para atacar
                # print(f"Inimigo em {enemy_pos} está na área de ataque, mudando para ATAQUE.")
            # Continua perseguindo
            else:
                self.last_known_player_pos = player_pos # Atualiza última posição conhecida
                direction = player_pos - enemy_pos
                # Usa velocidade total para perseguir
                new_velocity = direction.normalize() * self.enemy.speed

        # == ESTADO DE ATAQUE ==
        elif self.state == AIState.ATTACK:
            self.enemy.set_animation('attack') # Usa animação de ataque
            # Verifica se o jogador saiu do alcance
            if distance_sq_to_player > (ENEMY_ATTACK_RADIUS * 1.2)**2: # Adiciona histerese
                self.state = AIState.CHASE # Volta para perseguição
                self.last_known_player_pos = player_pos  # Atualiza a posição antes de perseguir novamente
                # print(f"Inimigo em {enemy_pos} jogador saiu da área, mudando para PERSEGUIR.")
            # Verifica cooldown do ataque
            elif now > self.last_attack_time + ENEMY_ATTACK_COOLDOWN:
                # Verifica o alcance novamente antes de atacar
                if distance_sq_to_player < ENEMY_ATTACK_RADIUS**2:
                    should_attack = True  # Sinaliza a intenção de atacar
                    self.last_attack_time = now
                    # print(f"Inimigo em {enemy_pos} realizando ataque.")
                else:
                    # Jogador moveu assim que o ataque estava pronto, volta para a perseguição
                    self.state = AIState.CHASE # Volta para a perseguição
                    self.last_known_player_pos = player_pos

            # Mantém a velocidade zero enquanto estiver no estado de ataque (ou adiciona lógica de strafing/recuo)
            new_velocity = vec(0, 0)

        # --- Aplica Resultados ---
        # Define a velocidade calculada para o sprite do inimigo
        self.enemy.velocity = new_velocity

        # Retorna o sinalizador de ataque (o método de atualização do inimigo chamará sua função de ataque se True)
        return should_attack # Retorna se o inimigo deve atacar

# --- Controladores de IA Específicos ---

class RaiderAIController(AIController):
    """Controlador de IA específico para o inimigo Raider."""
    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        # Parâmetros específicos do Raider podem ser adicionados aqui se necessário
        # ex: self.preferred_range = TILE_SIZE * 2

    def update(self, dt):
        """Lógica de atualização específica do Raider."""
        # Chama a atualização da classe base para lidar com transições de estado e definir velocidade
        should_attack = super().update(dt)

        # Se a lógica base determinou que um ataque deve acontecer, diz ao sprite do inimigo
        if should_attack:
            if hasattr(self.enemy, 'attack'): # Verifica se o inimigo tem método de ataque
                 self.enemy.attack() # Chama o método de ataque específico do Raider
            else:
                 print(f"Aviso: {type(self.enemy).__name__} IA sinalizou ataque, mas sprite não possui método attack().")

        # Comportamento específico do Raider pode ser adicionado aqui.
        # Por exemplo, talvez Raiders tentem manter certa distância ou usar cobertura.
        # Atualmente usa exatamente a mesma lógica do AIController base.

class WildDogAIController(AIController):
    """Controlador de IA específico para o inimigo Cão Selvagem."""
    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        # Cães Selvagens podem ser mais rápidos ou ter diferentes raios de detecção
        # (Estes são atualmente definidos na própria classe WildDog via settings.py)
        # Exemplo: Modificar cooldown ou alcance de ataque especificamente para cães
        # self.attack_cooldown = ENEMY_ATTACK_COOLDOWN * 0.8 # Ataques mais rápidos?

    def update(self, dt):
        """Lógica de atualização específica do Cão Selvagem."""
        # Chama a atualização da classe base
        should_attack = super().update(dt)

        # Dispara ataque se necessário
        if should_attack:
            if hasattr(self.enemy, 'attack'):
                 self.enemy.attack() # Chama o método de ataque do Cão Selvagem
            else:
                 print(f"Aviso: {type(self.enemy).__name__} IA sinalizou ataque, mas sprite não possui método attack().")

        # Adiciona comportamentos específicos de cão aqui.
        # Exemplo: Movimento errático aleatório durante a perseguição?
        # if self.state == AIState.CHASE and random.random() < 0.1:
        #     # Adiciona um pequeno componente de velocidade perpendicular para zig-zag
        #     if self.enemy.velocity.length_squared() > 0:
        #          perp_vec = self.enemy.velocity.rotate(random.choice([-90, 90])) # Gira aleatoriamente -90 ou 90
        #          self.enemy.velocity += perp_vec * 0.2 # Adiciona pequeno componente zig-zag
