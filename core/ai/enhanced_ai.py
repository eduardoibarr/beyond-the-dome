import pygame
import random
import math
from enum import Enum
from core.settings import *

vec = pygame.math.Vector2

class AIState(Enum):
    IDLE = 1
    PATROL = 2
    CHASE = 3
    ATTACK = 4
    SEARCH = 5
    WANDER = 6
    INVESTIGATE = 7

class AIPersonality(Enum):
    AGGRESSIVE = 1
    CAUTIOUS = 2
    LAZY = 3
    ERRATIC = 4

class EnhancedAIController:

    def __init__(self, enemy_sprite):
        self.enemy = enemy_sprite
        self.game = enemy_sprite.game
        self.state = AIState.WANDER
        self.previous_state = AIState.WANDER

        self.target_position = None
        self.last_known_player_pos = None
        self.patrol_center = vec(self.enemy.position)
        self.patrol_points = []
        self.current_patrol_index = 0

        self.last_attack_time = 0
        self.search_start_time = 0
        self.state_change_time = 0
        self.last_decision_time = 0
        self.idle_timer = 0
        self.wander_timer = 0

        self.personality = random.choice(list(AIPersonality))
        self.alertness = random.uniform(0.3, 1.0)
        self.aggression = random.uniform(0.2, 1.0)
        self.patience = random.uniform(0.5, 2.0)
        self.curiosity = random.uniform(0.1, 0.8)

        self.decision_interval = random.uniform(1.0, 3.0)
        self.random_action_chance = 0.1
        self.direction_change_timer = 0
        self.preferred_distance = random.uniform(50, 150)

        self.is_confused = False
        self.confusion_timer = 0
        self.last_player_direction = vec(0, 0)
        self.stuck_timer = 0
        self.last_position = vec(self.enemy.position)

        self._generate_patrol_points()
        self._set_personality_traits()
        self.set_new_wander_target()

    def _set_personality_traits(self):
        if self.personality == AIPersonality.AGGRESSIVE:
            self.aggression *= 1.5
            self.patience *= 1.3
            self.alertness *= 1.2
            self.decision_interval *= 0.7
        elif self.personality == AIPersonality.CAUTIOUS:
            self.aggression *= 0.6
            self.patience *= 0.8
            self.alertness *= 1.4
            self.curiosity *= 1.3
        elif self.personality == AIPersonality.LAZY:
            self.aggression *= 0.4
            self.patience *= 0.5
            self.alertness *= 0.7
            self.decision_interval *= 1.5
        elif self.personality == AIPersonality.ERRATIC:
            self.random_action_chance = 0.25
            self.decision_interval *= random.uniform(0.3, 2.0)

    def _generate_patrol_points(self):
        num_points = random.randint(3, 6)
        for _ in range(num_points):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(ENEMY_PATROL_RADIUS * 0.3, ENEMY_PATROL_RADIUS)
            offset = vec(radius, 0).rotate_rad(angle)
            point = self.patrol_center + offset

            point.x = max(TILE_SIZE, min(MAP_WIDTH - TILE_SIZE, point.x))
            point.y = max(TILE_SIZE, min(MAP_HEIGHT - TILE_SIZE, point.y))
            self.patrol_points.append(point)

    def set_new_wander_target(self):

        current_direction = getattr(self, 'last_direction', vec(1, 0))

        if random.random() < 0.4:
            angle_offset = random.uniform(-math.pi/4, math.pi/4)
        else:
            angle_offset = random.uniform(-math.pi, math.pi)

        new_direction = current_direction.rotate_rad(angle_offset)
        distance = random.uniform(50, 200)

        self.target_position = vec(self.enemy.position) + new_direction * distance

        self.target_position.x = max(TILE_SIZE, min(MAP_WIDTH - TILE_SIZE, self.target_position.x))
        self.target_position.y = max(TILE_SIZE, min(MAP_HEIGHT - TILE_SIZE, self.target_position.y))

        self.last_direction = new_direction
        self.wander_timer = random.uniform(2.0, 8.0)

    def _check_if_stuck(self, dt):
        current_pos = vec(self.enemy.position)
        if current_pos.distance_to(self.last_position) < 5:
            self.stuck_timer += dt
            if self.stuck_timer > 2.0:

                self.set_new_wander_target()
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.last_position = current_pos

    def _should_make_random_decision(self, dt):
        self.last_decision_time += dt
        if self.last_decision_time >= self.decision_interval:
            self.last_decision_time = 0
            self.decision_interval = random.uniform(1.0, 4.0)
            return random.random() < self.random_action_chance
        return False

    def _handle_confusion(self, dt):
        if self.is_confused:
            self.confusion_timer -= dt
            if self.confusion_timer <= 0:
                self.is_confused = False
                return False

            if random.random() < 0.3:
                self.set_new_wander_target()
            return True
        return False

    def _get_speed_modifier(self):
        base_modifier = 1.0

        if self.state == AIState.WANDER:
            base_modifier = 0.4
        elif self.state == AIState.PATROL:
            base_modifier = 0.6
        elif self.state == AIState.SEARCH:
            base_modifier = 0.8
        elif self.state == AIState.CHASE:
            base_modifier = 1.0
        elif self.state == AIState.INVESTIGATE:
            base_modifier = 0.5
        elif self.state == AIState.IDLE:
            base_modifier = 0.0

        if self.personality == AIPersonality.AGGRESSIVE:
            base_modifier *= 1.2
        elif self.personality == AIPersonality.LAZY:
            base_modifier *= 0.7
        elif self.personality == AIPersonality.ERRATIC:
            base_modifier *= random.uniform(0.5, 1.5)

        return base_modifier

    def alert_damage(self, source_pos):
        self.is_confused = True
        self.confusion_timer = random.uniform(0.5, 2.0)

        if self.personality == AIPersonality.AGGRESSIVE:
            self.state = AIState.CHASE
            self.last_known_player_pos = vec(source_pos)
        elif self.personality == AIPersonality.CAUTIOUS:
            self.state = AIState.INVESTIGATE
            self.target_position = vec(source_pos)
        else:
            if random.random() < self.aggression:
                self.state = AIState.CHASE
                self.last_known_player_pos = vec(source_pos)
            else:
                self.state = AIState.SEARCH
                self.target_position = vec(source_pos)
                self.search_start_time = pygame.time.get_ticks()

    def update(self, dt):
        now = pygame.time.get_ticks()
        player_pos = vec(self.game.player.position)
        enemy_pos = vec(self.enemy.position)
        distance_to_player = enemy_pos.distance_to(player_pos)

        self._check_if_stuck(dt)

        if self._handle_confusion(dt):
            return False

        detection_radius = ENEMY_DETECT_RADIUS * self.alertness
        can_see_player = distance_to_player < detection_radius

        if self._should_make_random_decision(dt):
            self._make_random_decision()

        new_velocity = vec(0, 0)
        should_attack = False

        if self.state == AIState.IDLE:
            self._handle_idle_state(dt, can_see_player, player_pos)

        elif self.state == AIState.WANDER:
            new_velocity = self._handle_wander_state(dt, can_see_player, player_pos, enemy_pos)

        elif self.state == AIState.PATROL:
            new_velocity = self._handle_patrol_state(dt, can_see_player, player_pos, enemy_pos)

        elif self.state == AIState.INVESTIGATE:
            new_velocity = self._handle_investigate_state(dt, can_see_player, player_pos, enemy_pos)

        elif self.state == AIState.SEARCH:
            new_velocity = self._handle_search_state(dt, can_see_player, player_pos, enemy_pos, now)

        elif self.state == AIState.CHASE:
            new_velocity = self._handle_chase_state(dt, can_see_player, player_pos, enemy_pos, distance_to_player, now)

        elif self.state == AIState.ATTACK:
            should_attack = self._handle_attack_state(dt, can_see_player, player_pos, enemy_pos, distance_to_player, now)

        speed_modifier = self._get_speed_modifier()
        self.enemy.velocity = new_velocity * speed_modifier

        return should_attack

    def _handle_idle_state(self, dt, can_see_player, player_pos):
        self.idle_timer += dt

        if can_see_player and random.random() < self.alertness:
            self.state = AIState.CHASE
            self.last_known_player_pos = player_pos
        elif self.idle_timer > random.uniform(2.0, 8.0):
            self.state = random.choice([AIState.WANDER, AIState.PATROL])
            self.idle_timer = 0

    def _handle_wander_state(self, dt, can_see_player, player_pos, enemy_pos):
        self.enemy.set_animation('walk')

        if can_see_player and random.random() < self.alertness:
            if self.personality == AIPersonality.CAUTIOUS:
                self.state = AIState.INVESTIGATE
                self.target_position = player_pos
            else:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            return vec(0, 0)

        self.wander_timer -= dt

        if self.target_position:
            direction = self.target_position - enemy_pos
            if direction.length() < 20 or self.wander_timer <= 0:
                self.set_new_wander_target()

                if random.random() < 0.2:
                    self.state = AIState.IDLE
                    return vec(0, 0)
            else:
                return direction.normalize() * self.enemy.speed
        else:
            self.set_new_wander_target()

        return vec(0, 0)

    def _handle_patrol_state(self, dt, can_see_player, player_pos, enemy_pos):
        self.enemy.set_animation('walk')

        if can_see_player and random.random() < self.alertness:
            self.state = AIState.CHASE
            self.last_known_player_pos = player_pos
            return vec(0, 0)

        if self.patrol_points:
            target = self.patrol_points[self.current_patrol_index]
            direction = target - enemy_pos

            if direction.length() < 30:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)

                if random.random() < 0.3:
                    self.state = AIState.IDLE
                    return vec(0, 0)
            else:
                return direction.normalize() * self.enemy.speed
        else:
            self.state = AIState.WANDER

        return vec(0, 0)

    def _handle_investigate_state(self, dt, can_see_player, player_pos, enemy_pos):
        self.enemy.set_animation('walk')

        if can_see_player:
            if random.random() < self.aggression:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            else:

                pass
            return vec(0, 0)

        if self.target_position:
            direction = self.target_position - enemy_pos
            if direction.length() < 40:

                self.state = AIState.SEARCH
                self.search_start_time = pygame.time.get_ticks()
                return vec(0, 0)
            else:
                return direction.normalize() * self.enemy.speed * 0.7
        else:
            self.state = AIState.WANDER

        return vec(0, 0)

    def _handle_search_state(self, dt, can_see_player, player_pos, enemy_pos, now):
        self.enemy.set_animation('walk')

        if can_see_player:
            self.state = AIState.CHASE
            self.last_known_player_pos = player_pos
            return vec(0, 0)

        search_duration = ENEMY_SEARCH_DURATION * self.patience
        if now > self.search_start_time + search_duration:
            self.state = random.choice([AIState.WANDER, AIState.PATROL])
            return vec(0, 0)

        if random.random() < 0.1:
            self.set_new_wander_target()

        if self.target_position:
            direction = self.target_position - enemy_pos
            if direction.length() < 30:
                self.set_new_wander_target()
            else:
                return direction.normalize() * self.enemy.speed * 0.8

        return vec(0, 0)

    def _handle_chase_state(self, dt, can_see_player, player_pos, enemy_pos, distance_to_player, now):
        self.enemy.set_animation('walk')

        if not can_see_player:
            self.state = AIState.SEARCH
            self.target_position = self.last_known_player_pos
            self.search_start_time = now
            return vec(0, 0)

        if distance_to_player < ENEMY_ATTACK_RADIUS:
            self.state = AIState.ATTACK
            return vec(0, 0)

        self.last_known_player_pos = player_pos

        direction = player_pos - enemy_pos

        if self.personality == AIPersonality.ERRATIC:

            if random.random() < 0.2:
                perpendicular = direction.rotate(90).normalize()
                direction += perpendicular * random.uniform(-0.5, 0.5)
        elif self.personality == AIPersonality.CAUTIOUS:

            if distance_to_player < self.preferred_distance:
                direction = -direction

        return direction.normalize() * self.enemy.speed

    def _handle_attack_state(self, dt, can_see_player, player_pos, enemy_pos, distance_to_player, now):
        self.enemy.set_animation('attack')

        if distance_to_player > ENEMY_ATTACK_RADIUS * 1.2:
            self.state = AIState.CHASE
            self.last_known_player_pos = player_pos
            return False

        if now > self.last_attack_time + ENEMY_ATTACK_COOLDOWN:
            if distance_to_player < ENEMY_ATTACK_RADIUS:
                self.last_attack_time = now
                return True

        return False

    def _make_random_decision(self):
        if self.personality == AIPersonality.ERRATIC:

            possible_states = [AIState.WANDER, AIState.PATROL, AIState.IDLE]
            if self.state in possible_states:
                new_state = random.choice([s for s in possible_states if s != self.state])
                self.state = new_state
        elif random.random() < 0.1:

            if self.state in [AIState.WANDER, AIState.PATROL]:
                self.state = AIState.IDLE

