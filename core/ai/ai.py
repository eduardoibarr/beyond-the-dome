import pygame
import random
import math  # Mantém a importação do módulo 'math' para cálculos de ângulo, se necessário mais tarde
from enum import Enum
from core.settings import *

# Certifica-se de que 'vec' está definido (geralmente pygame.math.Vector2)
vec = pygame.math.Vector2

# Enumeração dos estados possíveis da IA (Inteligência Artificial)
class AIState(Enum):
    IDLE = 1      # Estado de repouso - inimigo parado.
    PATROL = 2    # Estado de patrulha - movendo-se entre pontos aleatórios.
    CHASE = 3     # Estado de perseguição - seguindo o jogador.
    ATTACK = 4    # Estado de ataque - tentando causar dano ao jogador.
    SEARCH = 5    # Estado de busca - procurando o jogador após perdê-lo de vista.

# Classe base do controlador de IA (Inteligência Artificial)
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
        """Sets a new random target position within the patrol radius."""
        try:
            # Generate random angle and radius
            angle = random.uniform(0, 2 * math.pi) # Use math.pi
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
            self.enemy.set_animation('walk') # Use walk animation for patrol
            # Check if player is detected
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
                # print(f"Enemy at {enemy_pos} spotted player, switching to CHASE.")
            # Move towards patrol target
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

        # == SEARCH STATE ==
        elif self.state == AIState.SEARCH:
            self.enemy.set_animation('walk') # Use walk animation for search
            # Check if player is re-detected
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
                # print(f"Enemy at {enemy_pos} re-found player, switching to CHASE.")
            # Check if search timer expired
            elif now > self.search_start_time + ENEMY_SEARCH_DURATION:
                self.state = AIState.PATROL
                self.patrol_center = vec(enemy_pos) # Reset patrol center
                self.set_new_patrol_target()
                # print(f"Enemy at {enemy_pos} finished searching, returning to PATROL.")
            # Move towards last known player position
            elif self.target_position: # Target should be last_known_player_pos
                direction = self.target_position - enemy_pos
                dist_sq_to_target = direction.length_squared()
                search_speed = self.enemy.speed * 0.8 # Faster search speed

                if dist_sq_to_target < (search_speed * dt * 1.5)**2:
                    # Arrived at last known position, give up and patrol
                    self.state = AIState.PATROL
                    self.patrol_center = vec(enemy_pos)
                    self.set_new_patrol_target()
                    # print(f"Enemy at {enemy_pos} reached last known pos, returning to PATROL.")
                else:
                    new_velocity = direction.normalize() * search_speed
            else:
                 # No target? Should have one (last_known_player_pos). Go patrol.
                 self.state = AIState.PATROL
                 self.patrol_center = vec(enemy_pos)
                 self.set_new_patrol_target()

        # == CHASE STATE ==
        elif self.state == AIState.CHASE:  # Estado de perseguição
            self.enemy.set_animation('walk') # Use walk/run animation for chase
            # Check if player is lost
            if not can_see_player:
                self.state = AIState.SEARCH
                # Target becomes the last place player was seen
                self.target_position = self.last_known_player_pos
                self.search_start_time = now
                # print(f"Enemy at {enemy_pos} lost player, switching to SEARCH.")
            # Check if close enough to attack
            elif distance_sq_to_player < ENEMY_ATTACK_RADIUS**2:
                self.state = AIState.ATTACK # Entra em estado de ataque
                new_velocity = vec(0, 0) # Para de mover para atacar
                # print(f"Inimigo em {enemy_pos} está na área de ataque, mudando para ATAQUE.")
            # Continua perseguindo
            else:
                self.last_known_player_pos = player_pos # Update last known position
                direction = player_pos - enemy_pos
                # Usa velocidade total para perseguir
                new_velocity = direction.normalize() * self.enemy.speed

        # == ATTACK STATE ==
        elif self.state == AIState.ATTACK:
            self.enemy.set_animation('attack') # Use attack animation
            # Check if player moved out of range
            if distance_sq_to_player > (ENEMY_ATTACK_RADIUS * 1.2)**2: # Add hysteresis
                self.state = AIState.CHASE # Volta para perseguição
                self.last_known_player_pos = player_pos  # Atualiza a posição antes de perseguir novamente
                # print(f"Inimigo em {enemy_pos} jogador saiu da área, mudando para PERSEGUIR.")
            # Check attack cooldown
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

        # --- Apply Results ---
        # Define a velocidade calculada para o sprite do inimigo
        self.enemy.velocity = new_velocity

        # Retorna o sinalizador de ataque (o método de atualização do inimigo chamará sua função de ataque se True)
        return should_attack # Retorna se o inimigo deve atacar


# --- Specific AI Controllers ---

class RaiderAIController(AIController):
    """AI Controller specific to the Raider enemy."""
    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        # Raider specific parameters could be added here if needed
        # e.g., self.preferred_range = TILE_SIZE * 2

    def update(self, dt):
        """Raider's specific update logic."""
        # Call the base class update to handle state transitions and set velocity
        should_attack = super().update(dt)

        # Se a lógica base determinou que um ataque deve acontecer, diz ao sprite do inimigo
        if should_attack:
            if hasattr(self.enemy, 'attack'): # Check if enemy has attack method
                 self.enemy.attack() # Chama o método de ataque específico do Raider
            else:
                 print(f"Warning: {type(self.enemy).__name__} AI signaled attack, but sprite has no attack() method.")

        # Raider-specific behavior can be added here.
        # For example, maybe Raiders try to maintain a certain distance or use cover.
        # This currently uses the exact same logic as the base AIController.


class WildDogAIController(AIController):
    """AI Controller specific to the Wild Dog enemy."""
    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        # Wild Dogs might be faster or have different detection ranges
        # (These are currently set in the WildDog class itself via settings.py)
        # Example: Modify cooldown or attack range specifically for dogs
        # self.attack_cooldown = ENEMY_ATTACK_COOLDOWN * 0.8 # Faster attacks?

    def update(self, dt):
        """Wild Dog's specific update logic."""
        # Call the base class update
        should_attack = super().update(dt)

        # Trigger attack if needed
        if should_attack:
            if hasattr(self.enemy, 'attack'):
                 self.enemy.attack() # Chama o método de ataque do Wild Dog
            else:
                 print(f"Aviso: {type(self.enemy).__name__} AI sinalizou ataque, mas sprite não possui método attack().")

        # Add dog-specific behaviors here.
        # Exemplo: Movimento errático aleatório durante a perseguição?
        # if self.state == AIState.CHASE and random.random() < 0.1:
        #     # Adiciona um pequeno componente de velocidade perpendicular para zig-zag
        #     if self.enemy.velocity.length_squared() > 0:
        #          perp_vec = self.enemy.velocity.rotate(random.choice([-90, 90])) # Gira aleatoriamente -90 ou 90
        #          self.enemy.velocity += perp_vec * 0.2 # Adiciona pequeno componente zig-zag
