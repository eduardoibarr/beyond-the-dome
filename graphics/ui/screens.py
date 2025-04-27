import pygame
import math
import threading  # Necessário para o fade do áudio da introdução
# from settings import * # Substituído por imports explícitos (substituído por imports explícitos)
from core.settings import (
    WIDTH, HEIGHT, FPS, TITLE, BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN, LIGHTBLUE, DARKGREY, LIGHTGREY, GREY, INTRO_TITLE_FONT_SIZE, INTRO_FONT_SIZE, PROMPT_FONT_SIZE, GAME_OVER_FONT_SIZE,
    # Importa constantes específicas de tamanho de fonte se necessário diretamente, ou confia nos objetos game.font
    # Por simplicidade, assume que funções usam game.font, game.intro_font etc.
)

# --- Funções Auxiliares de Desenho/Animação (Movidas de Game) ---
    
def create_vignette(screen_width, screen_height, color=(0, 0, 0)):
    """Cria uma sobreposição de vinheta (bordas escuras)."""  # Mantive em português
    vignette = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    center_x, center_y = screen_width // 2, screen_height // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)

    for y in range(screen_height):
        for x in range(screen_width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2) / max_dist
            alpha = int(min(200, 255 * (dist * 1.5)**2))
            vignette.set_at((x, y), (*color, alpha))
    return vignette

