import pygame
from settings import *
from ai import RaiderAIController, WildDogAIController
from weapons import Slingshot
from particles import BloodParticleSystem
from spritesheet import Spritesheet

vec = pygame.math.Vector2

# Carregar spritesheets
player_sprites = {
    'idle': Spritesheet('sprites/run.png'),    # Animação de repouso - jogador parado
    'run': Spritesheet('sprites/run.png'),     # Animação de corrida - movimento rápido
    'walk': Spritesheet('sprites/run.png'),    # Animação de caminhada - movimento normal
    'hurt': Spritesheet('sprites/run.png'),    # Animação de dano - quando recebe hit
    'shoot': Spritesheet('sprites/run.png'),   # Animação de tiro - usando estilingue
    'attack': Spritesheet('sprites/run.png'),  # Animação de ataque - corpo a corpo
}

enemy_sprites = {
    'idle': Spritesheet('sprites/run.png'),    # Animação de repouso - inimigo parado
    'walk': Spritesheet('sprites/run.png'),    # Animação de caminhada - patrulhando
    'hurt': Spritesheet('sprites/run.png'),    # Animação de dano - quando recebe hit
    'slash': Spritesheet('sprites/run.png'),   # Animação de ataque - golpe corpo a corpo
}

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Carrega sprites para as animações
        self.animations = {
            'idle': player_sprites['idle'].load_strip((0, 0, 64, 64), 4),    # 4 frames de repouso
            'run': player_sprites['run'].load_strip((0, 0, 64, 64), 8),      # 8 frames de corrida
            'walk': player_sprites['walk'].load_strip((0, 0, 64, 64), 4),    # 4 frames de caminhada
            'hurt': player_sprites['hurt'].load_strip((0, 0, 64, 64), 3),    # 3 frames de dano
            'shoot': player_sprites['shoot'].load_strip((0, 0, 64, 64), 4),  # 4 frames de tiro
            'attack': player_sprites['attack'].load_strip((0, 0, 64, 64), 6) # 6 frames de ataque
        }
        
        # Configura animação inicial
        self.current_animation = 'idle'  # Animação atual
        self.animation_frame = 0         # Frame atual da animação
        self.animation_speed = 0.15      # Tempo entre frames em segundos
        self.animation_time = 0          # Tempo acumulado da animação
        self.facing_right = True         # Direção para qual o sprite está olhando
        
        # Configura sprite inicial
        self.image = self.animations[self.current_animation][0]  # Primeiro frame da animação
        self.original_image = self.image  # Imagem original (sem efeitos)
        self.rect = self.image.get_rect() # Retângulo de colisão
        
        # Posição e movimento
        self.x = x * TILE_SIZE           # Posição X em pixels
        self.y = y * TILE_SIZE           # Posição Y em pixels
        self.pos = vec(self.x, self.y)   # Vetor de posição
        self.rect.centerx = self.x       # Centro X do retângulo
        self.rect.bottom = self.y + TILE_SIZE  # Base do sprite alinhada com o tile
        self.vx, self.vy = 0, 0          # Velocidade em X e Y
        
        # Atributos do jogador
        self.health = PLAYER_HEALTH      # Vida atual
        self.max_health = PLAYER_HEALTH  # Vida máxima
        self.last_hit_time = 0           # Tempo do último dano
        self.invincible = False          # Estado de invencibilidade
        self.stone_count = STONE_INITIAL_COUNT  # Quantidade de pedras
        self.slingshot = Slingshot(game, self)  # Arma do jogador
        self.blood_system = BloodParticleSystem()  # Sistema de partículas de sangue
        
    def take_damage(self, amount):
        # Recebe dano do inimigo
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= amount  # Reduz vida
            # Cria partículas de sangue no ponto de impacto
            for _ in range(3):
                self.blood_system.add_particles(self.rect.centerx, self.rect.centery)
            self.last_hit_time = now
            self.invincible = True  # Ativa invencibilidade temporária
            self.set_animation('hurt')  # Muda para animação de dano
            if self.health <= 0:
                self.kill()  # Remove o jogador se morrer
                self.game.playing = False  # Termina o jogo
                
    def set_animation(self, animation_name):
        # Muda a animação atual
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.animation_frame = 0  # Reseta para o primeiro frame
            self.animation_time = 0   # Reseta o tempo da animação
                
    def update_animation(self, dt):
        # Atualiza a animação atual
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            # Avança para o próximo frame, voltando ao início se necessário
            self.animation_frame = (self.animation_frame + 1) % len(self.animations[self.current_animation])
        
        # Obtém o frame atual
        current_frame = self.animations[self.current_animation][self.animation_frame]
        
        # Inverte o sprite se estiver olhando para a esquerda
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
            
        # Aplica efeitos visuais (como piscar quando invencível)
        now = pygame.time.get_ticks()
        if self.invincible:
            # Alterna transparência para efeito de piscar
            alpha = 128 if now % 200 < 100 else 255
            temp_image = current_frame.copy().convert_alpha()
            temp_image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = temp_image
        else:
            self.image = current_frame
            
        # Atualiza a imagem original (sem efeitos)
        self.original_image = current_frame
    
    def get_keys(self):
        # Processa entrada do teclado
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        
        # Movimento horizontal
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False  # Olha para a esquerda
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            self.facing_right = True   # Olha para a direita
            
        # Movimento vertical
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED
            
        # Normaliza velocidade diagonal (evita movimento mais rápido na diagonal)
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071  # 1/√2
            self.vy *= 0.7071
            
        # Define animação com base no movimento
        if self.vx != 0 or self.vy != 0:
            self.set_animation('run')  # Movendo = animação de corrida
        else:
            if self.slingshot.charging:
                self.set_animation('shoot')  # Carregando tiro = animação de tiro
            else:
                self.set_animation('idle')  # Parado = animação de repouso
                
        # Verifica ataque corpo a corpo
        if keys[pygame.K_SPACE]:
            self.attack()

    def move(self, dx=0, dy=0):
        # Move o jogador
        self.x += dx
        self.y += dy
        
    def attack(self):
        # Executa ataque corpo a corpo
        self.set_animation('attack')
        # Verifica colisões com inimigos
        for sprite in self.game.enemies:
            if pygame.sprite.collide_rect(self, sprite):
                sprite.take_damage(MELEE_WEAPON_DAMAGE)  # Causa dano ao inimigo

    def update(self):
        # Atualização do jogador
        dt = self.game.dt  # Delta time para animações suaves
        
        # Atualiza estado de invencibilidade
        now = pygame.time.get_ticks()
        if self.invincible and now - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
            self.invincible = False  # Desativa invencibilidade após o tempo
            if self.current_animation == 'hurt':
                self.set_animation('idle')  # Volta para animação normal

        # Processa entrada e movimento
        self.get_keys()
        self.move(self.vx, self.vy)
        
        # Atualiza a posição do retângulo
        self.rect.centerx = self.x
        self.rect.bottom = self.y + TILE_SIZE // 2
        
        # Atualiza outros componentes
        self.slingshot.update()  # Atualiza estado da estilingue
        self.blood_system.update()  # Atualiza partículas de sangue
        
        # Atualiza a animação
        self.update_animation(dt)

    def draw_weapon(self, screen):
        # Desenha a arma e partículas de sangue
        self.slingshot.draw(screen)  # Desenha a estilingue
        self.blood_system.draw(screen)  # Desenha partículas de sangue

    def has_stones(self):
        # Verifica se tem pedras para atirar
        return self.stone_count > 0
        
    def use_stone(self):
        # Usa uma pedra para atirar
        if self.stone_count > 0:
            self.stone_count -= 1  # Reduz contagem de pedras
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, groups):
        self._layer = 2  # Camada de renderização (acima do chão)
        self.groups = groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = None
        self.rect = None
        self.pos = vec(x * TILE_SIZE, y * TILE_SIZE)  # Posição em pixels
        self.vel = vec(0, 0)  # Velocidade
        self.acc = vec(0, 0)  # Aceleração
        self.health = 0       # Vida atual
        self.max_health = 0   # Vida máxima
        self.damage = 0       # Dano causado
        self.speed = 0        # Velocidade de movimento
        self.ai_controller = None  # Controlador de IA
        self.blood_system = BloodParticleSystem()  # Sistema de partículas de sangue

    def move(self, dx, dy):
        # Move o inimigo
        self.pos += vec(dx, dy)
        self.rect.center = self.pos

    def take_damage(self, amount):
        # Recebe dano
        self.health -= amount
        # Cria partículas de sangue no ponto de impacto
        for _ in range(3):
            self.blood_system.add_particles(self.rect.centerx, self.rect.centery)
        if self.ai_controller:
            # Alerta a IA sobre o dano para reagir
            self.ai_controller.alert_damage(vec(self.game.player.rect.center))
        if self.health <= 0:
            self.kill()  # Remove o inimigo se morrer

    def draw_health_bar(self, screen):
        # Desenha a barra de vida
        if self.health <= 0:
            return

        # Calcula porcentagem de vida
        health_pct = self.health / self.max_health
        bar_width = ENEMY_HEALTH_BAR_WIDTH
        bar_height = ENEMY_HEALTH_BAR_HEIGHT
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - ENEMY_HEALTH_BAR_OFFSET - bar_height

        # Calcula cor da barra baseada na vida (verde para vida cheia, vermelho para vida baixa)
        color_r = int(ENEMY_HEALTH_BAR_COLOR_MIN[0] + (ENEMY_HEALTH_BAR_COLOR_MAX[0] - ENEMY_HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(ENEMY_HEALTH_BAR_COLOR_MIN[1] + (ENEMY_HEALTH_BAR_COLOR_MAX[1] - ENEMY_HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(ENEMY_HEALTH_BAR_COLOR_MIN[2] + (ENEMY_HEALTH_BAR_COLOR_MAX[2] - ENEMY_HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_color = (color_r, color_g, color_b)

        # Desenha a barra de fundo
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BACKGROUND_COLOR, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Desenha a barra de vida proporcional à vida atual
        if health_pct > 0:
            pygame.draw.rect(screen, current_color, 
                           (bar_x, bar_y, int(bar_width * health_pct), bar_height))
        
        # Desenha a borda da barra
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BORDER_COLOR, 
                        (bar_x, bar_y, bar_width, bar_height), 1)

    def update(self):
        # Atualiza IA e partículas
        if self.ai_controller:
            self.ai_controller.update()  # Atualiza comportamento da IA
        self.blood_system.update()  # Atualiza partículas de sangue

    def draw(self, screen):
        # Desenha o inimigo, barra de vida e partículas
        screen.blit(self.image, self.rect)  # Desenha o sprite
        self.draw_health_bar(screen)  # Desenha a barra de vida
        self.blood_system.draw(screen)  # Desenha partículas de sangue

class Raider(Enemy):
    def __init__(self, game, x, y):
        groups = game.all_sprites, game.enemies
        super().__init__(game, x, y, groups)
        
        # Configuração básica
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_RAIDER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        # Atributos do inimigo
        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED
        self.last_hit_time = 0
        self.invincible = False
        self.ai_controller = RaiderAIController(self)  # Controlador de IA específico
        self.blood_system = BloodParticleSystem()
        
    def take_damage(self, amount, knockback=0):
        # Recebe dano com possível knockback
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= amount
            # Cria partículas de sangue no ponto de impacto
            for _ in range(3):
                self.blood_system.add_particles(self.rect.centerx, self.rect.centery)
            self.last_hit_time = now
            self.invincible = True  # Ativa invencibilidade temporária
            if self.health <= 0:
                self.kill()  # Remove o inimigo se morrer
        
    def attack(self):
        # Ataca o jogador
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Player):
                if pygame.sprite.collide_rect(self, sprite):
                    sprite.take_damage(self.damage)  # Causa dano ao jogador
        
    def update(self):
        # Atualiza estado de invencibilidade
        now = pygame.time.get_ticks()
        if self.invincible and now - self.last_hit_time > ENEMY_INVINCIBILITY_DURATION:
            self.invincible = False  # Desativa invencibilidade após o tempo
            
        # Usa IA para decidir movimento
        dx, dy, should_attack = self.ai_controller.update(self.game.player)
            
        # Move-se ou ataca baseado na decisão da IA
        if should_attack:
            self.attack()  # Executa ataque
        else:
            self.move(dx, dy)  # Move-se na direção calculada
        
        # Atualiza sistema de partículas
        self.blood_system.update()

    def draw_blood(self, screen):
        # Desenha partículas de sangue
        self.blood_system.draw(screen)

class WildDog(Enemy):
    def __init__(self, game, x, y):
        groups = game.all_sprites, game.enemies
        super().__init__(game, x, y, groups)

        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_DOG_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.health = ENEMY_DOG_HEALTH
        self.max_health = ENEMY_DOG_HEALTH
        self.damage = ENEMY_DOG_DAMAGE
        self.speed = ENEMY_DOG_SPEED
        self.ai_controller = WildDogAIController(self)  # Controlador de IA específico
