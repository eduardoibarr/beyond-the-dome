import pygame
import math
import random
from core.settings import (
    WIDTH, HEIGHT, FPS, TITLE, BLACK, WHITE, GREY
)
    
def create_vignette(screen_width, screen_height, color=(0, 0, 0)):
    """Cria uma sobreposição de vinheta (bordas escuras) para efeito visual.
    
    A vinheta é uma técnica visual que escurece as bordas da tela,
    criando um efeito de foco no centro e melhorando a imersão.
    
    Args:
        screen_width (int): Largura da tela em pixels
        screen_height (int): Altura da tela em pixels
        color (tuple): Cor RGB da vinheta (padrão: preto)
        
    Returns:
        pygame.Surface: Superfície com a vinheta aplicada
    """
    # Cria uma superfície com suporte à transparência
    vignette = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    center_x, center_y = screen_width // 2, screen_height // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)

    # Calcula a intensidade da vinheta para cada pixel
    for y in range(screen_height):
        for x in range(screen_width):
            # Calcula a distância do pixel ao centro
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2) / max_dist
            # Ajusta a transparência baseado na distância
            alpha = int(min(200, 255 * (dist * 1.5)**2))
            vignette.set_at((x, y), (*color, alpha))
    return vignette

def fade_in_surface(game, surface, rect, duration, keep_previous=False):
    """Realiza um efeito de fade in em uma superfície.
    
    Este método cria uma transição suave para exibir uma superfície,
    mantendo a vinheta e elementos anteriores se necessário.
    
    Args:
        game: Referência ao objeto principal do jogo
        surface (pygame.Surface): Superfície a ser exibida
        rect (pygame.Rect): Retângulo de posicionamento
        duration (int): Duração da transição em milissegundos
        keep_previous (bool): Se True, mantém o conteúdo anterior da tela
        
    Returns:
        bool: True se a transição foi concluída, False se foi interrompida
    """
    start_time = pygame.time.get_ticks()
    vignette = create_vignette(WIDTH, HEIGHT)
    orig_alpha = surface.get_alpha()
    if orig_alpha is None: 
        orig_alpha = 255  # Define alpha padrão para superfícies sem transparência

    # Mantém uma cópia da tela anterior se necessário
    previous_screen = game.screen.copy() if keep_previous else None

    # Loop de animação do fade in
    while pygame.time.get_ticks() - start_time < duration:
        # Calcula o progresso da transição
        progress = (pygame.time.get_ticks() - start_time) / duration
        alpha = int(orig_alpha * progress)

        # Renderiza o fundo
        if keep_previous:
            game.screen.blit(previous_screen, (0, 0))
        else:
            game.screen.fill(BLACK)
            game.screen.blit(vignette, (0, 0))

        # Aplica o fade in na superfície
        temp_surf = surface.copy()
        temp_surf.set_alpha(alpha)
        game.screen.blit(temp_surf, rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        # Verifica eventos de encerramento
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
    return True

def animate_text_line(game, text_surf, final_rect, duration, keep_previous=True):
    """Anima uma linha de texto com efeitos de fade in e movimento.
    
    Cria uma animação suave para exibir texto, combinando movimento
    horizontal e fade in para um efeito mais dinâmico.
    
    Args:
        game: Referência ao objeto principal do jogo
        text_surf (pygame.Surface): Superfície com o texto
        final_rect (pygame.Rect): Posição final do texto
        duration (int): Duração da animação em milissegundos
        keep_previous (bool): Se True, mantém o conteúdo anterior da tela
        
    Returns:
        bool: True se a animação foi concluída, False se foi interrompida
    """
    start_time = pygame.time.get_ticks()
    vignette = create_vignette(WIDTH, HEIGHT)
    previous_screen = game.screen.copy() if keep_previous else None
    start_x = final_rect.x - 30  # Posição inicial fora da tela
    orig_alpha = text_surf.get_alpha()
    if orig_alpha is None: 
        orig_alpha = 255

    # Loop de animação
    while pygame.time.get_ticks() - start_time < duration:
        progress = (pygame.time.get_ticks() - start_time) / duration
        alpha = int(orig_alpha * progress)

        # Aplica curva de aceleração para movimento suave
        if progress < 0.5:
            ease = 2 * progress * progress
        else:
            ease = -1 + (4 * progress) - (2 * progress * progress)

        # Calcula posição atual com easing
        current_x = start_x + (final_rect.x - start_x) * ease
        current_rect = final_rect.copy()
        current_rect.x = int(current_x)

        # Renderiza o fundo
        if keep_previous:
            game.screen.blit(previous_screen, (0, 0))
        else:
            game.screen.fill(BLACK)
            game.screen.blit(vignette, (0, 0))

        # Aplica o fade in e movimento no texto
        temp_surf = text_surf.copy()
        temp_surf.set_alpha(alpha)
        game.screen.blit(temp_surf, current_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        # Verifica eventos de encerramento
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.running = False
                return False
    return True

def wait_time(game, duration):
    """Aguarda um período específico enquanto verifica eventos.
    
    Mantém o jogo responsivo durante a espera, verificando
    eventos de encerramento e controlando o FPS.
    
    Args:
        game: Referência ao objeto principal do jogo
        duration (int): Tempo de espera em milissegundos
        
    Returns:
        bool: True se a espera foi concluída, False se foi interrompida
    """
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        # Verifica eventos de encerramento
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
    """Aguarda pressionamento de tecla com animação de prompt.
    
    Exibe uma animação de prompt piscante enquanto aguarda
    o jogador pressionar uma tecla para continuar.
    
    Args:
        game: Referência ao objeto principal do jogo
        vignette (pygame.Surface): Vinheta da tela
        title_surface (pygame.Surface): Superfície com o título
        title_rect (pygame.Rect): Posição do título
        text_surfaces (list): Lista de superfícies de texto
        start_y (int): Posição Y inicial para o texto
        
    Returns:
        bool: True se a tecla foi pressionada, False se foi interrompido
    """
    prompt_text = "PRESSIONE ENTER"
    prompt_surface = game.prompt_font.render(prompt_text, True, GREY)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50))

    waiting = True
    start_time = pygame.time.get_ticks()

    # Loop de espera com animação
    while waiting:
        # Calcula a transparência do prompt com efeito de pulsação
        time_passed = pygame.time.get_ticks() - start_time
        alpha = int(100 + 155 * (0.5 + 0.5 * math.sin(time_passed / 500)))

        # Renderiza o fundo
        game.screen.fill(BLACK)
        game.screen.blit(vignette, (0, 0))
        game.screen.blit(title_surface, title_rect)

        # Renderiza o texto linha por linha
        current_y = start_y
        for surf, line in text_surfaces:
            if not line:
                current_y += 20
                continue
            rect = surf.get_rect(center=(WIDTH // 2, current_y + surf.get_height() // 2))
            game.screen.blit(surf, rect)
            current_y += surf.get_height() + 10

        # Aplica o efeito de pulsação no prompt
        temp_prompt = prompt_surface.copy()
        temp_prompt.set_alpha(alpha)
        game.screen.blit(temp_prompt, prompt_rect)

        pygame.display.flip()
        game.clock.tick(FPS)

        # Verifica eventos
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
    """Realiza um efeito de fade out em toda a tela.
    
    Cria uma transição suave para escurecer a tela,
    útil para transições entre cenas.
    
    Args:
        game: Referência ao objeto principal do jogo
        vignette (pygame.Surface): Vinheta da tela
        fade_duration (int): Duração do fade out em milissegundos
        
    Returns:
        bool: True se o fade foi concluído, False se foi interrompido
    """
    current_screen = game.screen.copy()
    start_time = pygame.time.get_ticks()
    
    # Loop de animação do fade out
    while pygame.time.get_ticks() - start_time < fade_duration:
        progress = (pygame.time.get_ticks() - start_time) / fade_duration
        alpha = int(255 * (1 - progress))

        # Aplica o fade out na tela atual
        game.screen.fill(BLACK)
        temp_screen = current_screen.copy()
        temp_screen.set_alpha(alpha)
        game.screen.blit(temp_screen, (0, 0))

        pygame.display.flip()
        game.clock.tick(FPS)

        # Verifica eventos de encerramento
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
    """Exibe a sequência de introdução do jogo.
    
    Apresenta uma sequência de cenas com texto narrativo,
    combinando efeitos visuais e sonoros para criar uma
    experiência imersiva de introdução.
    """
    # Define as cenas da introdução
    intro_scenes = [
        {
            "title": "ALÉM DA CÚPULA",
            "lines": [
                "Uma catástrofe devastou a humanidade.",
                "A cúpula é a última defesa.",
                "Uma IA governou a humanidade por séculos.",
                "Mas algo não faz sentido...",
                "Segredos dormem sob as ruínas.",
                "Verdades que podem destruir tudo que você acredita."
            ]
        }
    ]

    # Configuração dos tempos de animação
    vignette = create_vignette(WIDTH, HEIGHT)
    fade_duration = 1000
    pause_before_title = 700
    title_to_text_pause = 1000
    line_transition_duration = 850

    # Inicia a música de introdução
    intro_sound = None
    if hasattr(game, 'audio_manager'):
        game.audio_manager.play('music/intro', volume=0.7, loop=True)
        intro_sound = True

    # Processa cada cena da introdução
    for scene_index, scene in enumerate(intro_scenes):
        # Prepara a tela inicial
        game.screen.fill(BLACK)
        game.screen.blit(vignette, (0, 0))
        pygame.display.flip()

        if not wait_time(game, pause_before_title): 
            return

        # Renderiza e anima o título
        title_surface = game.intro_title_font.render(scene["title"], True, WHITE)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))

        if not fade_in_surface(game, title_surface, title_rect, fade_duration): 
            return
        if not wait_time(game, title_to_text_pause): 
            return

        # Prepara as superfícies de texto
        text_surfaces = []
        line_pause_times = []
        total_height = 0
        
        # Calcula tempos de pausa para cada linha
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

        # Anima cada linha de texto
        start_y = title_rect.bottom + 40
        current_y = start_y
        for i, (text_surf, line) in enumerate(text_surfaces):
            if text_surf is None:
                current_y += 20
                continue
            text_rect = text_surf.get_rect(center=(WIDTH // 2, current_y + text_surf.get_height() // 2))
            if not animate_text_line(game, text_surf, text_rect, line_transition_duration, keep_previous=True): 
                return
            if i < len(text_surfaces) - 1:
                if not wait_time(game, line_pause_times[i]): 
                    return
            current_y += text_surf.get_height() + 10

        # Aguarda input do jogador
        if not wait_for_keypress_with_animation(game, vignette, title_surface, title_rect, text_surfaces, start_y): 
            return

        # Finaliza a cena com fade out
        if scene_index == len(intro_scenes) - 1 and intro_sound and hasattr(game, 'audio_manager'):
            game.stop_music(fadeout_ms=1500)
            intro_sound = False

        if not fade_out_everything(game, vignette, 1200): 
            return

    # Garante que a música foi parada
    if intro_sound and hasattr(game, 'audio_manager'):
        game.stop_music(fadeout_ms=500)

    game.screen.fill(BLACK)
    pygame.display.flip()

def show_start_screen(game):
    """Exibe a tela inicial do jogo com efeitos visuais.
    
    Apresenta o título do jogo com efeitos de brilho e pulsação,
    junto com instruções para o jogador iniciar.
    """
    # Cria gradiente de fundo
    gradient_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_value = int(25 * (y / HEIGHT))
        gradient_surface.fill((0, 0, color_value), (0, y, WIDTH, 1))

    # Adiciona efeito de ondas
    t = pygame.time.get_ticks() * 0.001
    for x in range(0, WIDTH, 4):
        wave = math.sin(x * 0.01 + t) * 10
        wave_pos = int(wave) + HEIGHT // 2
        if 0 < wave_pos < HEIGHT:
            pygame.draw.line(gradient_surface, (0, 40, 80), (x, wave_pos - 2), (x + 3, wave_pos - 2), 4)
    game.screen.blit(gradient_surface, (0, 0))

    # Aplica vinheta
    vignette = create_vignette(WIDTH, HEIGHT)
    game.screen.blit(vignette, (0, 0))

    # Renderiza título com efeitos
    title_font = game.intro_title_font
    title_shadow = title_font.render(TITLE, True, (0, 0, 40))
    title_text = title_font.render(TITLE, True, (120, 180, 255))
    
    # Efeito de pulsação para o brilho
    pulse = (math.sin(pygame.time.get_ticks() * 0.002) * 0.2) + 0.8
    glow_size = 10
    glow_color = (0, 100, 200, 50)
    title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 3))
    
    # Cria efeito de brilho
    glow_surf = pygame.Surface((title_rect.width + glow_size*2, title_rect.height + glow_size*2), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, glow_color, (0, 0, title_rect.width + glow_size*2, title_rect.height + glow_size*2), border_radius=20)
    glow_rect = glow_surf.get_rect(center=title_rect.center)
    glow_surf.set_alpha(int(120 * pulse))
    game.screen.blit(glow_surf, glow_rect)

    # Renderiza título com sombra
    shadow_offset = 2
    game.screen.blit(title_shadow, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
    game.screen.blit(title_text, title_rect)

    # Adiciona linha decorativa
    line_y = title_rect.bottom + 10
    line_width = title_rect.width * 0.8
    line_height = 2
    line_rect = pygame.Rect(WIDTH/2 - line_width/2, line_y, line_width, line_height)
    pygame.draw.rect(game.screen, (80, 140, 240), line_rect, border_radius=line_height//2)

    # Renderiza instrução com efeito de pulsação
    alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.002)) * 255)
    instr_font = game.intro_font
    instr_text = instr_font.render("Pressione qualquer tecla para começar", True, (200, 200, 255))
    instr_rect = instr_text.get_rect(center=(WIDTH / 2, HEIGHT * 2 / 3))
    instr_surf = pygame.Surface((instr_text.get_width(), instr_text.get_height()), pygame.SRCALPHA)
    instr_surf.fill((255, 255, 255, 0))
    instr_surf.blit(instr_text, (0, 0))
    instr_surf.set_alpha(alpha)
    game.screen.blit(instr_surf, instr_rect)

    # Renderiza informações de controles
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
    """Exibe a tela de Game Over com efeitos visuais dramáticos.
    
    Apresenta uma sequência de animações e efeitos visuais
    para comunicar o fim do jogo, incluindo:
    - Efeito de sangue escorrendo
    - Partículas de poeira
    - Batimentos cardíacos
    - Texto pulsante
    """
    if not game.running:
        return

    # Fade para preto
    current_screen = game.screen.copy()
    for alpha in range(0, 256, 5):
        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill((0, 0, 0))
        fade.set_alpha(alpha)
        game.screen.blit(current_screen, (0, 0))
        game.screen.blit(fade, (0, 0))
        pygame.display.flip()
        game.clock.tick(60)
        
    # Cria gradiente vermelho para fundo
    gradient_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        red_value = int(40 * (1 - y / HEIGHT))
        dark_value = int(red_value * 0.2)
        gradient_surface.fill((red_value, dark_value, dark_value), (0, y, WIDTH, 1))
    
    # Inicializa efeito de sangue escorrendo
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
    
    # Inicializa partículas de poeira
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
    
    # Cria vinheta vermelha
    vignette = create_vignette(WIDTH, HEIGHT, color=(60, 0, 0))
    
    # Configura efeitos sonoros
    heartbeat_sounds = []
    heartbeat_times = []
    heartbeat_interval = 1500  # ms
    heartbeat_available = False
    if hasattr(game, 'audio_manager'):
        # Tenta reproduzir som de batimento cardíaco
        heartbeat_sound = game.audio_manager.play('heartbeat', volume=0.7)
        if heartbeat_sound:
            heartbeat_sounds.append(heartbeat_sound)
            heartbeat_times.append(pygame.time.get_ticks())
            heartbeat_available = True
        # Fallback para som de game over
        elif hasattr(game, 'audio_manager'):
            heartbeat_sound = game.audio_manager.play('game_over', volume=0.5, loop=True)
            if heartbeat_sound:
                heartbeat_sounds.append(heartbeat_sound)
                heartbeat_times.append(pygame.time.get_ticks())
                heartbeat_available = True
    
    # Prepara texto
    title_text = "GAME OVER"
    
    # Configura animação principal
    animation_time = 3000  # ms
    start_time = pygame.time.get_ticks()
    fully_rendered = False
    
    # Loop principal de animação
    while not fully_rendered:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / animation_time)
        
        # Atualiza efeito de batimentos
        if elapsed > 0 and heartbeat_available and hasattr(game, 'audio_manager'):
            last_beat = current_time - heartbeat_times[-1]
            if last_beat > heartbeat_interval:
                if not any(sound for sound in heartbeat_sounds if sound and hasattr(sound, 'get_busy') and sound.get_busy()):
                    heartbeat_sound = game.audio_manager.play('heartbeat', volume=0.7)
                    if heartbeat_sound:
                        heartbeat_sounds.append(heartbeat_sound)
                        heartbeat_times.append(current_time)
                        # Efeito visual de pulso
                        game.screen.fill((100, 0, 0))
                        pygame.display.flip()
                        pygame.time.delay(50)
        
        # Atualiza sangue escorrendo
        for streak in blood_streaks:
            streak['progress'] = min(1.0, streak['progress'] + streak['speed'] * 0.01)
        
        # Atualiza partículas
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
        
        # Renderiza fundo
        game.screen.blit(gradient_surface, (0, 0))
        
        # Renderiza sangue
        for streak in blood_streaks:
            current_length = int(streak['length'] * streak['progress'])
            if current_length > 0:
                blood_surf = pygame.Surface((streak['width'], current_length), pygame.SRCALPHA)
                for i in range(current_length):
                    alpha = max(0, streak['opacity'] - (i / current_length * streak['opacity']))
                    color = (120, 0, 0, int(alpha))
                    pygame.draw.line(blood_surf, color, (streak['width']//2, i), (streak['width']//2, i+1), streak['width'])
                game.screen.blit(blood_surf, (streak['x'] - streak['width']//2, streak['y']))
        
        # Renderiza partículas
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
        
        # Aplica vinheta
        game.screen.blit(vignette, (0, 0))
        
        # Renderiza título com animação
        if progress > 0.2:
            title_progress = min(1.0, (progress - 0.2) / 0.4)
            title_scale = 1.5 - (0.5 * title_progress)
            
            title_font = pygame.font.Font(None, int(100 * title_scale))
            if hasattr(game, 'game_over_font'):
                title_font = game.game_over_font
                
            # Efeito de distorção do texto
            title_chars = []
            total_width = 0
            for char in title_text:
                char_surf = title_font.render(char, True, (200, 0, 0))
                char_shadow = title_font.render(char, True, (60, 0, 0))
                title_chars.append((char_surf, char_shadow))
                total_width += char_surf.get_width()
            
            # Centraliza e anima caracteres
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
        
        # Renderiza causa da morte
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
        
        # Instrução para tentar novamente
        if progress > 0.9:
            instr_font = pygame.font.Font(None, 28) # Ajuste o tamanho da fonte se necessário
            if hasattr(game, 'prompt_font'):
                instr_font = game.prompt_font
                
            instr_text_surf = instr_font.render("Pressione qualquer tecla para tentar novamente", True, (220, 220, 220))
            instr_shadow_surf = instr_font.render("Pressione qualquer tecla para tentar novamente", True, (0, 0, 0))
            
            text_rect = instr_text_surf.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4 + 20)) # Posiciona abaixo de onde o botão estava
            shadow_pos = text_rect.move(2, 2)
            
            # Animação de fade in para a instrução
            instruction_progress = min(1.0, (progress - 0.9) / 0.1)
            alpha = int(255 * instruction_progress)
            instr_text_surf.set_alpha(alpha)
            instr_shadow_surf.set_alpha(alpha)

            game.screen.blit(instr_shadow_surf, shadow_pos)
            game.screen.blit(instr_text_surf, text_rect)
        
        pygame.display.flip()
        game.clock.tick(60)
        
        # Verifica eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.running = False
                    return
        
        # Finaliza animação
        if elapsed >= animation_time + 500: # Tempo um pouco menor pois não esperamos o botão aparecer totalmente
            fully_rendered = True
    
    # Para efeitos sonoros
    if hasattr(game, 'audio_manager'):
        for sound in heartbeat_sounds:
            if sound:
                game.audio_manager.stop(sound)
    
    # Aguarda input final (qualquer tecla)
    wait_for_key(game)

def wait_for_key(game, specific_key=None):
    """Aguarda pressionamento de tecla específica ou qualquer tecla.
    
    Mantém o jogo responsivo durante a espera, verificando
    eventos de encerramento e controlando o FPS.
    
    Args:
        game: Referência ao objeto principal do jogo
        specific_key (int, optional): Tecla específica para aguardar
        
    Returns:
        bool: True se a tecla foi pressionada, False se foi interrompido
    """
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