def fade_in_surface(game, surface, rect, duration, keep_previous=False):
    """Faz fade in de uma superfície mantendo a vinheta e elementos anteriores.""" # Mantive em português
    start_time = pygame.time.get_ticks()
    vignette = create_vignette(WIDTH, HEIGHT)
    orig_alpha = surface.get_alpha()
    if orig_alpha is None: orig_alpha = 255 # Lida com superfícies sem alpha explícito (Mantive em português)

    previous_screen = game.screen.copy() if keep_previous else None

    while pygame.time.get_ticks() - start_time < duration:
        progress = (pygame.time.get_ticks() - start_time) / duration
        alpha = int(orig_alpha * progress)

        if keep_previous:
            game.screen.blit(previous_screen, (0, 0))
        else:
            game.screen.fill(BLACK)
            game.screen.blit(vignette, (0, 0))

        temp_surf = surface.copy()
        temp_surf.set_alpha(alpha)
        game.screen.blit(temp_surf, rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        # Verifica se deve encerrar (Mantive em português)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False # Sinaliza para o jogo parar (Mantive em português)
                return False # Indica encerramento (Mantive em português)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
    return True # Indica sucesso (Mantive em português)

def animate_text_line(game, text_surf, final_rect, duration, keep_previous=True):
    """Anima linha de texto com fade-in e movimento suave."""
    start_time = pygame.time.get_ticks()
    vignette = create_vignette(WIDTH, HEIGHT)
    previous_screen = game.screen.copy() if keep_previous else None
    start_x = final_rect.x - 30
    orig_alpha = text_surf.get_alpha()
    if orig_alpha is None: orig_alpha = 255

    while pygame.time.get_ticks() - start_time < duration:
        progress = (pygame.time.get_ticks() - start_time) / duration
        alpha = int(orig_alpha * progress)

        if progress < 0.5:
            ease = 2 * progress * progress
        else:
            ease = -1 + (4 * progress) - (2 * progress * progress)

        current_x = start_x + (final_rect.x - start_x) * ease
        current_rect = final_rect.copy()
        current_rect.x = int(current_x)

        if keep_previous:
            game.screen.blit(previous_screen, (0, 0))
        else:
            game.screen.fill(BLACK)
            game.screen.blit(vignette, (0, 0))

        temp_surf = text_surf.copy()
        temp_surf.set_alpha(alpha)
        game.screen.blit(temp_surf, current_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
    return True

def wait_time(game, duration):
    """Aguarda duração especificada enquanto verifica eventos de encerramento.""" # Mantive em português
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
        game.clock.tick(FPS)
    return True

def wait_for_keypress_with_animation(game, vignette, title_surface, title_rect, text_surfaces, start_y):
    """Mostra animação de prompt e aguarda pressionamento de tecla.""" # Mantive em português
    prompt_text = "PRESSIONE ENTER" # Mantive em português
    prompt_surface = game.prompt_font.render(prompt_text, True, GREY) # Mantive em português
    prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50))

    waiting = True
    start_time = pygame.time.get_ticks()

    while waiting:
        time_passed = pygame.time.get_ticks() - start_time
        alpha = int(100 + 155 * (0.5 + 0.5 * math.sin(time_passed / 500)))

        game.screen.fill(BLACK)
        game.screen.blit(vignette, (0, 0))
        game.screen.blit(title_surface, title_rect)

        current_y = start_y
        for surf, line in text_surfaces:
            if not line:
                current_y += 20
                continue
            rect = surf.get_rect(center=(WIDTH // 2, current_y + surf.get_height() // 2))
            game.screen.blit(surf, rect)
            current_y += surf.get_height() + 10

        temp_prompt = prompt_surface.copy()
        temp_prompt.set_alpha(alpha)
        game.screen.blit(temp_prompt, prompt_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                waiting = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    game.running = False
                    waiting = False
                    return False
    return True

def fade_out_everything(game, vignette, fade_duration=800):
    """Faz fade out de toda a tela.""" # Mantive em português
    current_screen = game.screen.copy()
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < fade_duration:
        progress = (pygame.time.get_ticks() - start_time) / fade_duration
        alpha = int(255 * (1 - progress))

        game.screen.fill(BLACK)
        temp_screen = current_screen.copy()
        temp_screen.set_alpha(alpha)
        game.screen.blit(temp_screen, (0, 0))

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
    return True

# --- Funções Principais das Telas ---

def display_intro(game):
    """Sequência de introdução no estilo AAA.""" # Mantive em português
    # ... (Copia o conteúdo de display_intro de main.py aqui) ...
    # ... (Substitui self. por game. quando necessário) ...
    intro_scenes = [
        # ... (definição das cenas) ...
        {
            "title": "ALÉM DA CÚPULA",
            "lines": [
                "Ar tóxico. Radiação mortal.",
                "Um mundo hostil e esquecido.",
                "",
                "Mas algo não faz sentido...",
                "",
                "Segredos dormem sob as ruínas.",
                "Verdades que podem destruir tudo que você acredita."
            ]
        }
    ]

    vignette = create_vignette(WIDTH, HEIGHT)
    fade_duration = 1000
    pause_before_title = 700
    title_to_text_pause = 1000
    line_transition_duration = 300

    intro_sound = None
    if hasattr(game, 'audio_manager'): # Verifica se o gerenciador de áudio existe (Mantive em português)
        intro_sound = game.audio_manager.play('intro', volume=0.0, loop=True)
        if intro_sound:
            game.audio_manager.fade(intro_sound, 0.0, 0.7, 2000)

    for scene_index, scene in enumerate(intro_scenes):
        game.screen.fill(BLACK)
        game.screen.blit(vignette, (0, 0))
        pygame.display.flip()

        if not wait_time(game, pause_before_title): return

        title_surface = game.intro_title_font.render(scene["title"], True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))

        if not fade_in_surface(game, title_surface, title_rect, fade_duration): return
        if not wait_time(game, title_to_text_pause): return

        text_surfaces = []
        line_pause_times = []
        total_height = 0
        for i, line in enumerate(scene["lines"]):
            # ... (lógica de cálculo de pausa) ...
            if not line:
                total_height += 20
                text_surfaces.append((None, None))
                line_pause_times.append(400)
            else:
                text_surf = game.intro_font.render(line, True, WHITE)
                text_surfaces.append((text_surf, line))
                total_height += text_surf.get_height() + 10
                if i == len(scene["lines"]) - 1: line_pause_times.append(1200)
                elif "..." in line: line_pause_times.append(900)
                elif i == 0: line_pause_times.append(700)
                elif line.endswith("."): line_pause_times.append(600)
                else: line_pause_times.append(400)

        start_y = title_rect.bottom + 40
        current_y = start_y
        for i, (text_surf, line) in enumerate(text_surfaces):
            if text_surf is None:
                current_y += 20
                continue
            text_rect = text_surf.get_rect(center=(WIDTH // 2, current_y + text_surf.get_height() // 2))
            if not animate_text_line(game, text_surf, text_rect, line_transition_duration, keep_previous=True): return
            if i < len(text_surfaces) - 1:
                if not wait_time(game, line_pause_times[i]): return
            current_y += text_surf.get_height() + 10

        if not wait_for_keypress_with_animation(game, vignette, title_surface, title_rect, text_surfaces, start_y): return

        if scene_index == len(intro_scenes) - 1 and intro_sound and hasattr(game, 'audio_manager'):
             game.audio_manager.fade(intro_sound, 0.7, 0.0, 2000)

        if not fade_out_everything(game, vignette, 1200): return

    if intro_sound and hasattr(game, 'audio_manager'):
        game.audio_manager.stop(intro_sound)

    game.screen.fill(BLACK)
    pygame.display.flip()

def show_start_screen(game):
    """Exibe a tela inicial com visuais melhorados.""" # Traduzi para pt-br
    # ... (Copia o conteúdo de show_start_screen de main.py aqui) ...
    # ... (Substitui self. por game. quando necessário) ...
    gradient_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_value = int(25 * (y / HEIGHT))
        gradient_surface.fill((0, 0, color_value), (0, y, WIDTH, 1))

    t = pygame.time.get_ticks() * 0.001
    for x in range(0, WIDTH, 4):
        wave = math.sin(x * 0.01 + t) * 10
        wave_pos = int(wave) + HEIGHT // 2
        if 0 < wave_pos < HEIGHT:
            pygame.draw.line(gradient_surface, (0, 40, 80), (x, wave_pos - 2), (x + 3, wave_pos - 2), 4)
    game.screen.blit(gradient_surface, (0, 0))

    vignette = create_vignette(WIDTH, HEIGHT)
    game.screen.blit(vignette, (0, 0))

    title_font = game.intro_title_font
    title_shadow = title_font.render(TITLE, True, (0, 0, 40))
    title_text = title_font.render(TITLE, True, (120, 180, 255))
    pulse = (math.sin(pygame.time.get_ticks() * 0.002) * 0.2) + 0.8
    glow_size = 10
    glow_color = (0, 100, 200, 50)
    title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3))
    glow_surf = pygame.Surface((title_rect.width + glow_size*2, title_rect.height + glow_size*2), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, glow_color, (0, 0, title_rect.width + glow_size*2, title_rect.height + glow_size*2), border_radius=20)
    glow_rect = glow_surf.get_rect(center=title_rect.center)
    glow_surf.set_alpha(int(120 * pulse))
    game.screen.blit(glow_surf, glow_rect)

    shadow_offset = 2
    game.screen.blit(title_shadow, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
    game.screen.blit(title_text, title_rect)

    line_y = title_rect.bottom + 10
    line_width = title_rect.width * 0.8
    line_height = 2
    line_rect = pygame.Rect(WIDTH/2 - line_width/2, line_y, line_width, line_height)
    pygame.draw.rect(game.screen, (80, 140, 240), line_rect, border_radius=line_height//2)

    alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.002)) * 255)
    instr_font = game.intro_font
    instr_text = instr_font.render("Pressione qualquer tecla para começar", True, (200, 200, 255))
    instr_rect = instr_text.get_rect(center=(WIDTH / 2, HEIGHT * 2 / 3))
    instr_surf = pygame.Surface((instr_text.get_width(), instr_text.get_height()), pygame.SRCALPHA)
    instr_surf.fill((255, 255, 255, 0))
    instr_surf.blit(instr_text, (0, 0))
    instr_surf.set_alpha(alpha)
    game.screen.blit(instr_surf, instr_rect)

    info_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 300, 70)
    info_surf = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(info_surf, (0, 0, 40, 160), info_surf.get_rect(), border_radius=10)
    pygame.draw.rect(info_surf, (100, 150, 255, 40), info_surf.get_rect(), 1, border_radius=10)
    info_font = game.prompt_font
    info_line1 = info_font.render("WASD: Movimento | Mouse: Mirar", True, (180, 180, 255))
    info_line2 = info_font.render("Clique: Atirar | E: Interagir", True, (180, 180, 255))
    info_surf.blit(info_line1, (info_rect.width//2 - info_line1.get_width()//2, 15))
    info_surf.blit(info_line2, (info_rect.width//2 - info_line2.get_width()//2, 40))
    game.screen.blit(info_surf, info_rect)

    pygame.display.flip()
    wait_for_key(game) # Pass game object

def show_go_screen(game):
    """Exibe a tela de Game Over com visuais melhorados."""  # Traduzi para pt-br
    # ... (Copia o conteúdo de show_go_screen de main.py aqui) ...
    # ... (Substitui self. por game. quando necessário) ...
    if not game.running:
        return

    gradient_surface = pygame.Surface((WIDTH, HEIGHT))
    # ... (desenho do fundo e sangue)
    for y in range(HEIGHT):
        red_value = int(35 * (y / HEIGHT))
        gradient_surface.fill((red_value, 0, 0), (0, y, WIDTH, 1))
    for _ in range(1000):
        # ... (dust effect)
        pass
    game.screen.blit(gradient_surface, (0, 0))
    vignette = create_vignette(WIDTH, HEIGHT, color=(40, 0, 0))
    game.screen.blit(vignette, (0, 0))
    for _ in range(10):
        # ... (blood streak effect)
        pass

    title_font = game.game_over_font
    title_text_base = "Você morreu..."
    for i, char in enumerate(title_text_base):
        char_text = title_font.render(char, True, (200, 0, 0))
        shadow_text = title_font.render(char, True, (60, 0, 0))
        game.screen.blit(char_text, (WIDTH/2 - char_text.get_width()/2, HEIGHT/3 + i*char_text.get_height()))
        game.screen.blit(shadow_text, (WIDTH/2 - shadow_text.get_width()/2, HEIGHT/3 + i*shadow_text.get_height() + 1)) # Mantive em português

    if game.cause_of_death:
        death_font = game.font
        death_text = death_font.render(game.cause_of_death, True, (220, 220, 220))
        death_shadow = death_font.render(game.cause_of_death, True, (0, 0, 0))
        game.screen.blit(death_text, (WIDTH/2 - death_text.get_width()/2, HEIGHT/3 + len(title_text_base)*death_text.get_height()))
        game.screen.blit(death_shadow, (WIDTH/2 - death_shadow.get_width()/2, HEIGHT/3 + len(title_text_base)*death_shadow.get_height() + 1))

    retry_rect = pygame.Rect(WIDTH / 2 - 120, HEIGHT * 3 / 4 - 25, 240, 50)
    retry_surf = pygame.Surface((retry_rect.width, retry_rect.height), pygame.SRCALPHA)
    button_color = (100, 20, 20, 220)
    pygame.draw.rect(retry_surf, button_color, retry_surf.get_rect(), border_radius=10)
    pulse = (math.sin(pygame.time.get_ticks() * 0.002) * 0.2) + 0.8
    retry_surf.set_alpha(int(255 * pulse))
    retry_font = game.font
    retry_text = retry_font.render("Tentar Novamente", True, (255, 200, 200))
    retry_text_pos = ((retry_rect.width - retry_text.get_width()) // 2, (retry_rect.height - retry_text.get_height()) // 2)
    retry_surf.blit(retry_text, retry_text_pos)
    game.screen.blit(retry_surf, retry_rect)

    pygame.display.flip()
    wait_for_key(game, pygame.K_RETURN)

def wait_for_key(game, specific_key=None):
    """Aguarda qualquer pressionamento de tecla ou um pressionamento de tecla específico.""" # Traduzi para pt-br
    waiting = True
    while waiting:
        game.clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                game.running = False
            if event.type == pygame.KEYDOWN:
                if specific_key is None:
                    waiting = False
                elif event.key == specific_key:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                     waiting = False
                     game.running = False # Permite que escape saia aqui também (Traduzi para pt-br)