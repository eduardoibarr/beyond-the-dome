import pygame
from core.settings import BULLET_DAMAGE, BULLET_RENDER_LAYER, BULLET_COLOR, BULLET_WIDTH, BULLET_HEIGHT, FX_RENDER_LAYER, BLACK
vec = pygame.math.Vector2
import random
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, direction, speed, bullet_type="pistol"):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self._layer = BULLET_RENDER_LAYER
        self.damage = BULLET_DAMAGE
        self.position = vec(start_pos)
        self.velocity = direction * speed
        self.bullet_type = bullet_type
        
        # Criar sprite visual da bala
        self.image = self.create_bullet_sprite()
        self.rect = self.image.get_rect(center=self.position)
        
        # Para rotação da bala
        self.angle = math.degrees(math.atan2(direction.y, direction.x))

    def create_bullet_sprite(self):
        """Cria um sprite visual para a bala baseado no tipo"""
        if self.bullet_type == "pistol":
            # Bala pequena amarelada
            bullet = pygame.Surface((8, 3), pygame.SRCALPHA)
            pygame.draw.ellipse(bullet, (255, 255, 150), (0, 0, 8, 3))
            pygame.draw.ellipse(bullet, (255, 255, 200), (1, 0, 6, 2))
        elif self.bullet_type == "rifle":
            # Bala maior
            bullet = pygame.Surface((12, 4), pygame.SRCALPHA)
            pygame.draw.ellipse(bullet, (255, 200, 100), (0, 0, 12, 4))
            pygame.draw.ellipse(bullet, (255, 255, 150), (2, 1, 8, 2))
        else:
            # Bala padrão
            bullet = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
            bullet.fill(BULLET_COLOR)
        
        return bullet

    def update(self, dt):
        self.position += self.velocity * dt
        
        # Rotacionar a bala baseado na direção
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.rect = rotated_image.get_rect(center=self.position)

        if self.collide_with_obstacles():
            self.create_impact_effect()
            self.kill()
            return

        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in enemy_hits:
            if hasattr(enemy, 'take_damage'):
                enemy.take_damage(self.damage)
                self.create_blood_effect()
                self.kill()
                return

        if self.off_screen():
            self.kill()

    def create_impact_effect(self):
        """Cria efeito de impacto quando a bala atinge um obstáculo"""
        # Pequenas partículas de poeira/detritos
        for _ in range(3):
            particle_pos = self.position + vec(random.uniform(-5, 5), random.uniform(-5, 5))
            ImpactParticle(self.game, particle_pos)

    def create_blood_effect(self):
        """Cria efeito de sangue quando a bala atinge um inimigo"""
        for _ in range(5):
            particle_pos = self.position + vec(random.uniform(-8, 8), random.uniform(-8, 8))
            BloodParticle(self.game, particle_pos)

    def off_screen(self):
        if self.rect.right < 0 or self.rect.left > self.game.map_width:
            return True
        if self.rect.bottom < 0 or self.rect.top > self.game.map_height:
            return True
        return False

    def collide_with_obstacles(self):
        for obstacle in self.game.obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True
        return False
        
    def draw(self, screen, camera):
        screen_rect = camera.apply(self)
        # Rotacionar a imagem antes de desenhar
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=screen_rect.center)
        screen.blit(rotated_image, rotated_rect)

class Rocket(pygame.sprite.Sprite):
    """Projétil de foguete com sprite visual"""
    def __init__(self, game, start_pos, direction, speed):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self._layer = BULLET_RENDER_LAYER
        self.damage = BULLET_DAMAGE * 3  # Foguetes fazem mais dano
        self.position = vec(start_pos)
        self.velocity = direction * speed
        
        # Carregar sprite do foguete
        try:
            self.image = game.asset_manager.get_image("assets/images/tds-modern-hero-weapons-and-props/rocket/rocket1.png")
            if self.image:
                self.image = pygame.transform.scale(self.image, (20, 8))
            else:
                raise Exception("Sprite não encontrado")
        except:
            # Fallback para sprite simples
            self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (200, 100, 50), (0, 0, 20, 8))
            pygame.draw.ellipse(self.image, (255, 150, 100), (2, 2, 16, 4))
        
        self.rect = self.image.get_rect(center=self.position)
        self.angle = math.degrees(math.atan2(direction.y, direction.x))
        
        # Efeito de rastro
        self.trail_timer = 0

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position
        
        # Criar rastro de fumaça
        self.trail_timer += dt
        if self.trail_timer > 0.05:  # A cada 50ms
            TrailParticle(self.game, self.position)
            self.trail_timer = 0

        if self.collide_with_obstacles():
            self.create_explosion()
            self.kill()
            return

        enemy_hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in enemy_hits:
            if hasattr(enemy, 'take_damage'):
                # Foguetes fazem dano em área
                self.create_explosion()
                self.damage_area()
                self.kill()
                return

        if self.off_screen():
            self.kill()

    def create_explosion(self):
        """Cria uma explosão visual"""
        for _ in range(15):
            particle_pos = self.position + vec(random.uniform(-20, 20), random.uniform(-20, 20))
            ExplosionParticle(self.game, particle_pos)

    def damage_area(self):
        """Causa dano em área ao redor da explosão"""
        explosion_radius = 50
        for enemy in self.game.enemies:
            distance = (enemy.rect.center - self.position).length()
            if distance <= explosion_radius:
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(self.damage)

    def collide_with_obstacles(self):
        for obstacle in self.game.obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True
        return False

    def off_screen(self):
        if self.rect.right < 0 or self.rect.left > self.game.map_width:
            return True
        if self.rect.bottom < 0 or self.rect.top > self.game.map_height:
            return True
        return False

    def draw(self, screen, camera):
        screen_rect = camera.apply(self)
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=screen_rect.center)
        screen.blit(rotated_image, rotated_rect)

