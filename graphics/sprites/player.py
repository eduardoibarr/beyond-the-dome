import pygame
from core.settings import *
from items.weapons import Pistol
from graphics.particles import BloodParticleSystem
from core.inventory import Inventory
from items.item_base import AmmoItem, MaskItem, HealthPackItem, FilterModuleItem
import math

vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x_pixel, y_pixel):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = PLAYER_RENDER_LAYER

        self.animations = {}
        self.current_animation = None
        self._setup_animations()

        if not self.current_animation:
            print("Animações do jogador desativadas. Usando fallback.")
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(PLAYER_COLOR)
            self.current_animation = None

        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.facing_right = True

        self.position = vec(x_pixel, y_pixel)
        self.velocity = vec(0, 0)
        self.acceleration = vec(0, 0)
        self.direction = vec(1, 0)
        self.rect.center = self.position
        self.size = PLAYER_WIDTH
        self.state = 'idle'

        self.max_speed = PLAYER_SPEED
        self.normal_speed = PLAYER_SPEED
        self.current_terrain = None
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.radiation = 0
        self.last_hit_time = 0
        self.invincible = False

        self.mask_buff_active = False
        self.mask_buff_timer = 0.0

        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE
        self.reserve_ammo = PLAYER_STARTING_RESERVE_AMMO
        self.pistol = Pistol(game, self)
        self.current_weapon = self.pistol
        self.blood_system = BloodParticleSystem()
        self.has_filter_module = False
        self.is_in_radioactive_zone = False

        self.step_timer = 0
        self.step_interval = 0.35
        self.last_melee_attack_time = 0
        self.melee_cooldown = PLAYER_MELEE_COOLDOWN

        self.walk_frame = 0
        self.death_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0

        self.inventory = Inventory(size=20)

        ammo_item = AmmoItem("pistol", 15)
        ammo_item.load_icon(self.game.asset_manager)
        self.inventory.add_item(ammo_item)

        mask_item = MaskItem()
        mask_item.load_icon(self.game.asset_manager)
        self.inventory.add_item(mask_item)

        pygame.mouse.set_visible(CURSOR_VISIBLE)

    def _setup_animations(self):

        if not hasattr(self.game, 'asset_manager'):
            print("Erro: Asset manager não encontrado.")
            return

        try:

            idle_frames = self.game.asset_manager.get_animation('player_idle')
            run_frames = self.game.asset_manager.get_animation('player_run')
            walk_frames = self.game.asset_manager.get_animation('player_walk')
            hurt_frames = self.game.asset_manager.get_animation('player_hurt')
            shoot_frames = self.game.asset_manager.get_animation('player_shoot')
            attack_frames = self.game.asset_manager.get_animation('player_attack')

            if not walk_frames and run_frames:
                walk_frames = run_frames

            if not idle_frames:
                raise ValueError("Animação 'player_idle' não encontrada no AssetManager.")

            self.animations = {
                ANIM_PLAYER_IDLE: idle_frames,
                ANIM_PLAYER_RUN: run_frames if run_frames else idle_frames,
                ANIM_PLAYER_WALK: walk_frames if walk_frames else idle_frames,
                ANIM_PLAYER_HURT: hurt_frames if hurt_frames else idle_frames,
                ANIM_PLAYER_SHOOT: shoot_frames if shoot_frames else idle_frames,
                ANIM_PLAYER_ATTACK: attack_frames if attack_frames else idle_frames
            }

            self.current_animation = ANIM_PLAYER_IDLE
            self.animation_frame = 0
            self.animation_frame_duration = 0.1
            self.animation_timer = 0
            self.image = self.animations[self.current_animation][0]
            print("Animações do jogador configuradas com sucesso.")

        except Exception as e:
            print(f"Erro ao configurar animações do jogador: {e}. Animações desativadas.")
            self.animations = {}
            self.current_animation = None

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= amount
            self.health = max(0, self.health)
            self.blood_system.add_particles(self.rect.centerx, self.rect.centery, count=5)
            self.last_hit_time = now
            self.invincible = True
            self.set_animation(ANIM_PLAYER_HURT)

            if hasattr(self.game, 'asset_manager'):
                self.game.asset_manager.play_sound('player_hurt')

            if self.health <= 0:
                print("Jogador morreu!")

    def set_animation(self, animation_name):
        if not self.current_animation or self.current_animation == animation_name:
            return

        if animation_name in self.animations:

            if self.current_animation == ANIM_PLAYER_HURT and self.animation_frame < len(self.animations[ANIM_PLAYER_HURT]) - 1:
                 return

            self.current_animation = animation_name
            self.animation_frame = 0
            self.animation_timer = 0
        else:

            if ANIM_PLAYER_IDLE in self.animations:
                 self.current_animation = ANIM_PLAYER_IDLE
            else:
                 self.current_animation = None

    def get_keys(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.acceleration = vec(0, 0)
        if keys[pygame.K_a]: self.acceleration.x = -self.max_speed * 8
        if keys[pygame.K_d]: self.acceleration.x = self.max_speed * 8
        if keys[pygame.K_w]: self.acceleration.y = -self.max_speed * 8
        if keys[pygame.K_s]: self.acceleration.y = self.max_speed * 8

        if self.acceleration.length() > 0:
            self.state = 'walking'
        else:
            self.state = 'idle'

        if keys[pygame.K_r]:
            self.pistol.start_reload()
            if self.current_weapon:
                self.current_weapon.start_reload()
        if keys[pygame.K_SPACE]:
            self.attack()

        if self.game.camera:

            world_mouse_pos = self.game.camera.screen_to_world(mouse_pos)
            self.direction = (vec(world_mouse_pos) - self.position).normalize() if (vec(world_mouse_pos) - self.position).length() > 0 else self.direction

            screen_center = vec(self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
            mouse_offset = vec(mouse_pos) - screen_center
            self.facing_right = mouse_offset.x > 0

            if mouse_buttons[0]:
                direction = vec(world_mouse_pos) - self.position
                if direction.length() > 0:
                    direction = direction.normalize()
                    self.pistol.shoot(direction)
                    if self.current_weapon:
                        self.current_weapon.shoot(direction)
                    self.state = 'shooting'

        if self.current_animation != ANIM_PLAYER_HURT:
            if self.acceleration.length_squared() > 0:

                if self.velocity.length_squared() > (self.max_speed * 0.5)**2:
                    self.set_animation(ANIM_PLAYER_RUN)
                else:
                    self.set_animation(ANIM_PLAYER_WALK)
            else:

                is_shooting = (pygame.time.get_ticks() - self.pistol.last_shot_time < 100)
                if self.pistol.reloading or is_shooting:
                    self.set_animation(ANIM_PLAYER_SHOOT)
                elif self.current_animation != ANIM_PLAYER_ATTACK:
                     self.set_animation(ANIM_PLAYER_IDLE)

    def move(self, dt):

        self.check_terrain()

        self.velocity += self.acceleration * dt * 10
        self.velocity *= (1 - PLAYER_FRICTION)

        if self.velocity.length_squared() > self.max_speed * self.max_speed:
            if self.velocity.length_squared() > 0:
                 self.velocity.scale_to_length(self.max_speed)

        if self.velocity.length_squared() < (0.5 * TILE_SIZE)**2 and self.acceleration.length_squared() == 0:
            self.velocity = vec(0, 0)

        displacement = self.velocity * dt
        new_position = self.position + displacement

        self.position = self.collide_with_obstacles(new_position)
        self.rect.center = self.position

    def collide_with_obstacles(self, new_position):
        potential_rect = self.rect.copy()
        final_pos = new_position.copy()

        potential_rect.centerx = new_position.x
        potential_rect.centery = self.position.y
        for obstacle in self.game.obstacles:
            if potential_rect.colliderect(obstacle.rect):
                if self.velocity.x > 0: final_pos.x = obstacle.rect.left - self.rect.width / 2
                elif self.velocity.x < 0: final_pos.x = obstacle.rect.right + self.rect.width / 2
                self.velocity.x = 0
                potential_rect.centerx = final_pos.x
                break

        potential_rect.centery = new_position.y
        for obstacle in self.game.obstacles:
            if potential_rect.colliderect(obstacle.rect):
                if self.velocity.y > 0: final_pos.y = obstacle.rect.top - self.rect.height / 2
                elif self.velocity.y < 0: final_pos.y = obstacle.rect.bottom + self.rect.height / 2
                self.velocity.y = 0
                break

        return final_pos

    def attack(self):

        now = pygame.time.get_ticks()
        if now - self.last_melee_attack_time < self.melee_cooldown:
             return

        if self.current_animation in [ANIM_PLAYER_ATTACK, ANIM_PLAYER_HURT]: return

        self.last_melee_attack_time = now
        self.set_animation(ANIM_PLAYER_ATTACK)

        hitbox_offset = 30
        hitbox_width = 40
        hitbox_height = self.rect.height * 0.8
        hitbox_center_x = self.rect.centerx + (hitbox_offset if self.facing_right else -hitbox_offset)
        hitbox_center_y = self.rect.centery
        attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

        for enemy in self.game.enemies:
            if attack_hitbox.colliderect(enemy.rect):
                 if hasattr(enemy, 'take_damage'):
                      enemy.take_damage(MELEE_WEAPON_DAMAGE)

    def update(self, dt):

        old_position = self.position.copy() if hasattr(self, 'position') else pygame.math.Vector2(0, 0)

        if self.mask_buff_active:
            self.mask_buff_timer -= dt
            if self.mask_buff_timer <= 0:
                self.mask_buff_active = False
                self.mask_buff_timer = 0
                print("Mask buff expired.")

        self.get_keys()
        self.move(dt)

        # Trigger mission event for movement
        if hasattr(self.game, 'trigger_mission_event') and hasattr(self, 'position'):
            distance_moved = old_position.distance_to(self.position)
            if distance_moved > 5:  # Se o jogador se moveu uma distância significativa
                self.game.trigger_mission_event("reach", "tutorial_area", 1)

        self.update_radiation(dt)
        self.pistol.update(dt)
        self.blood_system.update(dt)

        if self.invincible and pygame.time.get_ticks() - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
            self.invincible = False
            if self.current_animation == ANIM_PLAYER_HURT and self.animation_frame == 0:
                 self.set_animation(ANIM_PLAYER_IDLE)

        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.state == 'walking' and self.velocity.length() > 0:
                self.walk_frame += 1
            elif self.state == 'dead':
                if self.death_frame < 3:
                    self.death_frame += 1

        self._create_sprite()

        self.check_terrain()

    def draw_weapon(self, screen, camera):
        if not camera: return

        mouse_pos = pygame.mouse.get_pos()
        cursor_size = 16
        cursor_color = WHITE
        cursor_thickness = 2
        pygame.draw.circle(screen, cursor_color, mouse_pos, cursor_size, cursor_thickness)
        pygame.draw.line(screen, cursor_color,
                        (mouse_pos[0] - cursor_size, mouse_pos[1]),
                        (mouse_pos[0] + cursor_size, mouse_pos[1]), cursor_thickness)
        pygame.draw.line(screen, cursor_color,
                        (mouse_pos[0], mouse_pos[1] - cursor_size),
                        (mouse_pos[0], mouse_pos[1] + cursor_size), cursor_thickness)

        self.pistol.draw(screen, camera)
        self.blood_system.draw(screen, camera)

    def has_reserve_ammo(self):
        return self.reserve_ammo > 0

    def can_reload(self):
        return (self.pistol.ammo_in_mag < PISTOL_MAGAZINE_SIZE and
                self.has_reserve_ammo())

    def take_ammo_from_reserve(self, amount_needed):
        can_take = min(amount_needed, self.reserve_ammo)
        self.reserve_ammo -= can_take
        return can_take

    def update_radiation(self, dt):

        radiation_gain_rate = PLAYER_RADIATION_GAIN_RATE

        if self.mask_buff_active:

            radiation_gain_rate = 0

        if self.is_in_radioactive_zone:
            self.radiation += radiation_gain_rate * dt

            self.radiation = min(self.radiation, RADIATION_MAX)
        else:

            self.radiation -= PLAYER_RADIATION_RECOVERY_RATE * dt
            self.radiation = max(0, self.radiation)

        if self.radiation > RADIATION_DAMAGE_THRESHOLD:

            damage = (self.radiation - RADIATION_DAMAGE_THRESHOLD) * RADIATION_DAMAGE_MULTIPLIER * dt
            self.take_damage(damage)

    def collect_filter_module(self):
        print("Jogador coletou o módulo de filtro!")
        self.has_filter_module = True

    def apply_mask_buff(self, duration):
        self.mask_buff_active = True
        self.mask_buff_timer = duration
        print(f"Mask buff applied for {duration} seconds.")

    def check_terrain(self):

        tile_x = int(self.position.x / TILE_SIZE)
        tile_y = int(self.position.y / TILE_SIZE)

        if (tile_x < 0 or tile_x >= self.game.map_width or
            tile_y < 0 or tile_y >= self.game.map_height):
            return

        self.current_terrain = None
        terrain_found = False

        for tile in self.game.world_tiles:
            if not hasattr(tile, 'kind'):
                continue

            if tile.rect.collidepoint(self.position):
                self.current_terrain = tile.kind
                terrain_found = True
                break

        if terrain_found:
            if self.current_terrain == 'water':

                self.max_speed = self.normal_speed * 0.6

                if self.velocity.length_squared() > 0.5:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.step_timer > self.step_interval * 1000:
                        self.step_timer = current_time
                        if hasattr(self.game, 'asset_manager'):
                            self.game.play_audio('water_step', volume=0.3)
            else:

                self.max_speed = self.normal_speed

    def _create_sprite(self):

        if hasattr(self.game, 'asset_manager'):

            hero_base = "assets/images/tds-modern-hero-weapons-and-props/"

            if self.state == 'dead':

                frame_num = min(self.death_frame + 1, 4)
                asset_path = hero_base + f"Hero_Die/{frame_num}.png"
            elif self.current_weapon:
                weapon_name = self.current_weapon.name
                if weapon_name == "Pistol":
                    if self.state == 'shooting':
                        asset_path = hero_base + "Hero_Pistol/Shot/Hero_Pistol_Fire.png"
                    else:
                        asset_path = hero_base + "Hero_Pistol/Hero_Pistol.png"
                elif weapon_name == "Rifle":
                    if self.state == 'shooting':
                        asset_path = hero_base + "Hero_Rifle/Shot/Hero_Rifle_Fire.png"
                    else:
                        asset_path = hero_base + "Hero_Rifle/Hero_Rifle.png"
                elif weapon_name == "Machine Gun":
                    asset_path = hero_base + "Hero_MachineGun/Hero_MachineGun.png"
                elif weapon_name == "Flamethrower":
                    asset_path = hero_base + "Hero_Flamethrower/Hero_Flamethrower.png"
                elif weapon_name == "Grenade Launcher":
                    asset_path = hero_base + "Hero_GrenadeLauncher/Hero_GrenadeLauncher.png"
                else:

                    frame_num = (self.walk_frame // 5) % 7 + 1
                    asset_path = hero_base + f"Hero_Walk/With Kneepads/{frame_num}.png"
            else:

                if self.state == 'walking':
                    frame_num = (self.walk_frame // 5) % 7 + 1
                    asset_path = hero_base + f"Hero_Walk/With Kneepads/{frame_num}.png"
                else:

                    asset_path = hero_base + "Hero_Walk/With Kneepads/1.png"

            try:
                self.image = self.game.asset_manager.get_image(asset_path).copy()

                if self.image.get_width() != self.size or self.image.get_height() != self.size:
                    self.image = pygame.transform.scale(self.image, (self.size, self.size))

                angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
                self.image = pygame.transform.rotate(self.image, angle)

                self.rect = self.image.get_rect(center=self.rect.center)
                return
            except Exception as e:
                print(f"Erro ao carregar sprite do player: {e}")

        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2

        if self.state == 'dead':
            body_color = GRAY
            head_color = DARK_GRAY
        elif self.invincible and int(pygame.time.get_ticks() / 100) % 2:

            body_color = WHITE
            head_color = LIGHT_GRAY
        else:
            body_color = PLAYER_COLOR
            head_color = PLAYER_HEAD_COLOR

        pygame.draw.circle(surf, body_color, (center, center), self.size // 2)
        pygame.draw.circle(surf, BLACK, (center, center), self.size // 2, 2)

        head_radius = self.size // 4
        head_offset = self.size // 4
        head_x = center + int(self.direction.x * head_offset)
        head_y = center + int(self.direction.y * head_offset)
        pygame.draw.circle(surf, head_color, (head_x, head_y), head_radius)
        pygame.draw.circle(surf, BLACK, (head_x, head_y), head_radius, 1)

        if self.state != 'dead':
            eye_offset = head_radius // 2
            eye_radius = 2

            perp_x = -self.direction.y
            perp_y = self.direction.x

            eye1_x = head_x + int(perp_x * eye_offset) + int(self.direction.x * eye_offset)
            eye1_y = head_y + int(perp_y * eye_offset) + int(self.direction.y * eye_offset)
            pygame.draw.circle(surf, BLACK, (eye1_x, eye1_y), eye_radius)

            eye2_x = head_x - int(perp_x * eye_offset) + int(self.direction.x * eye_offset)
            eye2_y = head_y - int(perp_y * eye_offset) + int(self.direction.y * eye_offset)
            pygame.draw.circle(surf, BLACK, (eye2_x, eye2_y), eye_radius)

        if self.state != 'dead':
            line_start = (center, center)
            line_end = (center + int(self.direction.x * self.size // 2),
                       center + int(self.direction.y * self.size // 2))
            pygame.draw.line(surf, DARK_GRAY, line_start, line_end, 2)

        self.image = surf
        self.rect = self.image.get_rect(center=self.rect.center)
