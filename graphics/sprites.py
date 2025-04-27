import pygame
import math
import random # Needed for WildDog random movement
from core.settings import *

# --- Import Dependencies (Ensure these files exist and contain the required classes) ---
try:
    from core.ai.ai import RaiderAIController, WildDogAIController
except ImportError:
    print("Warning: Could not import AI controllers from 'core/ai/ai.py'. Enemy AI will not function.")
    # Define dummy classes if ai.py is missing to avoid crashing
    class RaiderAIController:
        def __init__(self, enemy): pass
        def update(self, dt): pass
        def alert_damage(self, source_pos): pass
    class WildDogAIController:
        def __init__(self, enemy): pass
        def update(self, dt): pass
        def alert_damage(self, source_pos): pass

try:
    from items.weapons import Pistol
except ImportError:
    print("Warning: Could not import Pistol from 'items/weapons.py'. Player weapon will not function.")
    # Define dummy class
    class Pistol:
        def __init__(self, game, player): self.reloading = False; self.ammo_in_mag = 0
        def update(self, dt): pass
        def draw(self, screen, camera): pass
        def shoot(self, target_pos): pass
        def start_reload(self): pass


try:
    from graphics.particles import BloodParticleSystem
except ImportError:
    print("Warning: Could not import BloodParticleSystem from 'graphics/particles.py'. Blood effects will not function.")
    # Define dummy class
    class BloodParticleSystem:
        def __init__(self): pass
        def add_particles(self, x, y, count=0): pass
        def update(self, dt): pass
        def draw(self, screen, camera): pass

try:
    from graphics.spritesheet import Spritesheet
except ImportError:
     print("Warning: Could not import Spritesheet from 'graphics/spritesheet.py'. Animations require this.")
     # Define dummy class
     class Spritesheet:
         def __init__(self, filename): pass
         def load_strip(self, rect, image_count, colorkey=None): return [] # Return empty list


vec = pygame.math.Vector2

# --- Load Spritesheets (Error handling added) ---
SPRITESHEETS_LOADED = False # Default to False
try:
    # !!! IMPORTANT: Replace 'sprites/run.png' with the ACTUAL paths to your spritesheets !!!
    # Ensure these files exist and are valid image files in a 'sprites' subfolder (or adjust path)
    # player_sprites_path = 'sprites/run.png' # Replaced by constant
    # enemy_sprites_path = 'sprites/run.png'  # Replaced by constant

    # Check if the dummy class is being used
    if 'Spritesheet' in locals() and not hasattr(Spritesheet, 'load_strip'):
         raise ImportError("Spritesheet class is a dummy, cannot load animations.")

    player_sprites = {
        # Create a Spritesheet object for each distinct spritesheet file used by the player
        SPRITESHEET_KEY_BASE: Spritesheet(PLAYER_SPRITESHEET_PATH), # Use constants
        # If animations are in separate files, create separate Spritesheet objects:
        # 'idle_sheet': Spritesheet('sprites/player_idle.png'),
        # 'run_sheet': Spritesheet('sprites/player_run.png'),
        # etc.
    }
    # Assign the correct Spritesheet object to each animation state
    player_sprites[ANIM_PLAYER_IDLE] = player_sprites[SPRITESHEET_KEY_BASE]
    player_sprites[ANIM_PLAYER_RUN] = player_sprites[SPRITESHEET_KEY_BASE]
    player_sprites[ANIM_PLAYER_WALK] = player_sprites[SPRITESHEET_KEY_BASE]
    player_sprites[ANIM_PLAYER_HURT] = player_sprites[SPRITESHEET_KEY_BASE]
    player_sprites[ANIM_PLAYER_SHOOT] = player_sprites[SPRITESHEET_KEY_BASE]
    player_sprites[ANIM_PLAYER_ATTACK] = player_sprites[SPRITESHEET_KEY_BASE]


    enemy_sprites = {
        # Create Spritesheet objects for enemy sheets
        SPRITESHEET_KEY_BASE: Spritesheet(ENEMY_SPRITESHEET_PATH), # Use constants
    }
    # Assign the correct Spritesheet object to each enemy animation state
    enemy_sprites[ANIM_ENEMY_IDLE] = enemy_sprites[SPRITESHEET_KEY_BASE]
    enemy_sprites[ANIM_ENEMY_WALK] = enemy_sprites[SPRITESHEET_KEY_BASE]
    enemy_sprites[ANIM_ENEMY_HURT] = enemy_sprites[SPRITESHEET_KEY_BASE]
    enemy_sprites[ANIM_ENEMY_SLASH] = enemy_sprites[SPRITESHEET_KEY_BASE]

    SPRITESHEETS_LOADED = True
    print("Spritesheets loaded successfully.")

