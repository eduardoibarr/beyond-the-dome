import pygame
from core.settings import (
    HUD_FONT_SIZE,
    HUD_COLOR,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    HEALTH_BAR_X,
    HEALTH_BAR_Y,
    HEALTH_BAR_COLOR_MAX,
    HEALTH_BAR_COLOR_MIN,
    HEALTH_BAR_BACKGROUND_COLOR,
    HEALTH_BAR_BORDER_COLOR,
    RADIATION_BAR_WIDTH,
    RADIATION_BAR_HEIGHT,
    RADIATION_BAR_X,
    RADIATION_BAR_Y,
    RADIATION_BAR_COLOR_MIN,
    RADIATION_BAR_COLOR_MAX,
    RADIATION_BAR_BACKGROUND_COLOR,
    RADIATION_BAR_BORDER_COLOR
)
from core.settings import PLAYER_HEALTH, RADIATION_MAX, PISTOL_MAGAZINE_SIZE, GREEN, RED, YELLOW, WHITE
import math # For pulsing effect


def draw_hud(game):
    """Desenha o Heads-Up Display (Vida, Radiação, Munição, Filtro)."""
    screen = game.screen
    player = game.player
    font = game.font  # Assumindo que o objeto do jogo possui a fonte carregada
    shadow_offset = 1  # Deslocamento da sombra
    border_radius = 8
    border_thickness = 1

    # --- Health Bar ---
    if hasattr(player, 'health'):
        health_pct = max(0, player.health / PLAYER_HEALTH)
        bar_width = HEALTH_BAR_WIDTH
        bar_height = HEALTH_BAR_HEIGHT
        bar_x = HEALTH_BAR_X
        bar_y = HEALTH_BAR_Y
        fill_width = int(bar_width * health_pct)

        # Interpolate color
        # Interpolação da cor da barra de vida
        color_r = int(HEALTH_BAR_COLOR_MIN[0] + (HEALTH_BAR_COLOR_MAX[0] - HEALTH_BAR_COLOR_MIN[0]) * health_pct)
        color_g = int(HEALTH_BAR_COLOR_MIN[1] + (HEALTH_BAR_COLOR_MAX[1] - HEALTH_BAR_COLOR_MIN[1]) * health_pct)
        color_b = int(HEALTH_BAR_COLOR_MIN[2] + (HEALTH_BAR_COLOR_MAX[2] - HEALTH_BAR_COLOR_MIN[2]) * health_pct)
        current_health_color = (max(0, min(255, color_r)), max(0, min(255, color_g)), max(0, min(255, color_b)))
        fill_color_end = (
            max(0, min(255, color_r - 20)), # Ajusta o final da cor para dar efeito degradê
            max(0, min(255, color_g - 20)), # Ajusta o final da cor para dar efeito degradê
            max(0, min(255, color_b - 20)) # Ajusta o final da cor para dar efeito degradê
        )

        # Desenha o fundo da barra
        bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*HEALTH_BAR_BACKGROUND_COLOR, 180), bg_surface.get_rect(),
                         border_radius=border_radius)
        screen.blit(bg_surface, (bar_x, bar_y))

        # Draw fill with gradient
        # ... (fill drawing logic as before) ...
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            gradient_surf = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            # Calcula gradiente por cor
            for x in range(fill_width):
                grad_factor = x / fill_width
                # Calculando r, g, b
                r = int(current_health_color[0] + (fill_color_end[0] - current_health_color[0]) * grad_factor)
                g = int(current_health_color[1] + (fill_color_end[1] - current_health_color[1]) * grad_factor)
                b = int(current_health_color[2] + (fill_color_end[2] - current_health_color[2]) * grad_factor)
                color = (r, g, b)
                pygame.draw.line(gradient_surf, color, (x, 0), (x, bar_height))

            # Cria mascara arredondada na ponta do degradê
            mask_surf = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(mask_surf, (255, 255, 255), mask_surf.get_rect(),
                             border_radius=border_radius)
            gradient_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(gradient_surf, (bar_x, bar_y))

        # Desenha a borda e o destaque
        border_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (*HEALTH_BAR_BORDER_COLOR, 180), border_rect, border_thickness,
                         border_radius=border_radius)
        highlight_height = max(2, int(bar_height * 0.2))
        highlight_rect = pygame.Rect(bar_x + border_thickness, bar_y + border_thickness, bar_width - 2 * border_thickness,
                                     highlight_height)
        highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height),
                                           pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, (255, 255, 255, 40), highlight_surface.get_rect(),
                         border_radius=border_radius - 1)
        screen.blit(highlight_surface, highlight_rect)

        # Desenha o texto
        health_text = f"Vida: {int(player.health)}%"
        shadow_surface = font.render(health_text, True, (0, 0, 0, 120))
        text_x = bar_x + bar_width + 10  # Deslocamento a direita da barra de vida
        text_y = bar_y + (bar_height - shadow_surface.get_height()) // 2
        screen.blit(shadow_surface, (text_x + shadow_offset, text_y + shadow_offset))
        health_text_surface = font.render(health_text, True, HUD_COLOR)
        screen.blit(health_text_surface, (text_x, text_y))

    # --- Radiation Bar ---
    if hasattr(player, 'radiation'):
        radiation_pct = max(0, min(1, player.radiation / RADIATION_MAX))
        rad_bar_x = RADIATION_BAR_X
        rad_bar_y = RADIATION_BAR_Y
        rad_bar_width = RADIATION_BAR_WIDTH
        rad_bar_height = RADIATION_BAR_HEIGHT
        rad_fill_width = int(rad_bar_width * radiation_pct)

        # Interpolate color
        rad_color_r = int(
            RADIATION_BAR_COLOR_MIN[0] + (RADIATION_BAR_COLOR_MAX[0] - RADIATION_BAR_COLOR_MIN[0]) * radiation_pct)
        rad_color_g = int(
            RADIATION_BAR_COLOR_MIN[1] + (RADIATION_BAR_COLOR_MAX[1] - RADIATION_BAR_COLOR_MIN[1]) * radiation_pct)
        rad_color_b = int(
            RADIATION_BAR_COLOR_MIN[2] + (RADIATION_BAR_COLOR_MAX[2] - RADIATION_BAR_COLOR_MIN[2]) * radiation_pct)
        current_rad_color = (max(0, min(255, rad_color_r)), max(0, min(255, rad_color_g)),
                             max(0, min(255, rad_color_b)))
        rad_color_end = (max(0, min(255, rad_color_r - 30)), max(0, min(255, rad_color_g - 30)),
                         max(0, min(255, rad_color_b - 30)))

        # Desenha o fundo da barra
        rad_bg_surface = pygame.Surface((rad_bar_width, rad_bar_height), pygame.SRCALPHA)
        pygame.draw.rect(rad_bg_surface, (*RADIATION_BAR_BACKGROUND_COLOR, 180), rad_bg_surface.get_rect(),
                         border_radius=border_radius)
        screen.blit(rad_bg_surface, (rad_bar_x, rad_bar_y))

        # Desenha o preenchimento com gradiente e efeito de pulsação
        if rad_fill_width > 0:
            rad_fill_rect = pygame.Rect(rad_bar_x, rad_bar_y, rad_fill_width, rad_bar_height)
            rad_gradient_surf = pygame.Surface((rad_fill_width, rad_bar_height), pygame.SRCALPHA)
            # Calcula gradiente por cor
            for x in range(rad_fill_width):
                grad_factor = x / rad_fill_width
                # Calculando r, g, b
                r = int(current_rad_color[0] + (rad_color_end[0] - current_rad_color[0]) * grad_factor)
                g = int(current_rad_color[1] + (rad_color_end[1] - current_rad_color[1]) * grad_factor)
                b = int(current_rad_color[2] + (rad_color_end[2] - current_rad_color[2]) * grad_factor)
                color = (r, g, b)
                pygame.draw.line(rad_gradient_surf, color, (x, 0), (x, rad_bar_height))
            # Efeito de pulsação
            if radiation_pct > 0.75:
                pulse_factor = (math.sin(pygame.time.get_ticks() * 0.01) * 0.2) + 0.8
                rad_gradient_surf.set_alpha(int(255 * pulse_factor))  # Ajusta a transparência
            rad_mask_surf = pygame.Surface((rad_fill_width, rad_bar_height), pygame.SRCALPHA)
            pygame.draw.rect(rad_mask_surf, (255, 255, 255), rad_mask_surf.get_rect(),
                             border_radius=border_radius)
            rad_gradient_surf.blit(rad_mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            screen.blit(rad_gradient_surf, (rad_bar_x, rad_bar_y))
            # if radiation_pct > 0.5:
            #   TODO Efeito de brilho não implementado


        # Desenha a borda e o destaque
        rad_border_rect = pygame.Rect(rad_bar_x, rad_bar_y, rad_bar_width, rad_bar_height)
        pygame.draw.rect(screen, (*RADIATION_BAR_BORDER_COLOR, 180), rad_border_rect, border_thickness,
                         border_radius=border_radius)
        rad_highlight_height = max(2, int(rad_bar_height * 0.2))
        rad_highlight_rect = pygame.Rect(rad_bar_x + border_thickness, rad_bar_y + border_thickness,
                                         rad_bar_width - 2 * border_thickness, rad_highlight_height)
        rad_highlight_surface = pygame.Surface((rad_highlight_rect.width, rad_highlight_rect.height),
                                               pygame.SRCALPHA)
        pygame.draw.rect(rad_highlight_surface, (255, 255, 255, 40), rad_highlight_surface.get_rect(),
                         border_radius=border_radius - 1)
        screen.blit(rad_highlight_surface, rad_highlight_rect)

        # Desenha o texto
        radiation_text = f"Rad: {int(player.radiation)}%"
        rad_shadow_surface = font.render(radiation_text, True, (0, 0, 0, 120))
        rad_text_x = rad_bar_x + rad_bar_width + 10  # Deslocamento a direita da barra de radiação
        rad_text_y = rad_bar_y + (rad_bar_height - rad_shadow_surface.get_height()) // 2
        screen.blit(rad_shadow_surface, (rad_text_x + shadow_offset, rad_text_y + shadow_offset))
        radiation_text_surface = font.render(radiation_text, True, HUD_COLOR)
        screen.blit(radiation_text_surface, (rad_text_x, rad_text_y))

    # --- Indicador do Módulo de Filtro ---
    if hasattr(player, 'has_filter_module'):
        # Lógica do indicador de filtro, usando VERDE/VERMELHO
        if player.has_filter_module:
            protection_text_str = "Filtro: ATIVO"
            protection_color = GREEN
            # TODO Desenhar icone filtro ATIVO
        else:
            protection_text_str = "Filtro: INATIVO"
            protection_color = RED
            # TODO Desenhar icone filtro INATIVO
        shadow_protection = font.render(protection_text_str, True, (0, 0, 0, 150))
        protection_text = font.render(protection_text_str, True, protection_color)
        protection_rect = protection_text.get_rect(topleft=(rad_bar_x, rad_bar_y + rad_bar_height + 5)) # Posiciona abaixo da barra de radiação
        screen.blit(shadow_protection, (protection_rect.x + shadow_offset, protection_rect.y + shadow_offset)) # Desloca a sombra
        screen.blit(protection_text, protection_rect)

    # --- Contador de Munição da Pistola ---
    if hasattr(player, 'pistol') and hasattr(player.pistol, 'ammo_in_mag') and hasattr(
            player, 'reserve_ammo'):
        ammo_text = f"{player.pistol.ammo_in_mag} / {player.reserve_ammo}"
        ammo_color = WHITE
        if player.pistol.reloading:
            ammo_text = "RECARREGANDO..."
            ammo_color = YELLOW
        elif player.pistol.ammo_in_mag <= PISTOL_MAGAZINE_SIZE * 0.2:
            ammo_color = RED

        ammo_surface = font.render(ammo_text, True, ammo_color) #Renderiza o texto
        ammo_rect = ammo_surface.get_rect(bottomright=(game.screen.get_width() - 15,
                                                        game.screen.get_height() - 15)) #Posiciona o texto no canto inferior direito

        # Desenha o fundo
        padding = 8
        ammo_bg_rect = pygame.Rect(ammo_rect.left - padding, ammo_rect.top - padding,
                                   ammo_rect.width + padding * 2, ammo_rect.height + padding * 2)
        ammo_bg_surface = pygame.Surface(ammo_bg_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(ammo_bg_surface, (0, 0, 0, 100), ammo_bg_surface.get_rect(),
                         border_radius=5)
        screen.blit(ammo_bg_surface, ammo_bg_rect.topleft) # Posiciona o retangulo de fundo

        # Desenha o texto
        ammo_shadow = font.render(ammo_text, True, (0, 0, 0, 150))
        screen.blit(ammo_shadow, (ammo_rect.x + shadow_offset, ammo_rect.y + shadow_offset))
        screen.blit(ammo_surface, ammo_rect) # Posiciona o texto de munição