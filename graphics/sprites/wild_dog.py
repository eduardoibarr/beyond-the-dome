import pygame
from core.settings import *
from graphics.sprites.enemy_base import Enemy
from core.ai.ai import WildDogAIController

class WildDog(Enemy):
    """Implementação do inimigo Cão Selvagem, um inimigo rápido e ágil.
    
    O Cão Selvagem é um inimigo que persegue o jogador e ataca com mordidas.
    Possui menos vida que outros inimigos, mas compensa com maior velocidade
    e agilidade de movimento.
    """
    def __init__(self, game, x_pixel, y_pixel):
        """Inicializa um novo Cão Selvagem no jogo.
        
        Args:
            game: Referência ao objeto principal do jogo
            x_pixel (int): Posição X inicial em pixels
            y_pixel (int): Posição Y inicial em pixels
        """
        # Inicializa a classe base Enemy
        super().__init__(game, x_pixel, y_pixel, (game.all_sprites, game.enemies))

        # --- Atributos Específicos do Cão Selvagem ---
        self.health = ENEMY_DOG_HEALTH
        self.max_health = ENEMY_DOG_HEALTH
        self.damage = ENEMY_DOG_DAMAGE
        self.speed = ENEMY_DOG_SPEED * TILE_SIZE  # Converte velocidade de tiles/sec para pixels/sec

        # --- Configuração de Aparência e IA ---
        # Tenta carregar as animações específicas do Cão Selvagem
        if not self.setup_animations('wild_dog'):
            # Fallback visual com dimensões reduzidas para melhor representação
            dog_width = int(ENEMY_WIDTH * 0.8)   # 80% da largura padrão
            dog_height = int(ENEMY_HEIGHT * 0.8) # 80% da altura padrão
            self.image = pygame.Surface((dog_width, dog_height))
            self.image.fill(ENEMY_DOG_COLOR)
            self.rect = self.image.get_rect(center=self.position)

        # Inicializa o controlador de IA específico do Cão Selvagem
        self.ai_controller = WildDogAIController(self)

    def attack(self):
        """Executa o ataque de mordida do Cão Selvagem.
        
        Este método é chamado pelo controlador de IA quando o Cão Selvagem
        está próximo o suficiente do jogador para atacar.
        
        O ataque consiste em:
        1. Iniciar a animação de mordida/investida
        2. Reproduzir o som de mordida
        3. Verificar proximidade com o jogador
        4. Aplicar dano se estiver no alcance
        """
        # Evita reativar o ataque durante a animação atual
        if self.current_animation == ANIM_ENEMY_SLASH:
            return

        # Inicia a animação de mordida/investida
        self.set_animation(ANIM_ENEMY_SLASH)
        
        # Reproduz o efeito sonoro da mordida
        if hasattr(self.game, 'asset_manager'):
            self.game.asset_manager.play_sound('wild_dog_bite')
        # --- Verificação de Alcance do Ataque ---
        # Cães têm um alcance de ataque menor que outros inimigos
        attack_range = ENEMY_ATTACK_RADIUS * 0.7
        
        # Verifica se o jogador está dentro do alcance de mordida
        if self.position.distance_squared_to(self.game.player.position) < attack_range**2:
            self.game.player.take_damage(self.damage)