except ImportError:
     # Handled above by dummy class definitions
     pass # Keep SPRITESHEETS_LOADED as False
except FileNotFoundError as e:
    print(f"Error loading spritesheet file: {e}. Animations disabled.")
    print("Please ensure spritesheet files exist at the specified paths.")
except pygame.error as e:
    print(f"Pygame error loading spritesheet image: {e}. Animations disabled.")
except Exception as e:
    print(f"An unexpected error occurred loading spritesheets: {e}. Animations disabled.")


# --- Player Class ---
class Player(pygame.sprite.Sprite):
    """Represents the player character."""
    def __init__(self, game, x_pixel, y_pixel): # Expect pixel coordinates
        global SPRITESHEETS_LOADED # Declare intent to use the global variable
        self.groups = game.all_sprites
        super().__init__(self.groups) # Use super() for initialization
        self.game = game
        self._layer = PLAYER_RENDER_LAYER # Use constant

        # --- Animation Setup ---
        self.animations = {}
        self.current_animation = None # Initialize as None
        if SPRITESHEETS_LOADED:
            try:
                # Define animation strips: ((x, y, width, height), num_frames)
                # !!! IMPORTANT: Adjust these rects and frame counts for YOUR spritesheets !!!
                idle_strip = ((0, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), PLAYER_IDLE_FRAMES)
                run_strip = ((0, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), PLAYER_RUN_FRAMES)
                walk_strip = ((0, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), PLAYER_RUN_FRAMES) # Using run frames for walk
                hurt_strip = ((0, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), 3) # Example, define HURT_FRAMES?
                shoot_strip = ((0, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), 4) # Example, define SHOOT_FRAMES?
                attack_strip = ((0, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), 6) # Example, define ATTACK_FRAMES?

                # Load frames using the correct Spritesheet object assigned above
                self.animations = {
                    ANIM_PLAYER_IDLE: player_sprites[ANIM_PLAYER_IDLE].load_strip(*idle_strip),
                    ANIM_PLAYER_RUN: player_sprites[ANIM_PLAYER_RUN].load_strip(*run_strip),
                    ANIM_PLAYER_WALK: player_sprites[ANIM_PLAYER_WALK].load_strip(*walk_strip),
                    ANIM_PLAYER_HURT: player_sprites[ANIM_PLAYER_HURT].load_strip(*hurt_strip),
                    ANIM_PLAYER_SHOOT: player_sprites[ANIM_PLAYER_SHOOT].load_strip(*shoot_strip),
                    ANIM_PLAYER_ATTACK: player_sprites[ANIM_PLAYER_ATTACK].load_strip(*attack_strip)
                }

                # Validate loaded animations
                if not self.animations[ANIM_PLAYER_IDLE]: # Check if idle animation loaded
                     raise ValueError(f"Failed to load '{ANIM_PLAYER_IDLE}' animation frames.")

                self.current_animation = ANIM_PLAYER_IDLE
                self.animation_frame = 0
                self.animation_frame_duration = 0.1 # Time (seconds) per frame
                self.animation_timer = 0
                self.image = self.animations[self.current_animation][0] # Set initial image

            except (KeyError, AttributeError, ValueError, Exception) as e:
                print(f"Error setting up player animations: {e}. Disabling animations.")
                SPRITESHEETS_LOADED = False # Disable animation if setup fails
                self.animations = {}
                self.current_animation = None

        # Fallback if spritesheets failed to load or setup failed
        if not self.current_animation:
            print("Player animations disabled or failed. Using fallback.")
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(PLAYER_COLOR)
            self.image.set_colorkey(BLACK) # Optional transparency
            self.current_animation = None # Ensure it's None

        self.original_image = self.image # Store original for flipping/effects
        self.rect = self.image.get_rect()
        self.facing_right = True

        # --- Position and Movement (Physics) ---
        self.position = vec(x_pixel, y_pixel) # Use float vector for precise position
        self.velocity = vec(0, 0)             # Velocity in pixels per second
        self.acceleration = vec(0, 0)         # Acceleration (temporary force vector)
        self.rect.center = self.position      # Initial rect position

        # --- Physics Constants ---
        # Max speed in pixels per second (adjust in settings.py)
        self.max_speed = PLAYER_SPEED # Use PLAYER_SPEED directly if it's pixels/sec
        # If PLAYER_SPEED was tiles/sec, use: self.max_speed = PLAYER_SPEED * TILE_SIZE

        # --- Player Attributes ---
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.radiation = 0
        self.last_hit_time = 0
        self.invincible = False
        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE # Set by pistol __init__ too, maybe redundant here
        self.reserve_ammo = BULLET_INITIAL_AMMO - PISTOL_MAGAZINE_SIZE # Initial reserve
        self.pistol = Pistol(game, self) # Changed to Pistol
        self.blood_system = BloodParticleSystem()
        self.has_filter_module = False
        self.is_in_radioactive_zone = False # Flag set by Game.update

        # --- Step Timer (for sounds/effects) ---
        self.step_timer = 0
        self.step_interval = 0.35 # Seconds between steps

    def take_damage(self, amount):
        """Applies damage to the player if not invincible."""
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= amount
            self.health = max(0, self.health) # Prevent health going below 0
            self.blood_system.add_particles(self.rect.centerx, self.rect.centery, count=5)
            self.last_hit_time = now
            self.invincible = True
            self.set_animation(ANIM_PLAYER_HURT)
            # Play hurt sound effect here if desired
            # self.game.sound_manager.play('player_hurt')

            if self.health <= 0:
                print("Player died!")
                # Game loop in main.py handles stopping by checking self.game.playing

    def set_animation(self, animation_name):
        """Changes the current animation if it's different and valid."""
        if not self.current_animation or self.current_animation == animation_name:
            return # Skip if animations disabled or already set

        if animation_name in self.animations:
            # Allow switching from 'hurt' only after it finishes one loop
            if self.current_animation == ANIM_PLAYER_HURT and self.animation_frame < len(self.animations[ANIM_PLAYER_HURT]) - 1:
                 return # Don't interrupt hurt animation early

            self.current_animation = animation_name
            self.animation_frame = 0
            self.animation_timer = 0
        else:
            # print(f"Warning: Animation '{animation_name}' not found for player.")
            if ANIM_PLAYER_IDLE in self.animations: # Check if idle exists before defaulting
                 self.current_animation = ANIM_PLAYER_IDLE
            else:
                 self.current_animation = None # No fallback if idle also missing

    def update_animation(self, dt):
        """Updates the current animation frame based on dt."""
        if not self.current_animation: return # Skip if no animation

        frames = self.animations[self.current_animation]
        num_frames = len(frames)
        if num_frames == 0: return # Skip if animation is empty

        # Determine frame duration
        current_frame_duration = self.animation_frame_duration
        if self.current_animation == ANIM_PLAYER_RUN:
            # Adjust run animation speed based on velocity
            speed_mag = self.velocity.length()
            if speed_mag > 1.0 and self.max_speed > 0: # Avoid division by zero
                 speed_factor = max(0.5, min(1.5, speed_mag / self.max_speed))
                 current_frame_duration = self.animation_frame_duration / speed_factor
        elif self.current_animation == ANIM_PLAYER_HURT:
             current_frame_duration = 0.08 # Faster hurt animation

        # Update timer and frame
        self.animation_timer += dt
        while self.animation_timer >= current_frame_duration: # Use while loop for low FPS
            self.animation_timer -= current_frame_duration
            self.animation_frame = (self.animation_frame + 1) % num_frames

            # Check for non-looping animation end
            if self.animation_frame == 0: # Just looped
                 if self.current_animation in [ANIM_PLAYER_HURT, ANIM_PLAYER_ATTACK, ANIM_PLAYER_SHOOT]:
                      self.set_animation(ANIM_PLAYER_IDLE) # Return to idle

        # Update image
        self.original_image = frames[self.animation_frame]
        self.image = self.original_image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Apply invincibility flash
        if self.invincible:
            now = pygame.time.get_ticks()
            alpha = 100 if (now - self.last_hit_time) % 200 < 100 else 255
            try:
                # Use a copy to avoid modifying the original frame in self.animations
                temp_image = self.image.copy()
                temp_image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = temp_image
            except pygame.error as e:
                 # Fallback if BLEND_RGBA_MULT fails (e.g., surface format issue)
                 # print(f"Warning: Could not apply alpha blend: {e}")
                 temp_image = self.image.copy()
                 temp_image.set_alpha(alpha)
                 self.image = temp_image


    def get_keys(self):
        """Processes keyboard input and sets player desired movement vector."""
        # self.acceleration = vec(0, 0) # Removed acceleration
        self.change = vec(0, 0) # Represents the desired movement direction (-1, 0, 1)
        keys = pygame.key.get_pressed()
        moving = False

        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            # self.acceleration.x = -self.move_force # Removed
            self.change.x = -1
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                 # self.acceleration.x = self.move_force # Removed
                 self.change.x = 1
                 self.facing_right = True
                 moving = True

        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            # self.acceleration.y = -self.move_force # Removed
            self.change.y = -1
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
             if not (keys[pygame.K_UP] or keys[pygame.K_w]):
                  # self.acceleration.y = self.move_force # Removed
                  self.change.y = 1
                  moving = True

        # Normalize diagonal movement to prevent faster speed
        if self.change.length_squared() > 0:
             self.change = self.change.normalize()

        # Set velocity directly based on desired change (for animation system)
        self.velocity = self.change * self.max_speed

        # --- Set Animation based on state ---
        if self.current_animation != ANIM_PLAYER_HURT:
            # Use self.change to determine if moving, velocity magnitude for run/walk
            if self.change.length_squared() > 0: # If change vector is non-zero, player intends to move
                if self.velocity.length_squared() > (self.max_speed * 0.5)**2:
                    self.set_animation(ANIM_PLAYER_RUN)
                else:
                    self.set_animation(ANIM_PLAYER_WALK)
            else: # Not moving based on input or velocity
                # Check weapon state before idling
                if self.pistol.reloading or (pygame.time.get_ticks() - self.pistol.last_shot_time < 100): # Simple check
                    self.set_animation(ANIM_PLAYER_SHOOT) # Reuse shoot animation?
                elif self.current_animation not in [ANIM_PLAYER_ATTACK]: # Don't interrupt attack
                     self.set_animation(ANIM_PLAYER_IDLE)

        # --- Actions ---
        if keys[pygame.K_SPACE]:
            self.attack() # Trigger melee attack (add cooldown check here)

        # Reload Key
        if keys[pygame.K_r]:
             self.pistol.start_reload()

        # Mouse button handling for pistol
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]: # Left mouse button (Fire)
             # No charging needed, just shoot directly
             mouse_pos = pygame.mouse.get_pos()
             world_mouse_pos = self.game.camera.screen_to_world(mouse_pos)
             self.pistol.shoot(world_mouse_pos)
        # else: # Mouse button released (No action needed for pistol)
             # if self.slingshot.charging: # Removed slingshot logic
                  # mouse_pos = pygame.mouse.get_pos()
                  # world_mouse_pos = self.game.camera.screen_to_world(mouse_pos)
                  # self.slingshot.shoot(world_mouse_pos)


    def move(self, dt):
        """Applies direct movement based on input and handles collisions."""
        # --- Physics Calculation (Removed) ---
        # friction_force = self.velocity * self.friction
        # net_acceleration = self.acceleration + friction_force
        # self.velocity += net_acceleration * dt

        # Apply speed limit (Removed - Velocity is now set directly in get_keys)
        # if self.velocity.length_squared() > self.max_speed * self.max_speed:
        #     if self.velocity.length_squared() > 0:
        #          self.velocity.scale_to_length(self.max_speed)

        # Stop if velocity is negligible (Removed - Stops instantly when key is released)
        # if self.velocity.length_squared() < (0.5 * TILE_SIZE)**2:
        #     self.velocity = vec(0, 0)

        # --- Direct Movement Calculation ---
        # Calculate displacement based on desired change, speed, and delta time
        displacement = self.change * self.max_speed * dt

        # Calculate potential new position
        new_position = self.position + displacement

        # --- Collision Handling (Keep as is) ---
        self.position = self.collide_with_obstacles(new_position)

        # Update the sprite's rect center to the final calculated position
        self.rect.center = self.position


    def collide_with_obstacles(self, new_position):
        """Checks and resolves collisions with obstacle sprites."""
        potential_rect = self.rect.copy()
        potential_rect.center = new_position
        final_pos = new_position.copy() # Start assuming no collision

        # Check X-axis movement
        potential_rect.centerx = new_position.x
        potential_rect.centery = self.position.y # Keep Y fixed for X check
        for obstacle in self.game.obstacles:
            if potential_rect.colliderect(obstacle.rect):
                # Collision on X axis
                if self.velocity.x > 0: # Moving right
                    final_pos.x = obstacle.rect.left - self.rect.width / 2
                elif self.velocity.x < 0: # Moving left
                    final_pos.x = obstacle.rect.right + self.rect.width / 2
                self.velocity.x = 0 # Stop horizontal movement
                potential_rect.centerx = final_pos.x # Update rect for Y check
                break # Only resolve against the first obstacle hit on this axis

        # Check Y-axis movement (using potentially resolved X)
        potential_rect.centery = new_position.y
        for obstacle in self.game.obstacles:
            if potential_rect.colliderect(obstacle.rect):
                # Collision on Y axis
                if self.velocity.y > 0: # Moving down
                    final_pos.y = obstacle.rect.top - self.rect.height / 2
                elif self.velocity.y < 0: # Moving up
                    final_pos.y = obstacle.rect.bottom + self.rect.height / 2
                self.velocity.y = 0 # Stop vertical movement
                break # Only resolve against the first obstacle hit on this axis

        return final_pos


    def attack(self):
        """Performs a melee attack action."""
        # TODO: Implement proper melee cooldown
        # TODO: Implement better hitbox (arc, specific shape)
        if self.current_animation == ANIM_PLAYER_ATTACK: return # Prevent re-triggering during animation

        self.set_animation(ANIM_PLAYER_ATTACK)
        # Play attack sound
        # print("Player attacks!") # Placeholder

        # --- Simple Hitbox Check (Placeholder) ---
        # Create a rect slightly in front of the player based on facing direction
        hitbox_offset = 30 # How far in front
        hitbox_width = 40
        hitbox_height = self.rect.height * 0.8
        if self.facing_right:
             hitbox_center_x = self.rect.centerx + hitbox_offset
        else:
             hitbox_center_x = self.rect.centerx - hitbox_offset
        hitbox_center_y = self.rect.centery
        attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

        # Debug: Draw hitbox
        # pygame.draw.rect(self.game.screen, YELLOW, self.game.camera.apply_rect(attack_hitbox), 1)

        # Check for hits
        for enemy in self.game.enemies:
            if attack_hitbox.colliderect(enemy.rect):
                 if hasattr(enemy, 'take_damage'):
                      enemy.take_damage(MELEE_WEAPON_DAMAGE)
                      # print(f"Hit {type(enemy).__name__}!")


    def update(self, dt):
        """Main update loop for the player."""
        self.get_keys()       # Process input -> sets self.acceleration
        self.move(dt)         # Apply physics & collision -> updates self.position, self.velocity, self.rect
        self.update_radiation(dt) # Update radiation status
        self.pistol.update(dt)    # Update weapon state (handles reload timer)
        self.blood_system.update(dt) # Update particles

        # Update invincibility state
        if self.invincible and pygame.time.get_ticks() - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
            self.invincible = False
            # If hurt animation finished, revert to idle/move animation
            if self.current_animation == ANIM_PLAYER_HURT and self.animation_frame == 0:
                 self.set_animation(ANIM_PLAYER_IDLE)

        # Update animation based on current state AFTER physics/state updates
        self.update_animation(dt)


    def draw_weapon(self, screen, camera):
        """Draws weapon effects (muzzle flash) and particles."""
        self.pistol.draw(screen, camera)      # Draw pistol effects (e.g., muzzle flash)
        self.blood_system.draw(screen, camera) # Particles draw themselves relative to camera

    def has_reserve_ammo(self):
        """Check if player has ammo in reserve."""
        return self.reserve_ammo > 0

    def can_reload(self):
        """Check if the player needs to and can reload."""
        return (self.pistol.ammo_in_mag < PISTOL_MAGAZINE_SIZE and
                self.has_reserve_ammo())

    def take_ammo_from_reserve(self, amount_needed):
        """Takes ammo from reserve to reload the magazine."""
        can_take = min(amount_needed, self.reserve_ammo)
        self.reserve_ammo -= can_take
        return can_take

    def update_radiation(self, dt):
        """Updates radiation level and applies damage."""
        rad_change = 0
        if self.is_in_radioactive_zone: # This flag must be set correctly in Game.update
            increase_rate = RADIATION_INCREASE_RATE * 3
            if self.has_filter_module:
                increase_rate *= 0.1 # Filter reduces intake significantly
            rad_change = increase_rate * dt
        elif self.has_filter_module:
            # Filter slowly cleans radiation outside zones
            rad_change = -RADIATION_INCREASE_RATE * 0.5 * dt
        else:
            # Natural slow decay without filter
            rad_change = -RADIATION_INCREASE_RATE * 0.1 * dt

        self.radiation += rad_change
        self.radiation = max(0, min(RADIATION_MAX, self.radiation)) # Clamp 0-MAX

        # Apply damage if high radiation and no filter
        if self.radiation > RADIATION_DAMAGE_THRESHOLD and not self.has_filter_module:
            # Damage scales with how far above threshold
            over_threshold = self.radiation - RADIATION_DAMAGE_THRESHOLD
            max_over = RADIATION_MAX - RADIATION_DAMAGE_THRESHOLD
            damage_factor = over_threshold / max_over if max_over > 0 else 1
            damage_amount = RADIATION_DAMAGE_RATE * (1 + damage_factor) * dt # Base + scaled damage

            self.health -= damage_amount
            self.health = max(0, self.health)
            if self.health <= 0 and not self.game.cause_of_death: # Check if already dead
                self.game.cause_of_death = "radiation"
                self.game.playing = False # Signal game over


    def collect_filter_module(self):
        """Activates the filter module effect."""
        print("Player collected filter module!")
        self.has_filter_module = True


