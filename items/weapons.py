import pygame
from core.settings import *
from projectiles.projectiles import Bullet, Casing, Rocket

vec = pygame.math.Vector2

class Weapon:
    def __init__(self, game, owner):
        self.game = game
        self.owner = owner
        self.last_use_time = 0

    def can_use(self):
        return True

    def use(self, direction):
        pass

    def update(self, dt):
        pass

    def draw(self, screen, camera):
        pass

class Pistol(Weapon):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.name = "Pistol"
        self.player = player
        self.last_shot_time = 0
        self.reloading = False
        self.reload_start_time = 0
        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE
        self.muzzle_flash_timer = 0
        self.last_fire_rate = BULLET_FIRE_RATE

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return (not self.reloading and
                self.ammo_in_mag > 0 and
                now - self.last_shot_time > PISTOL_FIRE_RATE)

    def start_reload(self):
        if self.reloading or self.ammo_in_mag == PISTOL_MAGAZINE_SIZE:
            return

        if self.player.can_reload():
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            self.game.play_audio('reload_start', volume=0.7)

    def finish_reload(self):
        needed_ammo = PISTOL_MAGAZINE_SIZE - self.ammo_in_mag
        transferred_ammo = self.player.take_ammo_from_reserve(needed_ammo)
        self.ammo_in_mag += transferred_ammo
        self.reloading = False
        self.game.play_audio('reload_end', volume=0.7)
        
    def shoot(self, direction):
        if not self.can_shoot():
            if not self.reloading and self.ammo_in_mag <= 0:
                self.start_reload()
            self.game.play_audio('empty_click', volume=0.7)
            return

        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.last_fire_rate:
            return

        self.last_shot_time = now
        self.ammo_in_mag -= 1
        self.muzzle_flash_timer = now

        offset_dist = self.player.rect.width / 2 + BULLET_WIDTH / 2
        spawn_pos = self.player.position + direction * offset_dist

        # Criar bala com tipo específico
        Bullet(self.game, spawn_pos, direction, BULLET_SPEED, bullet_type="pistol")
        self.game.play_audio('beretta-m9', volume=0.6)

        # Casquinha específica para pistola
        casing_spawn_offset = vec(15 if self.player.facing_right else -15, -5)
        casing_pos = self.player.position + casing_spawn_offset
        Casing(self.game, casing_pos, self.player.facing_right, weapon_type="pistol")

        if self.ammo_in_mag <= 0:
            self.start_reload()
            
    def update(self, dt):
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start_time > PISTOL_RELOAD_TIME:
                self.finish_reload()

    def draw(self, screen, camera):
        now = pygame.time.get_ticks()
        if self.muzzle_flash_timer > 0 and now - self.muzzle_flash_timer < PISTOL_MUZZLE_FLASH_DURATION:
            # Debug para verificar se está funcionando
            print(f"[DEBUG] Muzzle flash ativo! Timer: {now - self.muzzle_flash_timer}")
            
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = camera.screen_to_world(mouse_pos)
            direction = vec(world_mouse_pos) - self.player.position
            if direction.length_squared() > 0:
                direction = direction.normalize()
                
                # Posição do flash ajustada para ser mais visível
                offset_dist = self.player.rect.width * 0.8
                flash_pos_world = self.player.position + direction * offset_dist
                flash_pos_screen = camera.apply_coords(*flash_pos_world)
                
                # Desenhar múltiplos círculos para um efeito mais visível
                flash_radius = PISTOL_MUZZLE_FLASH_SIZE
                
                # Flash principal (amarelo brilhante)
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (int(flash_pos_screen[0]), int(flash_pos_screen[1])), 
                                 flash_radius)
                
                # Flash interno (branco para brilho)
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (int(flash_pos_screen[0]), int(flash_pos_screen[1])), 
                                 flash_radius // 2)
                
                # Flash externo (laranja para realismo)
                pygame.draw.circle(screen, (255, 165, 0), 
                                 (int(flash_pos_screen[0]), int(flash_pos_screen[1])), 
                                 flash_radius + 2)
        else:
            # Resetar o timer quando o flash termina
            if self.muzzle_flash_timer > 0:
                self.muzzle_flash_timer = 0
