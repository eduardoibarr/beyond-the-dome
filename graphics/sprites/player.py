import pygame
from core.settings import *
from items.weapons import Pistol
from graphics.particles import BloodParticleSystem

vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    """Representa o personagem controlável pelo jogador.
    
    Gerencia:
    - Movimentação e física
    - Animações e aparência visual
    - Sistema de vida e dano
    - Interação com armas e itens
    - Entrada do jogador (teclado e mouse)
    - Efeitos visuais (partículas, flash de invencibilidade)
    """
    def __init__(self, game, x_pixel, y_pixel):
        """Inicializa o jogador.
        
        Args:
            game (Game): Referência ao objeto principal do jogo
            x_pixel (int): Coordenada X inicial em pixels
            y_pixel (int): Coordenada Y inicial em pixels
        """
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.game = game
        self._layer = PLAYER_RENDER_LAYER

        # --- Configuração das Animações ---
        self.animations = {}
        self.current_animation = None
        self._setup_animations() # Chama método auxiliar

        # Imagem de fallback se as animações falharem
        if not self.current_animation:
            print("Animações do jogador desativadas. Usando fallback.")
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(PLAYER_COLOR)
            self.current_animation = None # Garante que não tente atualizar animações

        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.facing_right = True

        # --- Posição e Movimento ---
        self.position = vec(x_pixel, y_pixel)
        self.velocity = vec(0, 0)
        self.acceleration = vec(0, 0)
        self.rect.center = self.position

        # --- Atributos do Jogador ---
        self.max_speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.radiation = 0
        self.last_hit_time = 0
        self.invincible = False
        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE
        self.reserve_ammo = BULLET_INITIAL_AMMO - PISTOL_MAGAZINE_SIZE
        self.pistol = Pistol(game, self)
        self.blood_system = BloodParticleSystem()
        self.has_filter_module = False
        self.is_in_radioactive_zone = False

        # --- Temporizadores ---
        self.step_timer = 0
        self.step_interval = 0.35
        self.last_melee_attack_time = 0 # Tempo do último ataque corpo a corpo
        self.melee_cooldown = PLAYER_MELEE_COOLDOWN # Obtido de settings.py

        pygame.mouse.set_visible(CURSOR_VISIBLE)

    def _setup_animations(self):
        """Configura as animações do jogador usando o AssetManager."""
        # Verifica se o asset manager está disponível
        if not hasattr(self.game, 'asset_manager'):
            print("Erro: Asset manager não encontrado.")
            return
            
        try:
            # Tenta obter animações do AssetManager
            idle_frames = self.game.asset_manager.get_animation('player_idle')
            run_frames = self.game.asset_manager.get_animation('player_run')
            walk_frames = self.game.asset_manager.get_animation('player_walk')
            hurt_frames = self.game.asset_manager.get_animation('player_hurt')
            shoot_frames = self.game.asset_manager.get_animation('player_shoot')
            attack_frames = self.game.asset_manager.get_animation('player_attack')
            
            # Usa a animação run como walk se walk não estiver disponível
            if not walk_frames and run_frames:
                walk_frames = run_frames
                
            # Verifica se pelo menos a animação idle foi carregada
            if not idle_frames:
                raise ValueError("Animação 'player_idle' não encontrada no AssetManager.")
                
            # Define as animações no dicionário
            self.animations = {
                ANIM_PLAYER_IDLE: idle_frames,
                ANIM_PLAYER_RUN: run_frames if run_frames else idle_frames,
                ANIM_PLAYER_WALK: walk_frames if walk_frames else idle_frames,
                ANIM_PLAYER_HURT: hurt_frames if hurt_frames else idle_frames,
                ANIM_PLAYER_SHOOT: shoot_frames if shoot_frames else idle_frames,
                ANIM_PLAYER_ATTACK: attack_frames if attack_frames else idle_frames
            }
            
            # Define a animação inicial
            self.current_animation = ANIM_PLAYER_IDLE
            self.animation_frame = 0
            self.animation_frame_duration = 0.1 # Duração padrão do quadro
            self.animation_timer = 0
            self.image = self.animations[self.current_animation][0]
            print("Animações do jogador configuradas com sucesso.")
            
        except Exception as e:
            print(f"Erro ao configurar animações do jogador: {e}. Animações desativadas.")
            self.animations = {}
            self.current_animation = None
            # Define a imagem de fallback (garantida pelo código no __init__)
    
    def take_damage(self, amount):
        """Aplica dano ao jogador, ativando a invencibilidade temporária.
        
        Args:
            amount (int): Quantidade de dano a ser aplicada
        """
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.health -= amount
            self.health = max(0, self.health)
            self.blood_system.add_particles(self.rect.centerx, self.rect.centery, count=5)
            self.last_hit_time = now
            self.invincible = True
            self.set_animation(ANIM_PLAYER_HURT)
            
            # Reproduz som de dano
            if hasattr(self.game, 'asset_manager'):
                self.game.asset_manager.play_sound('player_hurt')

            if self.health <= 0:
                print("Jogador morreu!")

    def set_animation(self, animation_name):
        """Define a animação atual do jogador.
        
        Impede a interrupção de animações importantes (como dano).
        
        Args:
            animation_name (str): Nome da animação a ser definida (e.g., ANIM_PLAYER_RUN)
        """
        if not self.current_animation or self.current_animation == animation_name:
            return

        if animation_name in self.animations:
            # Impede a troca de animação durante a animação de dano
            if self.current_animation == ANIM_PLAYER_HURT and self.animation_frame < len(self.animations[ANIM_PLAYER_HURT]) - 1:
                 return

            self.current_animation = animation_name
            self.animation_frame = 0
            self.animation_timer = 0
        else:
            # Define animação padrão (ocioso) se a animação solicitada não existir
            if ANIM_PLAYER_IDLE in self.animations:
                 self.current_animation = ANIM_PLAYER_IDLE
            else:
                 self.current_animation = None

    def update_animation(self, dt):
        """Atualiza o quadro da animação atual.
        
        Ajusta a velocidade da animação de corrida com base na velocidade do jogador.
        Gerencia a transição de animações não contínuas (dano, ataque).
        Aplica o efeito visual de invencibilidade.
        
        Args:
            dt (float): Delta time em segundos
        """
        if not self.current_animation: return

        frames = self.animations[self.current_animation]
        num_frames = len(frames)
        if num_frames == 0: return

        # Ajusta a duração do quadro (velocidade da animação)
        current_frame_duration = self.animation_frame_duration
        if self.current_animation == ANIM_PLAYER_RUN:
            speed_mag = self.velocity.length()
            if speed_mag > 1.0 and self.max_speed > 0:
                 speed_factor = max(0.5, min(1.5, speed_mag / self.max_speed))
                 current_frame_duration = self.animation_frame_duration / speed_factor
        elif self.current_animation == ANIM_PLAYER_HURT:
             current_frame_duration = 0.08 # Animação de dano mais rápida

        # Avança o quadro da animação
        self.animation_timer += dt
        while self.animation_timer >= current_frame_duration:
            self.animation_timer -= current_frame_duration
            self.animation_frame = (self.animation_frame + 1) % num_frames

            # Retorna para animação ociosa após animações não contínuas
            if self.animation_frame == 0:
                 if self.current_animation in [ANIM_PLAYER_HURT, ANIM_PLAYER_ATTACK, ANIM_PLAYER_SHOOT]:
                      self.set_animation(ANIM_PLAYER_IDLE)

        # Atualiza a imagem do sprite
        self.original_image = frames[self.animation_frame]
        self.image = self.original_image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # Aplica efeito visual de invencibilidade (piscar)
        if self.invincible:
            now = pygame.time.get_ticks()
            alpha = 100 if (now - self.last_hit_time) % 200 < 100 else 255
            try:
                temp_image = self.image.copy()
                temp_image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = temp_image
            except pygame.error:
                 temp_image = self.image.copy()
                 temp_image.set_alpha(alpha)
                 self.image = temp_image


    def get_keys(self):
        """Processa a entrada do teclado e mouse para ações do jogador."""
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Movimento (define a aceleração)
        self.acceleration = vec(0, 0)
        if keys[pygame.K_a]: self.acceleration.x = -self.max_speed * 8
        if keys[pygame.K_d]: self.acceleration.x = self.max_speed * 8
        if keys[pygame.K_w]: self.acceleration.y = -self.max_speed * 8
        if keys[pygame.K_s]: self.acceleration.y = self.max_speed * 8

        # Ações
        if keys[pygame.K_r]: self.pistol.start_reload() # Recarregar
        if keys[pygame.K_SPACE]: self.attack() # Ataque corpo a corpo

        # Mira e Disparo
        if self.game.camera:
            # Define a direção que o jogador está olhando baseado no mouse
            screen_center = vec(self.game.screen.get_width() // 2, self.game.screen.get_height() // 2)
            mouse_offset = vec(mouse_pos) - screen_center
            self.facing_right = mouse_offset.x > 0

            # Dispara com o botão esquerdo do mouse
            if mouse_buttons[0]:
                world_mouse_pos = self.game.camera.screen_to_world(mouse_pos)
                direction = vec(world_mouse_pos) - self.position
                if direction.length() > 0:
                    direction = direction.normalize()
                    self.pistol.shoot(direction)

        # Define a animação baseada no estado
        if self.current_animation != ANIM_PLAYER_HURT:
            if self.acceleration.length_squared() > 0:
                # Define animação de corrida ou caminhada baseado na velocidade
                if self.velocity.length_squared() > (self.max_speed * 0.5)**2:
                    self.set_animation(ANIM_PLAYER_RUN)
                else:
                    self.set_animation(ANIM_PLAYER_WALK)
            else:
                # Define animação de disparo ou ocioso
                is_shooting = (pygame.time.get_ticks() - self.pistol.last_shot_time < 100)
                if self.pistol.reloading or is_shooting:
                    self.set_animation(ANIM_PLAYER_SHOOT)
                elif self.current_animation != ANIM_PLAYER_ATTACK:
                     self.set_animation(ANIM_PLAYER_IDLE)


    def move(self, dt):
        """Aplica movimento, física e colisões ao jogador.
        
        Implementa:
        - Movimento baseado em aceleração e velocidade
        - Fricção/Amortecimento simples
        - Limite de velocidade
        - Detecção e resolução de colisões com obstáculos
        
        Args:
            dt (float): Delta time em segundos
        """
        # Aplica aceleração e amortecimento
        self.velocity += self.acceleration * dt * 10
        self.velocity *= (1 - PLAYER_FRICTION)

        # Limita a velocidade máxima
        if self.velocity.length_squared() > self.max_speed * self.max_speed:
            if self.velocity.length_squared() > 0:
                 self.velocity.scale_to_length(self.max_speed)

        # Para o jogador se a velocidade for muito baixa e não houver aceleração
        if self.velocity.length_squared() < (0.5 * TILE_SIZE)**2 and self.acceleration.length_squared() == 0:
            self.velocity = vec(0, 0)

        # Calcula a nova posição
        displacement = self.velocity * dt
        new_position = self.position + displacement

        # Resolve colisões
        self.position = self.collide_with_obstacles(new_position)
        self.rect.center = self.position


    def collide_with_obstacles(self, new_position):
        """Verifica e resolve colisões com obstáculos.
        
        Move o jogador de volta para a posição anterior à colisão
        separadamente nos eixos X e Y.
        
        Args:
            new_position (vec): A posição potencial do jogador após o movimento
            
        Returns:
            vec: A posição final ajustada após a resolução de colisões
        """
        potential_rect = self.rect.copy()
        final_pos = new_position.copy()

        # Verifica colisão no eixo X
        potential_rect.centerx = new_position.x
        potential_rect.centery = self.position.y
        for obstacle in self.game.obstacles:
            if potential_rect.colliderect(obstacle.rect):
                if self.velocity.x > 0: final_pos.x = obstacle.rect.left - self.rect.width / 2
                elif self.velocity.x < 0: final_pos.x = obstacle.rect.right + self.rect.width / 2
                self.velocity.x = 0
                potential_rect.centerx = final_pos.x
                break

        # Verifica colisão no eixo Y
        potential_rect.centery = new_position.y
        for obstacle in self.game.obstacles:
            if potential_rect.colliderect(obstacle.rect):
                if self.velocity.y > 0: final_pos.y = obstacle.rect.top - self.rect.height / 2
                elif self.velocity.y < 0: final_pos.y = obstacle.rect.bottom + self.rect.height / 2
                self.velocity.y = 0
                break

        return final_pos


    def attack(self):
        """Executa um ataque corpo a corpo, respeitando o cooldown."""
        # TODO: Implementar cooldown do ataque corpo a corpo - Feito
        now = pygame.time.get_ticks()
        if now - self.last_melee_attack_time < self.melee_cooldown:
             return # Impede o ataque se estiver em cooldown
             
        # Impede o ataque se já estiver atacando ou tomando dano
        if self.current_animation in [ANIM_PLAYER_ATTACK, ANIM_PLAYER_HURT]: return

        self.last_melee_attack_time = now # Registra o tempo do ataque
        self.set_animation(ANIM_PLAYER_ATTACK)
        # self.game.play_audio('player_attack') # Tocar som de ataque

        # Cria uma hitbox simples na frente do jogador
        hitbox_offset = 30
        hitbox_width = 40
        hitbox_height = self.rect.height * 0.8
        hitbox_center_x = self.rect.centerx + (hitbox_offset if self.facing_right else -hitbox_offset)
        hitbox_center_y = self.rect.centery
        attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

        # Verifica acertos em inimigos
        for enemy in self.game.enemies:
            if attack_hitbox.colliderect(enemy.rect):
                 if hasattr(enemy, 'take_damage'):
                      enemy.take_damage(MELEE_WEAPON_DAMAGE)


    def update(self, dt):
        """Loop de atualização principal do jogador.
        
        Coordena todas as atualizações:
        - Entrada
        - Movimento e colisão
        - Radiação
        - Arma
        - Partículas
        - Estado de invencibilidade
        - Animação
        
        Args:
            dt (float): Delta time em segundos
        """
        self.get_keys()
        self.move(dt)
        self.update_radiation(dt)
        self.pistol.update(dt)
        self.blood_system.update(dt)

        # Atualiza estado de invencibilidade
        if self.invincible and pygame.time.get_ticks() - self.last_hit_time > PLAYER_INVINCIBILITY_DURATION:
            self.invincible = False
            if self.current_animation == ANIM_PLAYER_HURT and self.animation_frame == 0:
                 self.set_animation(ANIM_PLAYER_IDLE)

        # Atualiza animação
        self.update_animation(dt)


    def draw_weapon(self, screen, camera):
        """Desenha a arma e a mira na tela."""
        if not camera: return

        # Desenha a mira (cursor)
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

        # Desenha efeitos da arma (clarão) e partículas de sangue
        self.pistol.draw(screen, camera)
        self.blood_system.draw(screen, camera)

    def has_reserve_ammo(self):
        """Verifica se o jogador tem munição na reserva."""
        return self.reserve_ammo > 0

    def can_reload(self):
        """Verifica se o jogador pode e precisa recarregar."""
        return (self.pistol.ammo_in_mag < PISTOL_MAGAZINE_SIZE and
                self.has_reserve_ammo())

    def take_ammo_from_reserve(self, amount_needed):
        """Retira munição da reserva para o pente.
        
        Args:
            amount_needed (int): Quantidade de munição necessária
            
        Returns:
            int: Quantidade de munição efetivamente transferida
        """
        can_take = min(amount_needed, self.reserve_ammo)
        self.reserve_ammo -= can_take
        return can_take

    def update_radiation(self, dt):
        """Atualiza o nível de radiação do jogador e aplica dano se necessário."""
        rad_change = 0
        if self.is_in_radioactive_zone:
            increase_rate = RADIATION_INCREASE_RATE * 3
            if self.has_filter_module: increase_rate *= 0.1 # Filtro reduz a absorção
            rad_change = increase_rate * dt
        elif self.has_filter_module:
            rad_change = -RADIATION_INCREASE_RATE * 0.5 * dt # Filtro limpa radiação
        else:
            rad_change = -RADIATION_INCREASE_RATE * 0.1 * dt # Decaimento natural lento

        self.radiation = max(0, min(RADIATION_MAX, self.radiation + rad_change))

        # Aplica dano por radiação
        if self.radiation > RADIATION_DAMAGE_THRESHOLD and not self.has_filter_module:
            over_threshold = self.radiation - RADIATION_DAMAGE_THRESHOLD
            max_over = RADIATION_MAX - RADIATION_DAMAGE_THRESHOLD
            damage_factor = over_threshold / max_over if max_over > 0 else 1
            damage_amount = RADIATION_DAMAGE_RATE * (1 + damage_factor) * dt

            self.health -= damage_amount
            self.health = max(0, self.health)
            if self.health <= 0 and not self.game.cause_of_death:
                self.game.cause_of_death = "radiação"
                self.game.playing = False


    def collect_filter_module(self):
        """Ativa o efeito do módulo de filtro coletado."""
        print("Jogador coletou o módulo de filtro!")
        self.has_filter_module = True 