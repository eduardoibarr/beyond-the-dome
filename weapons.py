import pygame
import math
from settings import *
from projectiles import Stone

class Slingshot:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.charging = False
        self.charge_start_time = 0
        self.last_shot_time = 0
        self.target_angle = 0
        
    def can_shoot(self):
        now = pygame.time.get_ticks()
        return now - self.last_shot_time > SLINGSHOT_COOLDOWN
        
    def start_charging(self):
        if not self.charging and self.can_shoot() and self.player.has_stones():
            self.charging = True
            self.charge_start_time = pygame.time.get_ticks()
    
    def release_stone(self):
        if not self.charging:
            return
            
        now = pygame.time.get_ticks()
        self.charging = False
        
        if not self.player.use_stone():
            self.last_shot_time = now
            return
            
        self.last_shot_time = now
        
        charge_time = now - self.charge_start_time
        charge_percent = min(1.0, charge_time / SLINGSHOT_CHARGE_TIME)
        stone_speed = STONE_SPEED_MIN + (STONE_SPEED_MAX - STONE_SPEED_MIN) * charge_percent
        
        angle_rad = math.radians(self.target_angle)
        direction = pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad))
        
        offset = direction * self.player.rect.width // 2
        start_pos = (self.player.rect.centerx + offset.x, self.player.rect.centery + offset.y)
        
        Stone(self.game, start_pos, direction, stone_speed)
            
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.player.rect.centerx
        dy = mouse_pos[1] - self.player.rect.centery
        self.target_angle = math.degrees(math.atan2(-dy, dx))
        
        mouse_buttons = pygame.mouse.get_pressed()
        
        if mouse_buttons[0]:  
            if not self.charging and self.can_shoot() and self.player.has_stones():
                self.start_charging()
        elif self.charging:  
            self.release_stone()
            
    def get_charge_percent(self):
        if not self.charging:
            return 0
            
        now = pygame.time.get_ticks()
        charge_time = now - self.charge_start_time
        return min(1.0, charge_time / SLINGSHOT_CHARGE_TIME)
            
    def draw(self, screen):
        
        if self.charging:
            angle_rad = math.radians(self.target_angle)
            direction = pygame.math.Vector2(math.cos(angle_rad), -math.sin(angle_rad))
            handle_offset = direction * (self.player.rect.width // 2 - SLINGSHOT_HANDLE_HEIGHT // 2)
            handle_pos = (self.player.rect.centerx + handle_offset.x, self.player.rect.centery + handle_offset.y)
            handle_offset = direction * (self.player.rect.width // 2 - SLINGSHOT_HANDLE_HEIGHT // 2)
            handle_pos = (self.player.rect.centerx + handle_offset.x, self.player.rect.centery + handle_offset.y)
            
            charge_percent = self.get_charge_percent()
            
            pouch_offset_distance = SLINGSHOT_HANDLE_HEIGHT + charge_percent * 30
            pouch_pos = (handle_pos[0] - direction.x * pouch_offset_distance, 
                         handle_pos[1] - direction.y * pouch_offset_distance)

            aim_length = SLINGSHOT_POWER_MIN + (SLINGSHOT_POWER_MAX - SLINGSHOT_POWER_MIN) * charge_percent
            aim_start_pos = pouch_pos
            aim_end = (aim_start_pos[0] + direction.x * aim_length, 
                      aim_start_pos[1] + direction.y * aim_length)
            
            aim_color = (*SLINGSHOT_AIMING_LINE_COLOR, int(128 * charge_percent))
            
            aim_line_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(aim_line_surface, aim_color, aim_start_pos, aim_end, 1)
            screen.blit(aim_line_surface, (0, 0)) 