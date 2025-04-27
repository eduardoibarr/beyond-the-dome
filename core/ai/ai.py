import pygame
import random
import math # Keep math import for angle calculations if needed later
from enum import Enum
from settings import *

# Make sure vec is defined (usually pygame.math.Vector2)
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
    """Base class for controlling enemy behavior using a state machine."""
    def __init__(self, enemy_sprite):
        # Inicialização do controlador
        self.enemy = enemy_sprite # Reference to the enemy sprite this AI controls
        self.game = enemy_sprite.game # Reference to the main game object
        self.state = AIState.PATROL   # Estado inicial é patrulha
        self.target_position = None   # Current navigation target (world coordinates)
        self.last_known_player_pos = None # Last seen player position
        # Use enemy's initial position as the center for patrolling
        self.patrol_center = vec(self.enemy.position)
        self.last_attack_time = 0     # Timestamp of the last attack attempt
        self.search_start_time = 0    # Timestamp when search state began
        self.set_new_patrol_target()  # Define primeiro alvo de patrulha

    def alert_damage(self, source_pos):
        """Reacts when the enemy takes damage."""
        # If not already chasing or attacking, switch to chase the source of damage
        if self.state not in [AIState.CHASE, AIState.ATTACK]:
            # print(f"Enemy at {self.enemy.position} alerted, switching to CHASE towards {source_pos}")
            self.state = AIState.CHASE
            self.last_known_player_pos = vec(source_pos) # Store as Vector2
            self.target_position = self.last_known_player_pos

    def set_new_patrol_target(self):
        """Sets a new random target position within the patrol radius."""
        try:
            # Generate random angle and radius
            angle = random.uniform(0, 2 * math.pi) # Use math.pi
            radius = random.uniform(ENEMY_PATROL_RADIUS * 0.2, ENEMY_PATROL_RADIUS) # Vary radius
            # Calculate offset vector and add to patrol center
            offset = vec(radius, 0).rotate_rad(angle)
            self.target_position = self.patrol_center + offset
            # Clamp target position to stay within map bounds (optional but good practice)
            self.target_position.x = max(TILE_SIZE, min(MAP_WIDTH - TILE_SIZE, self.target_position.x))
            self.target_position.y = max(TILE_SIZE, min(MAP_HEIGHT - TILE_SIZE, self.target_position.y))
        except Exception as e:
            print(f"Error setting patrol target: {e}")
            self.target_position = self.patrol_center # Default to center if error

    def update(self, dt):
        """
        Updates the AI state machine and determines enemy actions.
        This method should typically set the enemy's velocity and state.
        Args:
            dt (float): Delta time in seconds.
        """
        now = pygame.time.get_ticks()
        player_pos = vec(self.game.player.position) # Use player's precise position
        enemy_pos = vec(self.enemy.position)
        distance_sq_to_player = enemy_pos.distance_squared_to(player_pos) # Use squared distance

        # --- Determine Player Visibility ---
        # Basic distance check
        can_see_player = distance_sq_to_player < ENEMY_DETECT_RADIUS**2
        # TODO: Add line-of-sight check (raycasting against obstacles) for more realistic detection

        # --- State Machine Logic ---
        new_velocity = vec(0, 0) # Velocity to be set for the enemy this frame
        should_attack = False    # Flag to signal attack intention

        # == PATROL STATE ==
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
                patrol_speed = self.enemy.speed * 0.6 # Slower patrol speed

                if dist_sq_to_target < (patrol_speed * dt * 1.5)**2: # Check if close enough
                    self.set_new_patrol_target() # Arrived, get new target
                else:
                    new_velocity = direction.normalize() * patrol_speed
            else:
                # No target? Get one.
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
        elif self.state == AIState.CHASE:
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
                self.state = AIState.ATTACK
                new_velocity = vec(0, 0) # Stop moving to attack
                # print(f"Enemy at {enemy_pos} in attack range, switching to ATTACK.")
            # Continue chasing
            else:
                self.last_known_player_pos = player_pos # Update last known position
                direction = player_pos - enemy_pos
                # Use full speed for chasing
                new_velocity = direction.normalize() * self.enemy.speed

        # == ATTACK STATE ==
        elif self.state == AIState.ATTACK:
            self.enemy.set_animation('attack') # Use attack animation
            # Check if player moved out of range
            if distance_sq_to_player > (ENEMY_ATTACK_RADIUS * 1.2)**2: # Add hysteresis
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos # Update pos before chasing again
                # print(f"Enemy at {enemy_pos} player moved out of range, switching to CHASE.")
            # Check attack cooldown
            elif now > self.last_attack_time + ENEMY_ATTACK_COOLDOWN:
                # Check range again before attacking
                if distance_sq_to_player < ENEMY_ATTACK_RADIUS**2:
                    should_attack = True # Signal intent to attack
                    self.last_attack_time = now
                    # print(f"Enemy at {enemy_pos} performing attack.")
                else:
                    # Player moved just as attack was ready, go back to chase
                    self.state = AIState.CHASE
                    self.last_known_player_pos = player_pos

            # Keep velocity zero while in attack state (or add strafing/backing up logic)
            new_velocity = vec(0, 0)

        # --- Apply Results ---
        # Set the calculated velocity for the enemy sprite
        self.enemy.velocity = new_velocity

        # Return attack flag (Enemy's update method will call its attack function if True)
        return should_attack


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

        # If the base logic determined an attack should happen, tell the enemy sprite
        if should_attack:
            if hasattr(self.enemy, 'attack'): # Check if enemy has attack method
                 self.enemy.attack() # Call the Raider's specific attack method
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
                 self.enemy.attack()
            else:
                 print(f"Warning: {type(self.enemy).__name__} AI signaled attack, but sprite has no attack() method.")

        # Add dog-specific behaviors here.
        # Example: Random erratic movement during chase?
        # if self.state == AIState.CHASE and random.random() < 0.1:
        #     # Add a small perpendicular velocity component for zig-zag
        #     if self.enemy.velocity.length_squared() > 0:
        #          perp_vec = self.enemy.velocity.rotate(random.choice([-90, 90]))
        #          self.enemy.velocity += perp_vec * 0.2 # Add small zig-zag component
