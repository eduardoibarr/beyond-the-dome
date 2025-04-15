import pygame
import random
from enum import Enum
from settings import *

vec = pygame.math.Vector2

class AIState(Enum):
    IDLE = 1
    PATROL = 2
    CHASE = 3
    ATTACK = 4
    SEARCH = 5

class AIController:
    def __init__(self, enemy_sprite):
        self.enemy = enemy_sprite
        self.game = enemy_sprite.game
        self.state = AIState.PATROL
        self.target_position = None
        self.last_known_player_pos = None
        self.patrol_center = vec(self.enemy.pos)
        self.last_attack_time = 0
        self.search_start_time = 0
        self.set_new_patrol_target()

    def alert_damage(self, player_pos):
        if self.state != AIState.ATTACK and self.state != AIState.CHASE:
            print(f"Inimigo em {self.enemy.pos} alertado sobre dano, mudando para CHASE")
            self.state = AIState.CHASE
            self.last_known_player_pos = player_pos
            self.target_position = player_pos

    def set_new_patrol_target(self):
        angle = random.uniform(0, 2 * 3.14159)
        radius = random.uniform(0, ENEMY_PATROL_RADIUS)
        self.target_position = self.patrol_center + vec(radius * pygame.math.Vector2(1, 0).rotate_rad(angle))

    def move_towards_target(self, target_pos, speed):
        if not target_pos:
            return False

        direction = target_pos - self.enemy.pos
        dist_sq = direction.length_squared()
        threshold_sq = speed * speed * 1.1

        if dist_sq < threshold_sq:
            return True
        else:
            move_vec = direction.normalize() * speed
            self.enemy.move(move_vec.x, move_vec.y)
            return False

    def update(self):
        now = pygame.time.get_ticks()
        player_pos = vec(self.game.player.rect.center)
        enemy_pos = self.enemy.pos
        distance_to_player = enemy_pos.distance_to(player_pos)

        can_see_player = distance_to_player < ENEMY_DETECT_RADIUS

        if self.state == AIState.PATROL:
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            elif self.move_towards_target(self.target_position, self.enemy.speed * 0.5):
                self.set_new_patrol_target()

        elif self.state == AIState.SEARCH:
            if can_see_player:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            elif now > self.search_start_time + ENEMY_SEARCH_DURATION:
                self.state = AIState.PATROL
                self.patrol_center = vec(self.enemy.pos)
                self.set_new_patrol_target()
            elif self.move_towards_target(self.target_position, self.enemy.speed * 0.75):
                self.state = AIState.PATROL
                self.patrol_center = vec(self.enemy.pos)
                self.set_new_patrol_target()

        elif self.state == AIState.CHASE:
            if not can_see_player:
                self.state = AIState.SEARCH
                self.target_position = self.last_known_player_pos
                self.search_start_time = now
            elif distance_to_player < ENEMY_ATTACK_RADIUS:
                self.state = AIState.ATTACK
            else:
                self.last_known_player_pos = player_pos
                self.move_towards_target(player_pos, self.enemy.speed)

        elif self.state == AIState.ATTACK:
            if distance_to_player > ENEMY_ATTACK_RADIUS * 1.1:
                self.state = AIState.CHASE
                self.last_known_player_pos = player_pos
            elif now > self.last_attack_time + ENEMY_ATTACK_COOLDOWN:
                if enemy_pos.distance_to(player_pos) < ENEMY_ATTACK_RADIUS * 1.1:
                    self.game.player.take_damage(self.enemy.damage)
                    self.last_attack_time = now
                else:
                    self.state = AIState.CHASE
                    self.last_known_player_pos = player_pos

class RaiderAIController(AIController):
    def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)

class WildDogAIController(AIController):
     def __init__(self, enemy_sprite):
        super().__init__(enemy_sprite)
