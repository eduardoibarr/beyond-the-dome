import pygame
import math
from core.settings import *
from projectiles.projectiles import Bullet



vec = pygame.math.Vector2

# Classe da Pistola
class Pistol:
    """Manages the player's pistol weapon."""
    def __init__(self, game, player):
        """ Inicializa a pistola.
        Args:
            game (Game): Referência ao objeto principal do jogo.
            player (Player): Referência ao sprite do jogador.
        """
        self.game = game
        self.player = player
        self.last_shot_time = 0        # Timestamp do último tiro disparado
        self.reloading = False
        self.reload_start_time = 0
        self.ammo_in_mag = PISTOL_MAGAZINE_SIZE # Começa com um pente cheio
        self.muzzle_flash_timer = 0 # Para desenhar o clarão do disparo

    def can_shoot(self):
        """Checks if the pistol can fire (fire rate, reloading, ammo)."""
        now = pygame.time.get_ticks()
        return (not self.reloading and
                self.ammo_in_mag > 0 and
                now - self.last_shot_time > PISTOL_FIRE_RATE)

    def start_reload(self):
        """Inicia a sequência de recarregamento se necessário e possível."""
        # Checa se já está recarregando ou se o pente está cheio
        if self.reloading or self.ammo_in_mag == PISTOL_MAGAZINE_SIZE:
            return
        # Checa se o jogador tem munição na reserva (implementar na classe Player)
        if self.player.can_reload():
            print("Recarregando...") # Debug/Som
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            # Toca o som de recarregando
            # self.game.sound_manager.play('pistol_reload_start')

    def finish_reload(self):
        """Completa a sequência de recarregamento."""
        needed_ammo = PISTOL_MAGAZINE_SIZE - self.ammo_in_mag
        transferred_ammo = self.player.take_ammo_from_reserve(needed_ammo)
        self.ammo_in_mag += transferred_ammo
        self.reloading = False
        print(f"Recarregamento finalizado. Munição: {self.ammo_in_mag}/{self.player.reserve_ammo}") # Debug
        # Toca o som de recarregamento completo
        # self.game.sound_manager.play('pistol_reload_end')

    def shoot(self, target_world_pos):
        """ Dispara uma bala na direção do alvo, se possível.

        Args:
            target_world_pos (vec): The target position in world coordinates.
        """
        if not self.can_shoot():
            # Optionally trigger reload if out of ammo
            if not self.reloading and self.ammo_in_mag <= 0:
                 self.start_reload()
            # Toca o som de sem munição?
            # self.game.sound_manager.play('pistol_empty')
            return

        now = pygame.time.get_ticks()
        self.last_shot_time = now
        self.ammo_in_mag -= 1
        self.muzzle_flash_timer = now # Inicia o timer do clarão do disparo

        # --- Calcula os parâmetros do tiro ---
        # Calcula o vetor de direção do centro do jogador até a posição do alvo no mundo
        start_pos_world = vec(self.player.position) # Usa a posição precisa do jogador no mundo
        direction = target_world_pos - start_pos_world
        if direction.length_squared() > 0: # Evita normalizar um vetor zero
             direction = direction.normalize()
        else:
             # Direção padrão (ex: baseado para onde o jogador está olhando) se o alvo for o mesmo que o jogador
             direction = vec(1, 0) if self.player.facing_right else vec(-1, 0)

        # Calcula a posição de spawn ligeiramente na frente do jogador
        # Usa o tamanho do rect do jogador para o cálculo do offset
        offset_dist = self.player.rect.width / 2 + BULLET_WIDTH / 2 # Spawn um pouco fora do raio do jogador
        spawn_pos = start_pos_world + direction * offset_dist

        # Aplica algum recuo/espalhamento (opcional)
        # angle_offset = random.uniform(-PISTOL_SPREAD_ANGLE, PISTOL_SPREAD_ANGLE)
        # direction = direction.rotate(angle_offset)

        # --- Cria o projétil da bala ---
        # print(f"Atirando bala! Dir: {direction}") # Debug
        Bullet(self.game, spawn_pos, direction, BULLET_SPEED) # Cria o projétil
        # Toca o som do tiro
        self.game.play_audio('pistol_fire') # Reproduz o som do tiro

        # Aplica recuo visual ao jogador (opcional, tratado em Player?)
        # self.player.apply_recoil(direction * -1 * PISTOL_RECOIL_AMOUNT)

        # Checa se precisa recarregar após esse tiro
        if self.ammo_in_mag <= 0:
             self.start_reload()


    def update(self, dt):
        """ Atualiza o estado da pistola, principalmente o timer de recarregamento.
        Args:
            dt (float): Delta time em segundos.
        """
        if self.reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start_time > PISTOL_RELOAD_TIME:
                self.finish_reload()

        # Mouse button handling is done in Player.get_keys
    def draw(self, screen, camera):
        """ Desenha os efeitos da arma, como o clarão do disparo.
        Args:
            screen (pygame.Surface): A superfície principal de exibição.
            camera (Camera): O objeto câmera do jogo.
        """
        now = pygame.time.get_ticks()
        if self.muzzle_flash_timer > 0 and now - self.muzzle_flash_timer < PISTOL_MUZZLE_FLASH_DURATION:
            # Calcula a posição do clarão (na ponta do cano)
            # Precisa da direção para onde o jogador está mirando
            direction = vec(1, 0) if self.player.facing_right else vec(-1, 0)
            offset_dist = self.player.rect.width * 0.6 # Ajustar se necessário
            flash_pos_world = self.player.position + direction * offset_dist
            flash_pos_screen = camera.apply_coords(*flash_pos_world)

            # Desenha o clarão
            flash_radius = PISTOL_MUZZLE_FLASH_SIZE // 2
            pygame.draw.circle(screen, PISTOL_MUZZLE_FLASH_COLOR, flash_pos_screen, flash_radius)
            # Ou usa um pequeno sprite/imagem
        else:
             self.muzzle_flash_timer = 0 # Garante que o timer esteja resetado

# --- Métodos específicos do estilingue foram removidos (get_charge_percent, is_shooting) ---

# --- Comentários dos métodos auxiliares da câmera foram removidos ---


