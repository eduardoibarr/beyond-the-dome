import pygame
import math
import random
from core.settings import ( CYAN, LIGHTBLUE, DETAIL_LEVEL )
from items.item import Item

class FilterModule(Item):
    """Módulo de filtro - Item principal do jogo.
    
    Este item é crucial para o objetivo principal do jogo, onde o jogador deve coletar
    módulos de filtro para reparar o sistema de filtragem de ar da cúpula. Cada módulo
    possui características especiais:
    
    - Efeitos visuais aprimorados (brilho e pulsação)
    - Sistema de detecção quando o jogador está próximo
    - Indicador visual que guia o jogador até o módulo
    - ID único para rastreamento e progresso do jogo
    """
    def __init__(self, game, x, y, groups=None):
        """Inicializa um módulo de filtro.
        
        Args:
            game: Referência ao objeto principal do jogo
            x (int): Posição X em coordenadas do mundo
            y (int): Posição Y em coordenadas do mundo
            groups (list): Lista de pygame.sprite.Group para adicionar este sprite
        """
        super().__init__(game, x, y, item_type='filter_module', groups=groups)
        
        # Propriedades de animação e efeitos visuais
        self.bob_height = 8  # Altura da flutuação do item
        self.bob_speed = 1.5  # Velocidade da flutuação
        self.pulse_rate = 0.8  # Frequência do efeito de pulsação
        self.glow_intensity = 0.8  # Intensidade do brilho
        
        # Propriedades de jogabilidade
        self.module_id = random.randint(1000, 9999)  # Identificador único do módulo
        self.discovered = False  # Estado de detecção pelo jogador
    
    def update(self, dt):
        """Atualiza o estado e comportamento do módulo de filtro.
        
        Este método:
        1. Atualiza as animações básicas
        2. Verifica a proximidade do jogador
        3. Gerencia o estado de descoberta
        4. Ativa alertas visuais quando necessário
        
        Args:
            dt (float): Tempo desde o último quadro em segundos
        """
        super().update(dt)
        
        # Verifica a proximidade do jogador para efeitos de dica
        if not self.collected and hasattr(self.game, 'player'):
            player_dist = math.sqrt(
                (self.rect.centerx - self.game.player.rect.centerx) ** 2 +
                (self.rect.centery - self.game.player.rect.centery) ** 2
            )
            
            # Ativa o estado de descoberta quando o jogador está próximo
            if player_dist < 300 and not self.discovered:
                self.discovered = True
                if hasattr(self.game, 'hud'):
                    self.game.hud.show_message("Módulo de filtro detectado nas proximidades!")
    
    def render(self, screen, camera):
        """Renderiza o módulo de filtro com efeitos visuais avançados.
        
        Implementa:
        1. Efeito de brilho pulsante
        2. Núcleo interno brilhante
        3. Linha de conexão com o jogador quando próximo
        4. Efeitos de camadas com opacidade variável
        
        Args:
            screen (pygame.Surface): Tela para renderizar
            camera (Camera): Câmera para calcular a posição na tela
        """
        # Renderiza efeitos de brilho apenas se o nível de detalhe for suficiente
        if DETAIL_LEVEL >= 2 and not self.collected:
            # Calcula o efeito de pulsação baseado no tempo
            pulse = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(self.age * self.pulse_rate * math.pi))
            
            # Cria superfície para o efeito de brilho
            glow_size = int(48 * pulse)
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Desenha camadas de brilho com opacidade decrescente
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
            
            # Desenha o núcleo central brilhante
            core_size = int(16 * pulse)
            pygame.draw.circle(
                glow_surf,
                (*LIGHTBLUE, 120), 
                (glow_size//2, glow_size//2), 
                core_size//2
            )
            
            # Posiciona o brilho na tela considerando a câmera
            glow_rect = glow_surf.get_rect(center=camera.apply(self.rect).center)
            screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_ADD)

            # Desenha linha de conexão quando o jogador está próximo
            if self.discovered and hasattr(self.game, 'player'):
                player_dist = math.sqrt(
                    (self.rect.centerx - self.game.player.rect.centerx) ** 2 +
                    (self.rect.centery - self.game.player.rect.centery) ** 2
                )
                
                if player_dist < 300:
                    player_screen_pos = camera.apply(self.game.player).center
                    item_screen_pos = camera.apply(self).center
                    
                    # Calcula a opacidade da linha baseada na distância
                    alpha = int(150 * (1 - player_dist / 300))
                    line_color = (*CYAN, alpha)
                    
                    # Configuração do padrão de linha tracejada
                    dash_length = 5
                    gap_length = 3
                    dash_pattern = dash_length + gap_length
                    
                    # Calcula o vetor de direção
                    dx = item_screen_pos[0] - player_screen_pos[0]
                    dy = item_screen_pos[1] - player_screen_pos[1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance > 0:
                        dx, dy = dx / distance, dy / distance

                        # Desenha a linha tracejada
                        steps = int(distance / dash_pattern)
                        for i in range(steps):
                            start_x = player_screen_pos[0] + dx * i * dash_pattern
                            start_y = player_screen_pos[1] + dy * i * dash_pattern
                            end_x = start_x + dx * dash_length
                            end_y = start_y + dy * dash_length
                            pygame.draw.line(screen, line_color, (start_x, start_y), (end_x, end_y), 1)
        
        # Renderiza os efeitos básicos do item
        super().render(screen, camera)