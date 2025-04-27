import pygame
import math
import random
# Imports
# from settings import * # Replaced with explicit imports
from settings import (
    TILE_SIZE, ITEM_COLLECT_RADIUS, BLACK, WHITE, GREY, CYAN, LIGHTBLUE,
    DETAIL_LEVEL
    # Add other necessary constants from settings if used
)
from items.item import Item

# Modulo de filtro, principal item do jogo
class FilterModule(Item):
    """Um item de módulo de filtro que os jogadores coletam para reparar o sistema de filtragem de ar de sua cúpula.
    Este é um colecionável chave no objetivo principal do jogo."""
    def __init__(self, game, x, y, groups=None):
        """Inicializa um item de módulo de filtro.

        Args:
            game: Referência ao objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        super().__init__(game, x, y, item_type='filter_module', groups=groups)
        
        # Propriedades especiais
        self.bob_height = 8  # Efeito de flutuação aprimorado para itens importantes
        self.bob_speed = 1.5
        self.pulse_rate = 0.8  # Controla a velocidade com que o item pulsa
        self.glow_intensity = 0.8  # Quão brilhante é o efeito de brilho
        
        # Propriedades de jogabilidade
        self.module_id = random.randint(1000, 9999)  # ID único para este módulo
        self.discovered = False  # Se este módulo foi detectado em scanners
    
    def update(self, dt):
        """Atualiza a animação e o comportamento do módulo de filtro.

        Args:
            dt (float): Tempo desde o último quadro em segundos
        """
        # Chama a atualização da classe base para animações básicas
        super().update(dt)
        
        # Verifica se o jogador está próximo para um efeito de dica
        if not self.collected and hasattr(self.game, 'player'):
            player_dist = math.sqrt(
                (self.rect.centerx - self.game.player.rect.centerx) ** 2 +
                (self.rect.centery - self.game.player.rect.centery) ** 2
            )
            
            # Se o jogador estiver perto o suficiente, marca como descoberto
            if player_dist < 300 and not self.discovered:
                self.discovered = True
                # Aciona o alerta do scanner se o jogo tiver um sistema UI/HUD
                if hasattr(self.game, 'hud'):
                    self.game.hud.show_message("Módulo de filtro detectado nas proximidades!")
                # Opcional: Adicionar um indicador direcional para guiar o jogador
    
    def render(self, screen, camera):
        """Renderiza o módulo de filtro com efeitos aprimorados.
        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição na tela
        """
        # Efeito de brilho aprimorado para módulos de filtro
        if DETAIL_LEVEL >= 2 and not self.collected:
            # Pulse effect based on time
            pulse = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(self.age * self.pulse_rate * math.pi))
            
            # Outer glow
            glow_size = int(48 * pulse)
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Desenha brilhos em camadas com opacidade decrescente
            for i in range(3):
                alpha = int(60 * self.glow_intensity * (1 - i * 0.3) * pulse)
                size = int(glow_size * (1 - i * 0.25))
                glow_color = (*CYAN, alpha)
                
                pygame.draw.circle(
                    glow_surf, 
                    glow_color, 
                    (glow_size//2, glow_size//2), 
                    size//2
                )
            
            # Desenha o núcleo interno brilhante
            core_size = int(16 * pulse)
            pygame.draw.circle(
                glow_surf,
                (*LIGHTBLUE, 120), 
                (glow_size//2, glow_size//2), 
                core_size//2
            )
            
            # Posicionado na tela considerando a câmera
            glow_rect = glow_surf.get_rect(center=camera.apply(self.rect).center)
            screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_ADD)

            # If player is close, draw a subtle connection line
            if self.discovered and hasattr(self.game, 'player'):
                player_dist = math.sqrt(
                    (self.rect.centerx - self.game.player.rect.centerx) ** 2 +
                    (self.rect.centery - self.game.player.rect.centery) ** 2
                )
                
                if player_dist < 300: # Se player proximo
                    player_screen_pos = camera.apply(self.game.player).center
                    item_screen_pos = camera.apply(self).center
                    
                    # Calcula o alfa com base na distância (mais fraco quanto mais distante)
                    alpha = int(150 * (1 - player_dist / 300))
                    line_color = (*CYAN, alpha)
                    
                    # Desenha linha tracejada para o item
                    dash_length = 5
                    gap_length = 3
                    dash_pattern = dash_length + gap_length
                    
                    # Calcula o vetor de direção
                    dx = item_screen_pos[0] - player_screen_pos[0]
                    dy = item_screen_pos[1] - player_screen_pos[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance > 0:
                        dx, dy = dx / distance, dy / distance

                        # Desenha linha tracejada
                        steps = int(distance / dash_pattern)
                        for i in range(steps):
                            start_x = player_screen_pos[0] + dx * i * dash_pattern
                            start_y = player_screen_pos[1] + dy * i * dash_pattern
                            end_x = start_x + dx * dash_length
                            end_y = start_y + dy * dash_length
                            pygame.draw.line(screen, line_color, (start_x, start_y), (end_x, end_y), 1) # desenha linha
        
        # Chama o método de renderização pai para efeitos básicos
        super().render(screen, camera)