class ImpactParticle(pygame.sprite.Sprite):
    """Partícula de impacto quando bala atinge obstáculo"""
    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = FX_RENDER_LAYER
        
        self.image = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150, 150, 100), (1, 1), 1)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = vec(pos)
        self.vel = vec(random.uniform(-30, 30), random.uniform(-30, 30))
        self.lifetime = random.uniform(0.2, 0.5)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        if (pygame.time.get_ticks() - self.spawn_time) / 1000 > self.lifetime:
            self.kill()

class BloodParticle(pygame.sprite.Sprite):
    """Partícula de sangue quando bala atinge inimigo"""
    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = FX_RENDER_LAYER
        
        self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150, 20, 20), (1, 1), 1)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = vec(pos)
        self.vel = vec(random.uniform(-50, 50), random.uniform(-50, 50))
        self.lifetime = random.uniform(0.3, 0.8)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        if (pygame.time.get_ticks() - self.spawn_time) / 1000 > self.lifetime:
            self.kill()

class TrailParticle(pygame.sprite.Sprite):
    """Partícula de rastro para foguetes"""
    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = FX_RENDER_LAYER
        
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (100, 100, 100, 150), (2, 2), 2)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = vec(pos)
        self.vel = vec(random.uniform(-10, 10), random.uniform(-10, 10))
        self.lifetime = random.uniform(0.5, 1.0)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        # Fade out effect
        time_alive = (pygame.time.get_ticks() - self.spawn_time) / 1000
        if time_alive > self.lifetime:
            self.kill()
        else:
            alpha = int(255 * (1 - time_alive / self.lifetime))
            self.image.set_alpha(alpha)

class ExplosionParticle(pygame.sprite.Sprite):
    """Partícula de explosão"""
    def __init__(self, game, pos):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = FX_RENDER_LAYER
        
        size = random.randint(3, 8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        colors = [(255, 100, 0), (255, 150, 0), (255, 200, 100)]
        color = random.choice(colors)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = vec(pos)
        self.vel = vec(random.uniform(-100, 100), random.uniform(-100, 100))
        self.lifetime = random.uniform(0.3, 0.8)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        time_alive = (pygame.time.get_ticks() - self.spawn_time) / 1000
        if time_alive > self.lifetime:
            self.kill()
        else:
            alpha = int(255 * (1 - time_alive / self.lifetime))
            self.image.set_alpha(alpha)

class Casing(pygame.sprite.Sprite):
    def __init__(self, game, pos, player_facing_right, weapon_type="pistol"):
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = FX_RENDER_LAYER
        
        # Criar sprite baseado no tipo de arma
        if weapon_type == "pistol":
            self.image_orig = pygame.Surface((6, 3), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image_orig, (200, 180, 0), (0, 0, 6, 3))
            pygame.draw.ellipse(self.image_orig, (220, 200, 20), (1, 0, 4, 2))
        elif weapon_type == "rifle":
            self.image_orig = pygame.Surface((8, 4), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image_orig, (180, 160, 0), (0, 0, 8, 4))
            pygame.draw.ellipse(self.image_orig, (200, 180, 20), (1, 1, 6, 2))
        else:
            # Casquinha padrão
            self.image_orig = pygame.Surface((5, 3))
            self.image_orig.fill((200, 180, 0))
            self.image_orig.set_colorkey(BLACK)
        
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=pos)

        self.pos = vec(pos)

        # Ejeção mais realista baseada na direção do jogador
        eject_x = random.uniform(20, 40) if player_facing_right else random.uniform(-40, -20)
        self.vel = vec(eject_x, random.uniform(-100, -140))
        self.acc = vec(0, 500)

        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-360, 360)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = random.uniform(800, 1200)  # Varia um pouco mais
        
        # Som de casquinha caindo (pode ser adicionado depois)
        self.bounce_count = 0
        self.max_bounces = random.randint(1, 3)

    def update(self, dt):
        self.vel += self.acc * dt
        old_pos = self.pos.copy()
        self.pos += self.vel * dt

        # Simular quique no chão
        if hasattr(self.game, 'map_height'):
            ground_level = self.game.map_height - 50  # Assumindo algum nível do chão
            if self.pos.y > ground_level and self.bounce_count < self.max_bounces:
                self.pos.y = ground_level
                self.vel.y = -self.vel.y * 0.3  # Quique com perda de energia
                self.vel.x *= 0.7  # Atrito
                self.bounce_count += 1
                
                # Som de casquinha batendo no chão (opcional)
                if hasattr(self.game, 'play_audio'):
                    self.game.play_audio('casing_drop', volume=0.1)

        self.angle = (self.angle + self.rot_speed * dt) % 360
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
