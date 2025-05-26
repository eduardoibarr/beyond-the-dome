import pygame
import math
import random
from core.settings import (
    WIDTH, HEIGHT, FPS, TITLE, BLACK, WHITE, GREY
)

def create_vignette(screen_width, screen_height, color=(0, 0, 0)):

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
    start_time = pygame.time.get_ticks()
    vignette = create_vignette(WIDTH, HEIGHT)
    orig_alpha = surface.get_alpha()
    if orig_alpha is None:
        orig_alpha = 255

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
    return True

def animate_text_line(game, text_surf, final_rect, duration, keep_previous=True):
    start_time = pygame.time.get_ticks()
    vignette = create_vignette(WIDTH, HEIGHT)
    previous_screen = game.screen.copy() if keep_previous else None
    start_x = final_rect.x - 30
    orig_alpha = text_surf.get_alpha()
    if orig_alpha is None:
        orig_alpha = 255

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
    prompt_text = "PRESSIONE ENTER"
    prompt_surface = game.prompt_font.render(prompt_text, True, GREY)
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

def wait_time_with_skip(game, duration):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        game.clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                    return False
    return True

def fade_in_surface_with_skip(game, surface, rect, duration, skip_text, skip_rect, keep_previous=False):
    start_time = pygame.time.get_ticks()
    if keep_previous:
        background = game.screen.copy()

    while True:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed >= duration:
            break

        alpha = int((elapsed / duration) * 255)

        if not keep_previous:
            game.screen.fill(BLACK)
            vignette = create_vignette(WIDTH, HEIGHT)
            game.screen.blit(vignette, (0, 0))
        else:
            game.screen.blit(background, (0, 0))

        temp_surface = surface.copy()
        temp_surface.set_alpha(alpha)
        game.screen.blit(temp_surface, rect)
        game.screen.blit(skip_text, skip_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                    return False

    if not keep_previous:
        game.screen.fill(BLACK)
        vignette = create_vignette(WIDTH, HEIGHT)
        game.screen.blit(vignette, (0, 0))
    else:
        game.screen.blit(background, (0, 0))

    game.screen.blit(surface, rect)
    game.screen.blit(skip_text, skip_rect)
    pygame.display.flip()
    return True

def animate_text_line_with_skip(game, text_surf, final_rect, duration, skip_text, skip_rect, keep_previous=True):
    start_time = pygame.time.get_ticks()
    start_x = -text_surf.get_width()
    end_x = final_rect.x

    if keep_previous:
        background = game.screen.copy()

    while True:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed >= duration:
            break

        progress = elapsed / duration
        progress = 1 - (1 - progress) ** 3

        current_x = start_x + (end_x - start_x) * progress
        current_rect = final_rect.copy()
        current_rect.x = int(current_x)

        if keep_previous:
            game.screen.blit(background, (0, 0))
        else:
            game.screen.fill(BLACK)
            vignette = create_vignette(WIDTH, HEIGHT)
            game.screen.blit(vignette, (0, 0))

        game.screen.blit(text_surf, current_rect)
        game.screen.blit(skip_text, skip_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                    return False

    if keep_previous:
        game.screen.blit(background, (0, 0))
    else:
        game.screen.fill(BLACK)
        vignette = create_vignette(WIDTH, HEIGHT)
        game.screen.blit(vignette, (0, 0))

    game.screen.blit(text_surf, final_rect)
    game.screen.blit(skip_text, skip_rect)
    pygame.display.flip()
    return True

def wait_for_keypress_with_animation_skip(game, vignette, title_surface, title_rect, text_surfaces, start_y, skip_text, skip_rect):
    pulse_speed = 0.002
    waiting = True

    while waiting:
        pulse = (math.sin(pygame.time.get_ticks() * pulse_speed) + 1) / 2
        alpha = int(100 + 155 * pulse)

        game.screen.fill(BLACK)
        game.screen.blit(vignette, (0, 0))

        title_copy = title_surface.copy()
        title_copy.set_alpha(alpha)
        game.screen.blit(title_copy, title_rect)

        current_y = start_y
        for text_surf, line in text_surfaces:
            if text_surf is None:
                current_y += 20
                continue
            text_rect = text_surf.get_rect(center=(WIDTH // 2, current_y + text_surf.get_height() // 2))
            game.screen.blit(text_surf, text_rect)
            current_y += text_surf.get_height() + 10

        prompt_font = pygame.font.Font(None, 24)
        prompt_text = prompt_font.render("Pressione qualquer tecla para continuar", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        prompt_copy = prompt_text.copy()
        prompt_copy.set_alpha(alpha)
        game.screen.blit(prompt_copy, prompt_rect)

        game.screen.blit(skip_text, skip_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                    return False
                else:
                    waiting = False
    return True

def fade_out_everything_with_skip(game, vignette, fade_duration=800):
    start_time = pygame.time.get_ticks()
    initial_screen = game.screen.copy()

    while True:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed >= fade_duration:
            break

        alpha = int(255 * (elapsed / fade_duration))

        game.screen.blit(initial_screen, (0, 0))

        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill(BLACK)
        fade_surface.set_alpha(alpha)
        game.screen.blit(fade_surface, (0, 0))

        pygame.display.flip()
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                    return False
    return True

def display_intro(game):

    intro_scenes = [
        {
            "title": "BEYOND THE DOME",
            "lines": [
                "A humanidade foi devastada por uma catástrofe.",
                "A cúpula é a última defesa.",
                "Uma IA governou a humanidade por séculos.",
                "Mas algo não faz sentido...",
                "A cúpula está caindo..."
            ]
        }
    ]

    vignette = create_vignette(WIDTH, HEIGHT)
    fade_duration = 1000
    pause_before_title = 700
    title_to_text_pause = 1000
    line_transition_duration = 850

    intro_sound = None
    if hasattr(game, 'audio_manager'):
        game.audio_manager.play('music/intro', volume=0.7, loop=True)
        intro_sound = True

    skip_font = pygame.font.Font(None, 24)
    skip_text = skip_font.render("Pressione ESC ou ESPAÇO para pular", True, (150, 150, 150))
    skip_rect = skip_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))

    for scene_index, scene in enumerate(intro_scenes):

        game.screen.fill(BLACK)
        game.screen.blit(vignette, (0, 0))
        game.screen.blit(skip_text, skip_rect)
        pygame.display.flip()

        if not wait_time_with_skip(game, pause_before_title):
            break

        title_surface = game.intro_title_font.render(scene["title"], True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))

        if not fade_in_surface_with_skip(game, title_surface, title_rect, fade_duration, skip_text, skip_rect):
            break
        if not wait_time_with_skip(game, title_to_text_pause):
            break

        text_surfaces = []
        line_pause_times = []
        total_height = 0

        for i, line in enumerate(scene["lines"]):
            if not line:
                total_height += 20
                text_surfaces.append((None, None))
                line_pause_times.append(400)
            else:
                text_surf = game.intro_font.render(line, True, WHITE)
                text_surfaces.append((text_surf, line))
                total_height += text_surf.get_height() + 10
                if i == len(scene["lines"]) - 1:
                    line_pause_times.append(1200)
                elif "..." in line:
                    line_pause_times.append(900)
                elif i == 0:
                    line_pause_times.append(700)
                elif line.endswith("."):
                    line_pause_times.append(600)
                else:
                    line_pause_times.append(400)

        start_y = title_rect.bottom + 40
        current_y = start_y
        skip_pressed = False
        for i, (text_surf, line) in enumerate(text_surfaces):
            if text_surf is None:
                current_y += 20
                continue
            text_rect = text_surf.get_rect(center=(WIDTH // 2, current_y + text_surf.get_height() // 2))
            if not animate_text_line_with_skip(game, text_surf, text_rect, line_transition_duration, skip_text, skip_rect, keep_previous=True):
                skip_pressed = True
                break
            if i < len(text_surfaces) - 1:
                if not wait_time_with_skip(game, line_pause_times[i]):
                    skip_pressed = True
                    break
            current_y += text_surf.get_height() + 10

        if skip_pressed:
            break

        if not wait_for_keypress_with_animation_skip(game, vignette, title_surface, title_rect, text_surfaces, start_y, skip_text, skip_rect):
            break

        if scene_index == len(intro_scenes) - 1 and intro_sound and hasattr(game, 'audio_manager'):
            game.stop_music(fadeout_ms=1500)
            intro_sound = False

        if not fade_out_everything_with_skip(game, vignette, 1200):
            break

    if intro_sound and hasattr(game, 'audio_manager'):
        game.stop_music(fadeout_ms=500)

    game.screen.fill(BLACK)
    pygame.display.flip()

def show_start_screen(game):

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
    wait_for_key(game)

def show_go_screen(game):
    if not game.running:
        return

    current_screen = game.screen.copy()
    for alpha in range(0, 256, 5):
        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill((0, 0, 0))
        fade.set_alpha(alpha)
        game.screen.blit(current_screen, (0, 0))
        game.screen.blit(fade, (0, 0))
        pygame.display.flip()
        game.clock.tick(60)

    gradient_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        red_value = int(40 * (1 - y / HEIGHT))
        dark_value = int(red_value * 0.2)
        gradient_surface.fill((red_value, dark_value, dark_value), (0, y, WIDTH, 1))

    blood_streaks = []
    for _ in range(15):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT // 3)
        length = random.randint(50, 300)
        width = random.randint(2, 8)
        speed = random.uniform(0.5, 2.0)
        opacity = random.randint(150, 255)
        blood_streaks.append({
            'x': x, 'y': y, 'length': length, 'width': width,
            'speed': speed, 'opacity': opacity, 'progress': 0
        })

    dust_particles = []
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        speed = random.uniform(0.1, 0.5)
        opacity = random.randint(30, 100)
        dust_particles.append({
            'x': x, 'y': y, 'size': size, 'speed': speed,
            'opacity': opacity, 'angle': random.uniform(0, 2 * math.pi)
        })

    vignette = create_vignette(WIDTH, HEIGHT, color=(60, 0, 0))

    heartbeat_sounds = []
    heartbeat_times = []
    heartbeat_interval = 1500
    heartbeat_available = False
    if hasattr(game, 'audio_manager'):

        heartbeat_sound = game.audio_manager.play('heartbeat', volume=0.7)
        if heartbeat_sound:
            heartbeat_sounds.append(heartbeat_sound)
            heartbeat_times.append(pygame.time.get_ticks())
            heartbeat_available = True

        elif hasattr(game, 'audio_manager'):
            heartbeat_sound = game.audio_manager.play('game_over', volume=0.5, loop=True)
            if heartbeat_sound:
                heartbeat_sounds.append(heartbeat_sound)
                heartbeat_times.append(pygame.time.get_ticks())
                heartbeat_available = True

    title_text = "GAME OVER"

    animation_time = 3000
    start_time = pygame.time.get_ticks()
    fully_rendered = False

    while not fully_rendered:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / animation_time)

        if elapsed > 0 and heartbeat_available and hasattr(game, 'audio_manager'):
            last_beat = current_time - heartbeat_times[-1]
            if last_beat > heartbeat_interval:
                if not any(sound for sound in heartbeat_sounds if sound and hasattr(sound, 'get_busy') and sound.get_busy()):
                    heartbeat_sound = game.audio_manager.play('heartbeat', volume=0.7)
                    if heartbeat_sound:
                        heartbeat_sounds.append(heartbeat_sound)
                        heartbeat_times.append(current_time)

                        game.screen.fill((100, 0, 0))
                        pygame.display.flip()
                        pygame.time.delay(50)

        for streak in blood_streaks:
            streak['progress'] = min(1.0, streak['progress'] + streak['speed'] * 0.01)

        for particle in dust_particles:
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            if particle['x'] < 0:
                particle['x'] = WIDTH
            elif particle['x'] > WIDTH:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = HEIGHT
            elif particle['y'] > HEIGHT:
                particle['y'] = 0

        game.screen.blit(gradient_surface, (0, 0))

        for streak in blood_streaks:
            current_length = int(streak['length'] * streak['progress'])
            if current_length > 0:
                blood_surf = pygame.Surface((streak['width'], current_length), pygame.SRCALPHA)
                for i in range(current_length):
                    alpha = max(0, streak['opacity'] - (i / current_length * streak['opacity']))
                    color = (120, 0, 0, int(alpha))
                    pygame.draw.line(blood_surf, color, (streak['width']//2, i), (streak['width']//2, i+1), streak['width'])
                game.screen.blit(blood_surf, (streak['x'] - streak['width']//2, streak['y']))

        particle_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for particle in dust_particles:
            alpha = int(particle['opacity'] * (1 - progress * 0.5))
            pygame.draw.circle(
                particle_surf,
                (100, 10, 10, alpha),
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        game.screen.blit(particle_surf, (0, 0))

        game.screen.blit(vignette, (0, 0))

        if progress > 0.2:
            title_progress = min(1.0, (progress - 0.2) / 0.4)
            title_scale = 1.5 - (0.5 * title_progress)

            title_font = pygame.font.Font(None, int(100 * title_scale))
            if hasattr(game, 'game_over_font'):
                title_font = game.game_over_font

            title_chars = []
            total_width = 0
            for char in title_text:
                char_surf = title_font.render(char, True, (200, 0, 0))
                char_shadow = title_font.render(char, True, (60, 0, 0))
                title_chars.append((char_surf, char_shadow))
                total_width += char_surf.get_width()

            x_offset = (WIDTH - total_width) // 2
            for i, (char_surf, char_shadow) in enumerate(title_chars):
                y_offset = math.sin(current_time * 0.003 + i * 0.5) * 5

                game.screen.blit(
                    char_shadow,
                    (x_offset + 3, HEIGHT//3 - char_shadow.get_height()//2 + y_offset + 3)
                )

                game.screen.blit(
                    char_surf,
                    (x_offset, HEIGHT//3 - char_surf.get_height()//2 + y_offset)
                )

                x_offset += char_surf.get_width()

        if progress > 0.6 and hasattr(game, 'cause_of_death') and game.cause_of_death:
            death_progress = min(1.0, (progress - 0.6) / 0.3)

            death_font = pygame.font.Font(None, 36)
            if hasattr(game, 'font'):
                death_font = game.font

            death_text = death_font.render(game.cause_of_death, True, (220, 220, 220))
            death_shadow = death_font.render(game.cause_of_death, True, (0, 0, 0))

            death_text.set_alpha(int(255 * death_progress))
            death_shadow.set_alpha(int(255 * death_progress))

            game.screen.blit(
                death_shadow,
                (WIDTH//2 - death_shadow.get_width()//2 + 2, HEIGHT//2 - death_shadow.get_height()//2 + 2)
            )
            game.screen.blit(
                death_text,
                (WIDTH//2 - death_text.get_width()//2, HEIGHT//2 - death_text.get_height()//2)
            )

        if progress > 0.9:
            instr_font = pygame.font.Font(None, 28)
            if hasattr(game, 'prompt_font'):
                instr_font = game.prompt_font

            instr_text_surf = instr_font.render("Pressione qualquer tecla para tentar novamente", True, (220, 220, 220))
            instr_shadow_surf = instr_font.render("Pressione qualquer tecla para tentar novamente", True, (0, 0, 0))

            text_rect = instr_text_surf.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4 + 20))
            shadow_pos = text_rect.move(2, 2)

            instruction_progress = min(1.0, (progress - 0.9) / 0.1)
            alpha = int(255 * instruction_progress)
            instr_text_surf.set_alpha(alpha)
            instr_shadow_surf.set_alpha(alpha)

            game.screen.blit(instr_shadow_surf, shadow_pos)
            game.screen.blit(instr_text_surf, text_rect)

        pygame.display.flip()
        game.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False
                    return

        if elapsed >= animation_time + 500:
            fully_rendered = True

    if hasattr(game, 'audio_manager'):
        for sound in heartbeat_sounds:
            if sound:
                game.audio_manager.stop(sound)

    wait_for_key(game)

def wait_for_key(game, specific_key=None):
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
                    game.running = False
