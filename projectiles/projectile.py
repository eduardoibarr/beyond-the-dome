import pygame
from core.settings import *

vec = pygame.math.Vector2


class Bullet(pygame.sprite.Sprite):
    """Represents a bullet projectile in the game."""

    def __init__(self, game, start_pos, direction, speed):
        """
        Initializes a Bullet instance.

        Args:
            game: The main game object.
            start_pos (vec): The starting position of the bullet.
            direction (vec): The direction the bullet will travel.
            speed (float): The speed of the bullet.
        """
        self.groups = game.all_sprites, game.bullets
        super().__init__(self.groups)
        self.game = game
        self.position = vec(start_pos)
        self.direction = direction.normalize()
        self.speed = speed
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=self.position)
        self.damage = BULLET_DAMAGE

    def update(self, dt):
        """
        Updates the bullet's position and checks for collisions.

        Args:
            dt (float): The time elapsed since the last frame.
        """
        self.position += self.direction * self.speed * dt
        self.rect.center = self.position

        # Check for collisions with obstacles
        if self.collide_with_obstacles():
            self.kill()  # Remove the bullet if it hit an obstacle

        # Check for collisions with enemies
        if self.collide_with_enemies():
            self.kill()

    def collide_with_obstacles(self):
        """Checks if the bullet collides with any obstacle."""
        for obstacle in self.game.obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True
        return False

    def collide_with_enemies(self):
        """Checks if the bullet collides with any enemy."""
        for enemy in self.game.enemies:
            if self.rect.colliderect(enemy.rect):
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(self.damage)
                return True
        return False

    def draw(self, screen, camera):
        """
        Draws the bullet onto the screen.

        Args:
            screen: The screen surface to draw on.
            camera: The camera object for coordinate transformation.
        """
        screen_rect = camera.apply(self)
        if screen_rect.colliderect(screen.get_rect()):
            screen.blit(self.image, screen_rect)