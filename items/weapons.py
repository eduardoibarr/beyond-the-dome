import pygame
from core.settings import *
from projectiles.projectiles import Bullet, Casing

vec = pygame.math.Vector2

class Weapon:
    """Classe base para todas as armas no jogo.
    
    Esta classe define a interface comum e funcionalidades básicas
    que todas as armas devem implementar.
    """
    def __init__(self, game, owner):
        """Inicializa a arma base.
        
        Args:
            game (Game): Referência ao objeto principal do jogo
            owner (GameObject): Referência ao dono da arma (jogador ou inimigo)
        """
        self.game = game
        self.owner = owner
        self.last_use_time = 0

    def can_use(self):
        """Verifica se a arma pode ser usada.
        
        Returns:
            bool: True se pode ser usada, False caso contrário
        """
        return True
        
    def use(self, direction):
        """Usa a arma na direção especificada.
        
        Args:
            direction (vec): Vetor normalizado indicando a direção de uso
        """
        pass
        
    def update(self, dt):
        """Atualiza o estado da arma.
        
        Args:
            dt (float): Delta time em segundos
        """
        pass
        
    def draw(self, screen, camera):
        """Renderiza os efeitos visuais da arma.
        
        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição
        """
        pass

class Pistol(Weapon):
    """Sistema de arma de fogo do jogador.
    
    Esta classe gerencia:
    - Sistema de disparo e cadência
    - Recarregamento e gerenciamento de munição
    - Efeitos visuais de disparo
    - Integração com o sistema de projéteis
    
    Características:
    - Cadência de tiro configurável
    - Sistema de pente com munição limitada
    - Recarregamento automático
    - Efeito visual de clarão do disparo
    """
    def __init__(self, game, player):
        """Inicializa a pistola.
        
        Args:
            game (Game): Referência ao objeto principal do jogo
            player (Player): Referência ao sprite do jogador
        """
        super().__init__(game, player)
        self.player = player
        self.last_shot_time = 0        # Timestamp do último tiro
        self.reloading = False         # Estado de recarregamento
        self.reload_start_time = 0     # Início do recarregamento
        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE  # Munição no pente
        self.muzzle_flash_timer = 0    # Timer para o clarão do disparo
        self.last_fire_rate = BULLET_FIRE_RATE   # Cadência de tiro

    def can_shoot(self):
        """Verifica se a pistola pode atirar.
        
        Condições necessárias:
        1. Não estar recarregando
        2. Ter munição no pente
        3. Respeitar a cadência de tiro
        
        Returns:
            bool: True se pode atirar, False caso contrário
        """
        now = pygame.time.get_ticks()
        return (not self.reloading and
                self.ammo_in_mag > 0 and
                now - self.last_shot_time > PISTOL_FIRE_RATE)

    def start_reload(self):
        """Inicia o processo de recarregamento.
        
        Verifica:
        1. Se já está recarregando
        2. Se o pente está cheio
        3. Se o jogador tem munição na reserva
        
        Inicia a animação e o som de recarregamento.
        """
        if self.reloading or self.ammo_in_mag == PISTOL_MAGAZINE_SIZE:
            return
            
        if self.player.can_reload():
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            self.game.play_audio('reload_start', volume=0.7)

    def finish_reload(self):
        """Finaliza o processo de recarregamento.
        
        Este método:
        1. Calcula a munição necessária
        2. Transfere munição da reserva para o pente
        3. Atualiza o estado da arma
        4. Toca o som de recarregamento completo
        """
        needed_ammo = PISTOL_MAGAZINE_SIZE - self.ammo_in_mag
        transferred_ammo = self.player.take_ammo_from_reserve(needed_ammo)
        self.ammo_in_mag += transferred_ammo
        self.reloading = False
        self.game.play_audio('reload_end', volume=0.7)

    def shoot(self, direction):
        """Dispara um projétil na direção especificada.
        
        Este método:
        1. Verifica se pode atirar
        2. Cria o projétil
        3. Atualiza a munição
        4. Inicia recarregamento se necessário
        5. Toca efeitos sonoros
        
        Args:
            direction (vec): Vetor normalizado indicando a direção do tiro
        """
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

        # Calcula a posição de spawn do projétil
        offset_dist = self.player.rect.width / 2 + BULLET_WIDTH / 2
        spawn_pos = self.player.position + direction * offset_dist

        # Cria e dispara o projétil
        Bullet(self.game, spawn_pos, direction, BULLET_SPEED)
        self.game.play_audio('beretta-m9', volume=0.6)

        # Ejetar casquilo
        casing_spawn_offset = vec(15 if self.player.facing_right else -15, -5) # Deslocamento do casquilo
        casing_pos = self.player.position + casing_spawn_offset
        Casing(self.game, casing_pos, self.player.facing_right)

        # Inicia recarregamento automático se necessário
        if self.ammo_in_mag <= 0:
            self.start_reload()

    def update(self, dt):
        """Atualiza o estado da pistola.
        
        Gerencia:
        1. Timer de recarregamento
        2. Estado da arma
        3. Efeitos visuais
        
        Args:
            dt (float): Delta time em segundos
        """
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start_time > PISTOL_RELOAD_TIME:
                self.finish_reload()

    def draw(self, screen, camera):
        """Renderiza os efeitos visuais da arma.
        
        Implementa:
        1. Clarão do disparo
        2. Posicionamento correto na tela
        3. Efeitos de partículas
        
        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição
        """
        now = pygame.time.get_ticks()
        if self.muzzle_flash_timer > 0 and now - self.muzzle_flash_timer < PISTOL_MUZZLE_FLASH_DURATION:
            # Calcula a direção do clarão baseado na posição do mouse
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = camera.screen_to_world(mouse_pos)
            direction = vec(world_mouse_pos) - self.player.position
            if direction.length_squared() > 0:
                direction = direction.normalize()
                offset_dist = self.player.rect.width * 0.6
                flash_pos_world = self.player.position + direction * offset_dist
                flash_pos_screen = camera.apply_coords(*flash_pos_world)

                # Renderiza o clarão do disparo
                flash_radius = PISTOL_MUZZLE_FLASH_SIZE // 2
                pygame.draw.circle(screen, PISTOL_MUZZLE_FLASH_COLOR, flash_pos_screen, flash_radius)
        else:
            self.muzzle_flash_timer = 0