class EnhancedRaiderAI(EnhancedAIController):

    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        self.personality = AIPersonality.AGGRESSIVE
        self.aggression *= 1.3
        self.alertness *= 1.1
        self._set_personality_traits()

    def update(self, dt):
        should_attack = super().update(dt)
        if should_attack and hasattr(self.enemy, 'attack'):
            self.enemy.attack()
        return should_attack

class EnhancedWildDogAI(EnhancedAIController):

    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        self.personality = AIPersonality.ERRATIC
        self.random_action_chance = 0.3
        self.decision_interval *= 0.5
        self._set_personality_traits()

    def update(self, dt):
        should_attack = super().update(dt)
        if should_attack and hasattr(self.enemy, 'attack'):
            self.enemy.attack()
        return should_attack

    def _handle_chase_state(self, dt, can_see_player, player_pos, enemy_pos, distance_to_player, now):
        base_velocity = super()._handle_chase_state(dt, can_see_player, player_pos, enemy_pos, distance_to_player, now)

        if base_velocity.length() > 0 and random.random() < 0.3:
            perpendicular = base_velocity.rotate(random.choice([-90, 90])).normalize()
            base_velocity += perpendicular * random.uniform(0.2, 0.5) * self.enemy.speed

        return base_velocity

class EnhancedFriendlyScavengerAI(EnhancedAIController):

    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
        self.personality = AIPersonality.CAUTIOUS
        self.aggression *= 0.3
        self.alertness *= 1.4
        self._set_personality_traits()
        
        self.interaction_state = "GREETING"
        self.trade_completed = False
        self.has_become_hostile = False
        
        self.dialogue = {
            "greeting": "Ei, calma! Não atire! Estou só tentando sobreviver como você.",
            "proposal": "Tenho uma máscara reforçada aqui. Posso trocar por um pente de munição. Topa? [Y]es / [N]o",
            "accept_trade": "Ótimo negócio! Aqui está sua máscara. Esta munição vai me ajudar bastante.",
            "refuse_trade": "Tudo bem, entendo. Boa sorte lá fora.",
            "hostile_trigger": "Ei! Por que fez isso?!",
            "post_trade": "Já negociamos. Siga seu caminho.",
            "no_ammo": "Você não tem munição suficiente, volte quando tiver um pente completo."
        }
        self.current_dialogue = ""

    def update(self, dt):
        if self.state == AIState.CHASE or self.state == AIState.ATTACK or self.has_become_hostile:
            should_attack = super().update(dt)
            if should_attack and random.random() < 0.1:
                if hasattr(self.enemy, 'attack'):
                    self.enemy.attack()
            return False
        
        self.enemy.velocity = pygame.math.Vector2(0, 0)
        
        player_pos = pygame.math.Vector2(self.game.player.position)
        enemy_pos = pygame.math.Vector2(self.enemy.position)
        distance_to_player = enemy_pos.distance_to(player_pos)
        
        interaction_distance = TILE_SIZE * 3
        if distance_to_player < interaction_distance:
            if self.interaction_state == "GREETING":
                self.current_dialogue = self.dialogue["greeting"]
            elif self.interaction_state == "PROPOSAL":
                self.current_dialogue = self.dialogue["proposal"]
            elif self.interaction_state == "ACCEPT":
                self.current_dialogue = self.dialogue["accept_trade"]
            elif self.interaction_state == "REFUSE":
                self.current_dialogue = self.dialogue["refuse_trade"]
            elif self.interaction_state == "POST_TRADE":
                self.current_dialogue = self.dialogue["post_trade"]
            elif self.interaction_state == "NO_AMMO":
                self.current_dialogue = self.dialogue["no_ammo"]
        else:
            self.current_dialogue = ""
        
        return False

    def alert_damage(self, source_pos):
        if not self.has_become_hostile:
            self.has_become_hostile = True
            self.state = AIState.CHASE
            self.last_known_player_pos = pygame.math.Vector2(source_pos)
            self.target_position = self.last_known_player_pos
            self.current_dialogue = self.dialogue["hostile_trigger"]
            self.interaction_state = "HOSTILE"

    def advance_dialogue(self):
        if self.has_become_hostile:
            return
        
        if self.interaction_state == "GREETING":
            self.interaction_state = "PROPOSAL"
        elif self.interaction_state == "NO_AMMO":
            self.interaction_state = "PROPOSAL"

    def accept_proposal(self):
        if self.interaction_state == "PROPOSAL" and not self.has_become_hostile:
            player = self.game.player
            
            ammo_needed = PISTOL_MAGAZINE_SIZE
            has_enough_ammo = False
            
            if hasattr(player, 'reserve_ammo'):
                has_enough_ammo = player.reserve_ammo >= ammo_needed
            
            if has_enough_ammo:
                player.reserve_ammo -= ammo_needed
                
                if hasattr(player, 'apply_mask_buff'):
                    player.apply_mask_buff(30)
                
                self.interaction_state = "ACCEPT"
                self.trade_completed = True
            else:
                self.interaction_state = "NO_AMMO"

    def refuse_proposal(self):
        if self.interaction_state == "PROPOSAL" and not self.has_become_hostile:
            self.interaction_state = "REFUSE"
