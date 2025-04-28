import pygame
from .item import Item
from core.settings import *

class ReinforcedMask(Item):
    """Representa o item 'Máscara Reforçada'.

    Quando coletada, oferece proteção temporária contra radiação/toxinas.
    """
    def __init__(self, game, x, y):
        """Inicializa a máscara reforçada."""
        super().__init__(game, x, y, item_type='reinforced_mask')
        self.buff_duration = REINFORCED_MASK_DURATION # Duração do buff em segundos (a ser definido em settings)
        self.load_image() # Carrega a imagem específica

    def load_image(self):
        """Carrega a imagem da máscara."""
        try:
            # Tenta carregar a imagem específica da máscara
            self.image = self.game.asset_manager.get_image('mask_powerup') # Nome da imagem a ser definida
            self.image = pygame.transform.scale(self.image, (ITEM_SIZE, ITEM_SIZE)) # Ajusta o tamanho
            # Atualiza o rect com o tamanho da nova imagem
            self.rect = self.image.get_rect(center=self.rect.center)
            self.hitbox = self.rect.inflate(-4, -4) # Ajusta hitbox se necessário
        except Exception as e:
            print(f"Erro ao carregar imagem para ReinforcedMask: {e}. Usando fallback.")
            # Fallback para um quadrado simples se a imagem não for encontrada
            self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
            self.image.fill(CYAN) # Cor de fallback
            self.rect = self.image.get_rect(center=self.rect.center)
            self.hitbox = self.rect.inflate(-4, -4)

    def setup(self):
        """Configurações adicionais (já tratado em load_image)."""
        pass # load_image é chamado no __init__

    def collect(self):
        """Aplica o efeito da máscara ao jogador."""
        if not self.collected:
            collected_base = super().collect() # Chama a coleta base (som, marcação)
            if collected_base and hasattr(self.game, 'player'):
                # Aplica o buff ao jogador
                self.game.player.apply_mask_buff(self.buff_duration)
                print(f"Máscara Reforçada coletada! Buff ativo por {self.buff_duration}s")
                self.kill() # Remove o sprite do item do jogo após coleta
                return True
        return False

    def render(self, screen, camera):
        """Renderiza a imagem específica da máscara."""
        if self.collected:
            return

        # Calcula a posição com animações da classe base
        render_pos_rect = pygame.Rect(
            self.x - self.image.get_width() // 2,
            self.y - self.image.get_height() // 2 - self.bob_offset - self.bounce_height,
            self.image.get_width(),
            self.image.get_height()
        )
        screen_pos = camera.apply(render_pos_rect)

        # Desenha a imagem do item
        screen.blit(self.image, screen_pos)

        # --- DEBUG (opcional): Desenhar hitbox ---
        # if DEBUG_MODE:
        #     hitbox_screen_pos = camera.apply(self.hitbox)
        #     pygame.draw.rect(screen, RED, hitbox_screen_pos, 1)
        # --- Fim DEBUG --- 