# --- Base Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    """Base class for all enemy characters."""
    def __init__(self, game, x_pixel, y_pixel, groups):
        self._layer = 2 # Render layer
        self.groups = groups
        super().__init__(self.groups)
        self.game = game

        # --- Attributes (Defaults - Subclasses MUST override) ---
        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.speed = 50 # Pixels per second
        self.invincibility_duration = ENEMY_INVINCIBILITY_DURATION

        # --- Position & Movement ---
        self.position = vec(x_pixel, y_pixel)
        self.velocity = vec(0, 0)
        self.rect = None # Must be set by subclass after loading image

        # --- AI & State ---
        self.ai_controller = None # Subclass MUST assign this
        self.last_hit_time = 0
        self.invincible = False

        # --- Effects ---
        self.blood_system = BloodParticleSystem()

        # --- Animation ---
        self.animations = {}
        self.current_animation = None # Start as None
        self.animation_frame = 0
        self.animation_frame_duration = 0.15 # Base duration
        self.animation_timer = 0
        self.facing_right = random.choice([True, False]) # Start facing random direction
        self.original_image = None # Store base frame
        self.image = None # Current frame to draw

    def setup_animations(self, sprite_dict_key):
        """Helper to load standard enemy animations using a base key."""
        if not SPRITESHEETS_LOADED: return False
        try:
            # Define standard animation strips (rect, num_frames)
            # !!! Adjust these rects and frame counts for YOUR enemy spritesheets !!!
            idle_strip = ((0, 0, 64, 64), 4)
            walk_strip = ((0, 0, 64, 64), 8)
            hurt_strip = ((0, 0, 64, 64), 3)
            attack_strip = ((0, 0, 64, 64), 6) # Assuming 'slash' is the attack

            # Use the provided key to get the correct Spritesheet object
            sheet = enemy_sprites[sprite_dict_key] # Use the key passed in

            self.animations = {
                ANIM_ENEMY_IDLE: sheet.load_strip(*idle_strip),
                ANIM_ENEMY_WALK: sheet.load_strip(*walk_strip),
                ANIM_ENEMY_HURT: sheet.load_strip(*hurt_strip),
                ANIM_ENEMY_SLASH: sheet.load_strip(*attack_strip) # Map generic 'attack'
            }

            if not self.animations[ANIM_ENEMY_IDLE]: # Validate
                raise ValueError(f"Failed to load '{ANIM_ENEMY_IDLE}' frames for key '{sprite_dict_key}'.")

            self.current_animation = ANIM_ENEMY_IDLE
            self.image = self.animations[ANIM_ENEMY_IDLE][0]
            self.original_image = self.image
            self.rect = self.image.get_rect(center=self.position)
            print(f"Animations loaded for {type(self).__name__}")
            return True

        except (KeyError, AttributeError, ValueError, Exception) as e:
            print(f"Error setting up animations for {type(self).__name__} using key '{sprite_dict_key}': {e}")
            self.animations = {}
            self.current_animation = None
            return False


    def set_animation(self, animation_name):
        """Safely sets the current animation."""
        if not self.animations or self.current_animation == animation_name:
            return
        if animation_name in self.animations:
             # Prevent interrupting hurt animation
             if self.current_animation == ANIM_ENEMY_HURT and self.animation_frame < len(self.animations[ANIM_ENEMY_HURT]) - 1:
                  return
             self.current_animation = animation_name
             self.animation_frame = 0
             self.animation_timer = 0
        else:
             # print(f"Warning: Anim '{animation_name}' not found for {type(self).__name__}")
             if ANIM_ENEMY_IDLE in self.animations: self.current_animation = ANIM_ENEMY_IDLE


    def update_animation(self, dt):
        """Updates the enemy's animation frame."""
        if not self.current_animation or not self.animations: return

        frames = self.animations[self.current_animation]
        num_frames = len(frames)
        if num_frames == 0: return

        current_frame_duration = self.animation_frame_duration
        if self.current_animation == ANIM_ENEMY_WALK:
            speed_mag = self.velocity.length()
            if speed_mag > 1.0 and self.speed > 0:
                 speed_factor = max(0.5, min(1.5, speed_mag / self.speed))
                 current_frame_duration = self.animation_frame_duration / speed_factor

        self.animation_timer += dt
        while self.animation_timer >= current_frame_duration:
            self.animation_timer -= current_frame_duration
            self.animation_frame = (self.animation_frame + 1) % num_frames
            if self.animation_frame == 0: # Loop completed
                 if self.current_animation in [ANIM_ENEMY_HURT, ANIM_ENEMY_SLASH]:
                      self.set_animation(ANIM_ENEMY_IDLE) # Revert to idle

        # Update image and handle flipping
        self.original_image = frames[self.animation_frame]
        self.image = self.original_image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)


    def move_towards(self, target_pos, dt):
        """Moves the enemy towards a target using velocity and handles basic collision."""
        direction = target_pos - self.position
        dist = direction.length()

        if dist > 1.0: # Check distance to avoid normalizing zero vector
            self.velocity = direction.normalize() * self.speed
            # Update facing direction based on horizontal velocity component
            if self.velocity.x > 0.1: self.facing_right = True
            elif self.velocity.x < -0.1: self.facing_right = False
            self.set_animation(ANIM_ENEMY_WALK)
        else:
            self.velocity = vec(0, 0) # Stop if very close
            self.set_animation(ANIM_ENEMY_IDLE)

        # Calculate potential new position
        new_position = self.position + self.velocity * dt
        # Check and resolve collisions
        self.position = self.collide_with_obstacles(new_position)
        # Update rectangle position
        self.rect.center = self.position

    def collide_with_obstacles(self, new_position):
         """Basic obstacle collision resolution for enemies."""
         potential_rect = self.rect.copy()
         potential_rect.center = new_position
         for obstacle in self.game.obstacles:
              if potential_rect.colliderect(obstacle.rect):
                   # Simplest resolution: stop movement entirely if collision
                   self.velocity = vec(0, 0)
                   return self.position # Return current position (no move)
         # No collision detected
         return new_position


    def take_damage(self, amount):
        """Handles enemy taking damage."""
        # Optional: Add invincibility check if desired for enemies
        # now = pygame.time.get_ticks()
        # if self.invincible and now - self.last_hit_time < self.invincibility_duration:
        #     return

        self.health -= amount
        self.health = max(0, self.health)
        self.blood_system.add_particles(self.rect.centerx, self.rect.centery, count=3)
        self.set_animation(ANIM_ENEMY_HURT)
        # self.last_hit_time = now
        # self.invincible = True

        # Notify AI controller about the damage event
        if self.ai_controller:
            # Provide the player's position as the likely source
            self.ai_controller.alert_damage(self.game.player.position)

        if self.health <= 0:
            self.kill() # Remove sprite from all groups when health is zero


    def draw_health_bar(self, screen, camera):
        """Draws the health bar above the enemy."""
        if self.health <= 0 or self.max_health <= 0 or not self.rect: return

        health_pct = max(0.0, min(1.0, self.health / self.max_health))
        bar_width = ENEMY_HEALTH_BAR_WIDTH
        bar_height = ENEMY_HEALTH_BAR_HEIGHT

        # Calculate screen position using camera's apply_rect method for consistency
        screen_rect = camera.apply(self)
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - ENEMY_HEALTH_BAR_OFFSET - bar_height # Position above

        # Interpolate color
        color_r = int(ENEMY_HEALTH_BAR_COLOR_MIN[0] + (ENEMY_HEALTH_BAR_COLOR_MAX[0] - ENEMY_HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(ENEMY_HEALTH_BAR_COLOR_MIN[1] + (ENEMY_HEALTH_BAR_COLOR_MAX[1] - ENEMY_HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(ENEMY_HEALTH_BAR_COLOR_MIN[2] + (ENEMY_HEALTH_BAR_COLOR_MAX[2] - ENEMY_HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_color = (max(0,min(255,color_r)), max(0,min(255,color_g)), max(0,min(255,color_b)))

        # Draw
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_pct), bar_height)
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BACKGROUND_COLOR, bg_rect)
        if health_pct > 0:
            pygame.draw.rect(screen, current_color, fill_rect)
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BORDER_COLOR, bg_rect, 1)


    def update(self, dt):
        """Base enemy update method. Calls AI and updates animation/particles."""
        # Update AI -> AI controller should handle setting velocity/triggering attacks
        if self.ai_controller:
            self.ai_controller.update(dt) # AI logic determines movement/actions

        # Update position based on velocity set by AI (and handle collisions)
        # This assumes AI sets self.velocity or calls a move function like move_towards
        # If AI directly modifies position, collision needs to be handled there or after.
        # If AI sets velocity:
        new_position = self.position + self.velocity * dt
        self.position = self.collide_with_obstacles(new_position)
        if self.rect: # Ensure rect exists
             self.rect.center = self.position


        # Update animation state
        self.update_animation(dt)

        # Update particle effects
        self.blood_system.update(dt)


    def draw(self, screen, camera):
        """Draws the enemy sprite, health bar, and blood particles."""
        if not self.rect: return # Don't draw if rect is not initialized

        # Calculate screen position using camera
        screen_rect = camera.apply(self)

        # Cull drawing if off-screen
        if screen_rect.colliderect(screen.get_rect()):
            if self.image:
                screen.blit(self.image, screen_rect)
            else: # Fallback draw (e.g., red rect)
                fallback_rect = pygame.Rect(screen_rect.left, screen_rect.top, ENEMY_WIDTH, ENEMY_HEIGHT)
                pygame.draw.rect(screen, RED, fallback_rect)

            # Draw health bar only if visible
            self.draw_health_bar(screen, camera)

        # Draw blood particles (they handle their own camera adjustment)
        self.blood_system.draw(screen, camera)


# --- Raider Enemy Class ---
class Raider(Enemy):
    """Specific Raider enemy implementation."""
    def __init__(self, game, x_pixel, y_pixel):
        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        # --- Raider Specific Attributes ---
        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED * TILE_SIZE # Assuming speed was tiles/sec

        # --- Setup Appearance and AI ---
        # Use 'base' key if all enemy anims are in one sheet, or a specific key like 'raider'
        if not self.setup_animations(SPRITESHEET_KEY_BASE): # Check return value
             # Fallback if animations failed
             self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
             self.image.fill(ENEMY_RAIDER_COLOR)
             self.rect = self.image.get_rect(center=self.position)

        self.ai_controller = RaiderAIController(self) # Assign Raider AI

    def attack(self):
        """Raider's melee attack action. Called by AI."""
        if self.current_animation == ANIM_ENEMY_SLASH: return # Don't re-attack mid-swing

        self.set_animation(ANIM_ENEMY_SLASH)
        # Play attack sound
        # print(f"Raider at {self.position} attacks!")

        # --- Simple Hitbox Check (Placeholder) ---
        hitbox_offset = TILE_SIZE * 0.6 # Adjust range
        hitbox_width = TILE_SIZE * 0.8
        hitbox_height = self.rect.height * 0.9
        if self.facing_right:
             hitbox_center_x = self.rect.centerx + hitbox_offset
        else:
             hitbox_center_x = self.rect.centerx - hitbox_offset
        hitbox_center_y = self.rect.centery
        attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

        # Check collision with player
        if attack_hitbox.colliderect(self.game.player.rect):
             self.game.player.take_damage(self.damage)

    # Raider inherits update() and draw() from the base Enemy class


# --- WildDog Enemy Class ---
class WildDog(Enemy):
    """Specific Wild Dog enemy implementation."""
    def __init__(self, game, x_pixel, y_pixel):
        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        # --- Wild Dog Specific Attributes ---
        self.health = ENEMY_DOG_HEALTH
        self.max_health = ENEMY_DOG_HEALTH
        self.damage = ENEMY_DOG_DAMAGE
        self.speed = ENEMY_DOG_SPEED * TILE_SIZE # Assuming speed was tiles/sec

        # --- Setup Appearance and AI ---
        if not self.setup_animations(SPRITESHEET_KEY_BASE): # Use 'base' or specific key like 'dog'
             # Fallback
             # Make dog slightly smaller visually if desired
             dog_width = int(ENEMY_WIDTH * 0.8)
             dog_height = int(ENEMY_HEIGHT * 0.8)
             self.image = pygame.Surface((dog_width, dog_height))
             self.image.fill(ENEMY_DOG_COLOR)
             self.rect = self.image.get_rect(center=self.position)

        self.ai_controller = WildDogAIController(self) # Assign Dog AI

    def attack(self):
        """Wild Dog's bite attack action. Called by AI."""
        if self.current_animation == ANIM_ENEMY_SLASH: return

        self.set_animation(ANIM_ENEMY_SLASH) # Use a bite/lunge animation
        # Play bite sound
        # print(f"Wild Dog at {self.position} bites!")

        # Simple proximity check for bite
        attack_range = ENEMY_ATTACK_RADIUS * 0.7 # Dogs might have shorter reach
        if self.position.distance_squared_to(self.game.player.position) < attack_range**2:
             self.game.player.take_damage(self.damage)

    # WildDog inherits update() and draw() from the base Enemy class
