import pygame
from core.settings import *
from graphics.sprites.enemy_base import Enemy
from core.ai.ai import RaiderAIController

class Raider(Enemy):
    """Implementação do inimigo Saqueador, um tipo de inimigo agressivo e resistente.
    
    O Saqueador é um inimigo que persegue o jogador e ataca corpo a corpo.
    Possui mais vida e dano que outros inimigos básicos, mas é mais lento.
    """
    def __init__(self, game, x_pixel, y_pixel):
        """Inicializa um novo Saqueador no jogo.
        
        Args:
            game: Referência ao objeto principal do jogo
            x_pixel (int): Posição X inicial em pixels
            y_pixel (int): Posição Y inicial em pixels
        """
        # Inicializa a classe base Enemy
        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        # --- Atributos Específicos do Saqueador ---
        self.health = ENEMY_RAIDER_HEALTH
        self.max_health = ENEMY_RAIDER_HEALTH
        self.damage = ENEMY_RAIDER_DAMAGE
        self.speed = ENEMY_RAIDER_SPEED * TILE_SIZE  # Converte velocidade de tiles/sec para pixels/sec

        # --- Configuração de Aparência e IA ---
        # Tenta carregar as animações específicas do Saqueador
        if not self.setup_animations('raider'):
            # Fallback visual caso as animações falhem
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(ENEMY_RAIDER_COLOR)
            self.rect = self.image.get_rect(center=self.position)

        # Inicializa o controlador de IA específico do Saqueador
        self.ai_controller = RaiderAIController(self)

    def attack(self):
        """Executa o ataque corpo a corpo do Saqueador.
        
        Este método é chamado pelo controlador de IA quando o Saqueador
        está próximo o suficiente do jogador para atacar.
        
        O ataque consiste em:
        1. Iniciar a animação de ataque
        2. Reproduzir o som de ataque
        3. Verificar colisão com o jogador
        4. Aplicar dano se houver contato
        """
        # Evita reativar o ataque durante a animação atual
        if self.current_animation == ANIM_ENEMY_SLASH:
            return

        # Inicia a animação de ataque
        self.set_animation(ANIM_ENEMY_SLASH)
        
        # Reproduz o efeito sonoro do ataque
        if hasattr(self.game, 'asset_manager'):
            self.game.asset_manager.play_sound('raider_attack')

        # --- Configuração da Hitbox do Ataque ---
        # Define os parâmetros da área de ataque
        hitbox_offset = TILE_SIZE * 0.6  # Distância do centro do sprite
        hitbox_width = TILE_SIZE * 0.8   # Largura da área de ataque
        hitbox_height = self.rect.height * 0.9  # Altura da área de ataque
        
        # Ajusta a posição da hitbox baseado na direção do sprite
        if self.facing_right:
            hitbox_center_x = self.rect.centerx + hitbox_offset
        else:
            hitbox_center_x = self.rect.centerx - hitbox_offset
        hitbox_center_y = self.rect.centery
        
        # Cria e posiciona a hitbox do ataque
        attack_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        attack_hitbox.center = (hitbox_center_x, hitbox_center_y)

        # Verifica colisão com o jogador e aplica dano
        if attack_hitbox.colliderect(self.game.player.rect):
            self.game.player.take_damage(self.damage)
