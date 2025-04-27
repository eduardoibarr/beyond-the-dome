# Importação das bibliotecas necessárias
import pygame
import math
from settings import * # Assuming settings.py is in the same directory

# Classe da Bala (projétil)
class Bullet(pygame.sprite.Sprite):
    """Represents a bullet projectile fired by the player."""
    def __init__(self, game, start_pos, direction, speed):
        """
        Initializes the Bullet sprite.
        Args:
            game (Game): Reference to the main game object.
            start_pos (tuple or pygame.math.Vector2): Initial position (x, y) in world coordinates.
            direction (pygame.math.Vector2): Normalized direction vector for the bullet.
            speed (float): The speed of the bullet in pixels per second.
        """
        # self._layer = 4 # Projectile layer
        self.groups = game.all_sprites, game.bullets # Use a new group for bullets
        super().__init__(self.groups)
        self.game = game

        # --- Position and Movement ---
        self.pos = pygame.math.Vector2(start_pos)
        if direction.length_squared() > 0:
             self.direction = direction.normalize()
        else:
             self.direction = pygame.math.Vector2(1, 0) # Default direction

        # Store angle for rotation
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))

        self.speed = speed
        self.velocity = self.direction * self.speed
        self.spawn_time = pygame.time.get_ticks()

        # --- Appearance ---
        # Create a base image (horizontal rectangle)
        self.base_image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        self.base_image.fill(BULLET_COLOR)
        # Rotate the base image according to the direction
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        # --- Combat ---
        self.damage = BULLET_DAMAGE

    def update(self, dt):
        """
        Updates the bullet's position and checks lifetime/boundaries/collisions.
        Args:
            dt (float): Delta time in seconds.
        """
        # --- Lifetime Check ---
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
            return

        # --- Movement ---
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # --- Boundary Check (Map Bounds) ---
        buffer = TILE_SIZE
        if (self.pos.x < -buffer or self.pos.x > MAP_WIDTH + buffer or
            self.pos.y < -buffer or self.pos.y > MAP_HEIGHT + buffer):
            self.kill()
            return

        # --- Collision Handling (Check against obstacles and enemies) ---
        self.check_collisions()

    def check_collisions(self):
        """Checks for collisions with obstacles and enemies."""
        # Check obstacles first
        obstacle_hits = pygame.sprite.spritecollide(self, self.game.obstacles, False)
        if obstacle_hits:
            self.kill() # Bullet hits a wall
            # TODO: Add impact effect/sound?
            return

        # Check enemies
        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in enemy_hits:
            if hasattr(enemy, 'take_damage'):
                enemy.take_damage(self.damage)
            self.kill() # Bullet is destroyed on hit
            # TODO: Add hit effect/sound?
            return # Exit after first hit
