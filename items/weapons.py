import pygame
import math
from settings import *
# Assuming projectiles.py contains the Bullet class
try:
    from projectiles import Bullet
except ImportError:
    print("Warning: Could not import Bullet from projectiles.py. Pistol cannot fire.")
    # Define dummy class if missing
    class Bullet:
        def __init__(self, game, start_pos, direction, speed): pass

vec = pygame.math.Vector2

# Classe da Pistola
class Pistol:
    """Manages the player's pistol weapon."""
    def __init__(self, game, player):
        """
        Initializes the Pistol.
        Args:
            game (Game): Reference to the main game object.
            player (Player): Reference to the player sprite.
        """
        self.game = game
        self.player = player
        self.last_shot_time = 0        # Timestamp of the last shot fired
        self.reloading = False
        self.reload_start_time = 0
        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE # Start with a full magazine
        self.muzzle_flash_timer = 0 # For drawing muzzle flash

    def can_shoot(self):
        """Checks if the pistol can fire (fire rate, reloading, ammo)."""
        now = pygame.time.get_ticks()
        return (not self.reloading and
                self.ammo_in_mag > 0 and
                now - self.last_shot_time > PISTOL_FIRE_RATE)

    def start_reload(self):
        """Initiates the reloading sequence if needed and possible."""
        # Check if already reloading or mag is full
        if self.reloading or self.ammo_in_mag == PISTOL_MAGAZINE_SIZE:
            return
        # Check if player has reserve ammo (implement in Player class)
        if self.player.can_reload():
            print("Reloading...") # Debug/Sound cue
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            # Play reload sound
            # self.game.sound_manager.play('pistol_reload_start')

    def finish_reload(self):
        """Completes the reload sequence."""
        needed_ammo = PISTOL_MAGAZINE_SIZE - self.ammo_in_mag
        transferred_ammo = self.player.take_ammo_from_reserve(needed_ammo)
        self.ammo_in_mag += transferred_ammo
        self.reloading = False
        print(f"Reload finished. Ammo: {self.ammo_in_mag}/{self.player.reserve_ammo}") # Debug
        # Play reload end sound
        # self.game.sound_manager.play('pistol_reload_end')

    def shoot(self, target_world_pos):
        """
        Fires a bullet towards the target world position if possible.
        Args:
            target_world_pos (vec): The target position in world coordinates.
        """
        if not self.can_shoot():
            # Optionally trigger reload if out of ammo
            if not self.reloading and self.ammo_in_mag <= 0:
                 self.start_reload()
            # Play empty click sound?
            # self.game.sound_manager.play('pistol_empty')
            return

        now = pygame.time.get_ticks()
        self.last_shot_time = now
        self.ammo_in_mag -= 1
        self.muzzle_flash_timer = now # Start muzzle flash timer

        # --- Calculate Shot Parameters ---
        # Calculate direction vector from player center to target world position
        start_pos_world = vec(self.player.position) # Use player's precise world position
        direction = target_world_pos - start_pos_world
        if direction.length_squared() > 0: # Avoid normalizing zero vector
             direction = direction.normalize()
        else:
             # Default direction (e.g., based on player facing) if target is same as player
             direction = vec(1, 0) if self.player.facing_right else vec(-1, 0)

        # Calculate spawn position slightly in front of the player
        # Use player's rect size for offset calculation
        offset_dist = self.player.rect.width / 2 + BULLET_WIDTH / 2 # Spawn just outside player radius
        spawn_pos = start_pos_world + direction * offset_dist

        # Apply some recoil/spread (optional)
        # angle_offset = random.uniform(-PISTOL_SPREAD_ANGLE, PISTOL_SPREAD_ANGLE)
        # direction = direction.rotate(angle_offset)

        # --- Create the Bullet Projectile ---
        # print(f"Shooting bullet! Dir: {direction}") # Debug
        Bullet(self.game, spawn_pos, direction, BULLET_SPEED) # Create the projectile
        # Play shooting sound
        self.game.play_audio('pistol_fire') # Toca o som carregado

        # Apply visual recoil to player (optional, handled in Player?)
        # self.player.apply_recoil(direction * -1 * PISTOL_RECOIL_AMOUNT)

        # Check if we need to reload after this shot
        if self.ammo_in_mag <= 0:
             self.start_reload()


    def update(self, dt):
        """
        Updates the pistol state, primarily handling reloading timer.
        Args:
             dt (float): Delta time in seconds.
        """
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start_time > PISTOL_RELOAD_TIME:
                self.finish_reload()

        # Mouse button handling is done in Player.get_keys

    def draw(self, screen, camera):
        """
        Draws weapon effects like muzzle flash.
        Args:
            screen (pygame.Surface): The main display surface.
            camera (Camera): The game camera object.
        """
        now = pygame.time.get_ticks()
        if self.muzzle_flash_timer > 0 and now - self.muzzle_flash_timer < PISTOL_MUZZLE_FLASH_DURATION:
            # Calculate flash position (end of barrel)
            # Need direction player is aiming (or just facing direction for simplicity)
            direction = vec(1, 0) if self.player.facing_right else vec(-1, 0)
            offset_dist = self.player.rect.width * 0.6 # Adjust as needed
            flash_pos_world = self.player.position + direction * offset_dist
            flash_pos_screen = camera.apply_coords(*flash_pos_world)

            # Draw flash
            flash_radius = PISTOL_MUZZLE_FLASH_SIZE // 2
            pygame.draw.circle(screen, PISTOL_MUZZLE_FLASH_COLOR, flash_pos_screen, flash_radius)
            # Or use a small sprite/image
        else:
             self.muzzle_flash_timer = 0 # Ensure timer is reset

# --- Removed Slingshot specific methods (get_charge_percent, is_shooting) ---

# --- Camera Helper Method comments removed ---

