import pygame
import random
from core.settings import *
from graphics.particles import BloodParticleSystem

vec = pygame.math.Vector2

class Enemy(pygame.sprite.Sprite):
    """Classe base abstrata para todos os inimigos do jogo.
    
    Define a estrutura e funcionalidades comuns a todos os inimigos:
    - Atributos básicos (vida, dano, velocidade)
    - Sistema de posicionamento e movimento
    - Gerenciamento de animações
    - Sistema de dano e morte
    - Desenho da barra de vida
    - Efeitos de partículas (sangue)
    - Integração com sistema de IA
    
    Subclasses devem:
    - Definir atributos específicos (vida, dano, etc.)
    - Carregar animações apropriadas (via `setup_animations`)
    - Atribuir um controlador de IA (`ai_controller`)
    - Implementar a lógica de ataque específica
    """
    def __init__(self, game, x_pixel, y_pixel, groups):
        """Inicializa um inimigo genérico.
        
        Args:
            game (Game): Referência ao objeto principal do jogo
            x_pixel (int): Coordenada X inicial em pixels
            y_pixel (int): Coordenada Y inicial em pixels
            groups (tuple): Grupos de sprites aos quais este inimigo pertence
        """
        self._layer = 2 # Camada de renderização padrão para inimigos
        self.groups = groups
        super().__init__(self.groups)
        self.game = game

        # --- Atributos Padrão (Subclasses devem sobrescrever) ---
        self.health = 10
        self.max_health = 10
        self.damage = 5
        self.speed = 50 # Pixels por segundo
        self.invincibility_duration = ENEMY_INVINCIBILITY_DURATION

        # --- Posição e Movimento ---
        self.position = vec(x_pixel, y_pixel)
        self.velocity = vec(0, 0)
        self.rect = None # Definido após carregar a imagem em setup_animations

        # --- IA e Estado ---
        self.ai_controller = None # Subclasse DEVE definir isso
        self.last_hit_time = 0
        self.invincible = False # Inimigos geralmente não são invencíveis

        # --- Efeitos Visuais ---
        self.blood_system = BloodParticleSystem()

        # --- Animação ---
        self.animations = {}
        self.current_animation = None
        self.animation_frame = 0
        self.animation_frame_duration = 0.15 # Duração base por quadro
        self.animation_timer = 0
        self.facing_right = random.choice([True, False]) # Direção inicial aleatória
        self.original_image = None
        self.image = None

    def setup_animations(self, enemy_type):
        """Carrega as animações do inimigo usando o AssetManager.
        
        Args:
            enemy_type (str): Tipo de inimigo para identificar as animações corretas.
        
        Returns:
            bool: True se as animações foram carregadas com sucesso, False caso contrário.
        """
        # Verifica se o game tem um asset_manager
        if not hasattr(self.game, 'asset_manager'):
            print(f"Erro: Asset manager não encontrado para {type(self).__name__}.")
            return False
            
        try:
            # Gera os nomes das animações baseados no tipo de inimigo
            anim_idle = f"{enemy_type}_idle"
            anim_walk = f"{enemy_type}_walk"
            anim_hurt = f"{enemy_type}_hurt"
            anim_attack = f"{enemy_type}_attack"
            
            # Tenta obter as animações do AssetManager
            idle_frames = self.game.asset_manager.get_animation(anim_idle)
            walk_frames = self.game.asset_manager.get_animation(anim_walk)
            hurt_frames = self.game.asset_manager.get_animation(anim_hurt)
            attack_frames = self.game.asset_manager.get_animation(anim_attack)
            
            # Se animações específicas não existirem, tenta carregar animações genéricas
            if not idle_frames:
                idle_frames = self.game.asset_manager.get_animation('enemy_idle')
            if not walk_frames:
                walk_frames = self.game.asset_manager.get_animation('enemy_walk')
            if not hurt_frames:
                hurt_frames = self.game.asset_manager.get_animation('enemy_hurt')
            if not attack_frames:
                attack_frames = self.game.asset_manager.get_animation('enemy_attack')
                
            # Verifica se pelo menos a animação idle foi carregada
            if not idle_frames:
                raise ValueError(f"Nenhum frame encontrado para a animação 'idle' do inimigo {enemy_type}.")
                
            # Define as animações no dicionário
            self.animations = {
                ANIM_ENEMY_IDLE: idle_frames,
                ANIM_ENEMY_WALK: walk_frames if walk_frames else idle_frames,
                ANIM_ENEMY_HURT: hurt_frames if hurt_frames else idle_frames,
                ANIM_ENEMY_SLASH: attack_frames if attack_frames else idle_frames
            }
            
            # Define a animação e imagem inicial
            self.current_animation = ANIM_ENEMY_IDLE
            self.image = self.animations[ANIM_ENEMY_IDLE][0]
            self.original_image = self.image
            self.rect = self.image.get_rect(center=self.position)
            print(f"Animações carregadas para {type(self).__name__}")
            return True
            
        except Exception as e:
            print(f"Erro ao configurar animações para {type(self).__name__}: {e}")
            self.animations = {}
            self.current_animation = None
            # Define uma imagem de fallback caso as animações falhem
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(RED)
            self.rect = self.image.get_rect(center=self.position)
            return False

    def set_animation(self, animation_name):
        """Define a animação atual do inimigo de forma segura.
        
        Args:
            animation_name (str): Nome da animação (e.g., ANIM_ENEMY_WALK)
        """
        if not self.animations or self.current_animation == animation_name:
            return
        if animation_name in self.animations:
             # Impede interrupção da animação de dano
             if self.current_animation == ANIM_ENEMY_HURT and self.animation_frame < len(self.animations[ANIM_ENEMY_HURT]) - 1:
                  return
             self.current_animation = animation_name
             self.animation_frame = 0
             self.animation_timer = 0
        else:
             # Fallback para animação ociosa se a solicitada não existir
             if ANIM_ENEMY_IDLE in self.animations: self.current_animation = ANIM_ENEMY_IDLE


    def update_animation(self, dt):
        """Atualiza o quadro da animação atual.
        
        Ajusta a velocidade da animação de caminhada e retorna para ocioso
        após animações não contínuas.
        
        Args:
            dt (float): Delta time em segundos
        """
        if not self.current_animation or not self.animations: return

        frames = self.animations[self.current_animation]
        num_frames = len(frames)
        if num_frames == 0: return

        # Ajusta a velocidade da animação de caminhada
        current_frame_duration = self.animation_frame_duration
        if self.current_animation == ANIM_ENEMY_WALK:
            speed_mag = self.velocity.length()
            if speed_mag > 1.0 and self.speed > 0:
                 speed_factor = max(0.5, min(1.5, speed_mag / self.speed))
                 current_frame_duration = self.animation_frame_duration / speed_factor

        # Atualiza o quadro
        self.animation_timer += dt
        while self.animation_timer >= current_frame_duration:
            self.animation_timer -= current_frame_duration
            self.animation_frame = (self.animation_frame + 1) % num_frames
            if self.animation_frame == 0:
                 if self.current_animation in [ANIM_ENEMY_HURT, ANIM_ENEMY_SLASH]:
                      self.set_animation(ANIM_ENEMY_IDLE)

        # Atualiza a imagem e a orientação (flip)
        self.original_image = frames[self.animation_frame]
        self.image = self.original_image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)


    def move_towards(self, target_pos, dt):
        """Move o inimigo em direção a uma posição alvo.
        
        Usado pela IA para direcionar o movimento.
        Inclui resolução básica de colisões.
        
        Args:
            target_pos (vec): Posição alvo no mundo
            dt (float): Delta time em segundos
        """
        direction = target_pos - self.position
        dist = direction.length()

        if dist > 1.0: # Evita divisão por zero e movimento mínimo
            self.velocity = direction.normalize() * self.speed
            # Atualiza a direção visual do inimigo
            if self.velocity.x > 0.1: self.facing_right = True
            elif self.velocity.x < -0.1: self.facing_right = False
            self.set_animation(ANIM_ENEMY_WALK)
        else:
            self.velocity = vec(0, 0)
            self.set_animation(ANIM_ENEMY_IDLE)

        # Calcula nova posição e resolve colisões
        new_position = self.position + self.velocity * dt
        self.position = self.collide_with_obstacles(new_position)
        if self.rect: self.rect.center = self.position

    def collide_with_obstacles(self, new_position):
         """Resolução simples de colisão com obstáculos.
         
         Impede o inimigo de atravessar obstáculos.
         Pode ser melhorado para deslizar ao longo das paredes.
         
         Args:
            new_position (vec): Posição potencial do inimigo
            
         Returns:
            vec: Posição final ajustada
         """
         potential_rect = self.rect.copy()
         potential_rect.center = new_position
         for obstacle in self.game.obstacles:
              if potential_rect.colliderect(obstacle.rect):
                   self.velocity = vec(0, 0) # Para completamente ao colidir
                   return self.position
         return new_position


    def take_damage(self, amount):
        """Aplica dano ao inimigo.
        
        Ativa a animação de dano, gera partículas de sangue e
        notifica o controlador de IA.
        Remove o inimigo se a vida chegar a zero.
        
        Args:
            amount (int): Quantidade de dano a aplicar
        """
        self.health -= amount
        self.health = max(0, self.health)
        self.blood_system.add_particles(self.rect.centerx, self.rect.centery, count=3)
        self.set_animation(ANIM_ENEMY_HURT)

        if self.ai_controller:
            # Informa a IA sobre o dano e a possível origem (posição do jogador)
            self.ai_controller.alert_damage(self.game.player.position)

        if self.health <= 0:
            self.kill() # Remove o sprite de todos os grupos


    def draw_health_bar(self, screen, camera):
        """Desenha a barra de vida acima do inimigo."""
        if self.health <= 0 or self.max_health <= 0 or not self.rect: return

        health_pct = max(0.0, min(1.0, self.health / self.max_health))
        bar_width = ENEMY_HEALTH_BAR_WIDTH
        bar_height = ENEMY_HEALTH_BAR_HEIGHT

        # Calcula a posição da barra na tela
        screen_rect = camera.apply(self)
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - ENEMY_HEALTH_BAR_OFFSET - bar_height

        # Interpola a cor da barra de vida
        color_r = int(ENEMY_HEALTH_BAR_COLOR_MIN[0] + (ENEMY_HEALTH_BAR_COLOR_MAX[0] - ENEMY_HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(ENEMY_HEALTH_BAR_COLOR_MIN[1] + (ENEMY_HEALTH_BAR_COLOR_MAX[1] - ENEMY_HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(ENEMY_HEALTH_BAR_COLOR_MIN[2] + (ENEMY_HEALTH_BAR_COLOR_MAX[2] - ENEMY_HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_color = (max(0,min(255,color_r)), max(0,min(255,color_g)), max(0,min(255,color_b)))

        # Desenha a barra de vida
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        fill_rect = pygame.Rect(bar_x, bar_y, int(bar_width * health_pct), bar_height)
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BACKGROUND_COLOR, bg_rect)
        if health_pct > 0:
            pygame.draw.rect(screen, current_color, fill_rect)
        pygame.draw.rect(screen, ENEMY_HEALTH_BAR_BORDER_COLOR, bg_rect, 1)


    def update(self, dt):
        """Loop de atualização principal do inimigo.
        
        Delega decisões de comportamento para o controlador de IA.
        Atualiza posição, animação e efeitos.
        
        Args:
            dt (float): Delta time em segundos
        """
        # Controlador de IA decide o movimento e ações
        if self.ai_controller:
            self.ai_controller.update(dt)

        # Atualiza a posição baseada na velocidade definida pela IA
        new_position = self.position + self.velocity * dt
        self.position = self.collide_with_obstacles(new_position)
        if self.rect: self.rect.center = self.position

        # Atualiza animação e partículas
        self.update_animation(dt)
        self.blood_system.update(dt)


    def draw(self, screen, camera):
        """Renderiza o inimigo, barra de vida e partículas.
        
        Implementa culling para otimização.
        
        Args:
            screen (pygame.Surface): Superfície para desenhar
            camera (Camera): Sistema de câmera do jogo
        """
        if not self.rect: return

        screen_rect = camera.apply(self)

        # Só desenha se estiver visível na tela (culling)
        if screen_rect.colliderect(screen.get_rect()):
            if self.image:
                screen.blit(self.image, screen_rect)
            else:
                # Desenho fallback se a imagem não carregar
                fallback_rect = pygame.Rect(screen_rect.left, screen_rect.top, ENEMY_WIDTH, ENEMY_HEIGHT)
                pygame.draw.rect(screen, RED, fallback_rect)

            self.draw_health_bar(screen, camera)

        # Desenha partículas independentemente (elas cuidam do próprio culling)
        self.blood_system.draw(screen, camera) 