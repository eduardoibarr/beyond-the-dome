import pygame
import random
import math
from core.settings import (
    TILE_SIZE,
    TEXTURE_POINT_SIZE_MIN,
    TEXTURE_POINT_SIZE_MAX,
    TEXTURE_DARK_COLOR_THRESHOLD,
    TEXTURE_LIGHT_COLOR_THRESHOLD,
    TEXTURE_DENSITY_DEFAULT,
)

def draw_gradient_rect(surface, rect, color1, color2, vertical=True):
    """Desenha um retângulo com um gradiente vertical ou horizontal.
    
    Args:
        surface (pygame.Surface): Superfície onde desenhar
        rect (tuple): Retângulo (x, y, largura, altura)
        color1 (tuple): Cor inicial (R, G, B)
        color2 (tuple): Cor final (R, G, B)
        vertical (bool): Se True, gradiente vertical; se False, horizontal
    """
    x, y, w, h = rect
    if vertical:
        for i in range(h):
            ratio = i / h
            color = (
                int(color1[0] * (1 - ratio) + color2[0] * ratio),
                int(color1[1] * (1 - ratio) + color2[1] * ratio),
                int(color1[2] * (1 - ratio) + color2[2] * ratio)
            )
            pygame.draw.line(surface, color, (x, y + i), (x + w - 1, y + i))
    else: # Horizontal
        for i in range(w):
            ratio = i / w
            color = (
                int(color1[0] * (1 - ratio) + color2[0] * ratio),
                int(color1[1] * (1 - ratio) + color2[1] * ratio),
                int(color1[2] * (1 - ratio) + color2[2] * ratio)
            )
            pygame.draw.line(surface, color, (x + i, y), (x + i, y + h - 1))

def draw_textured_rect(surface, rect, base_color, dark_color, light_color, density=TEXTURE_DENSITY_DEFAULT, point_size=(TEXTURE_POINT_SIZE_MIN, TEXTURE_POINT_SIZE_MAX), tile_size=TILE_SIZE):
    """Desenha um retângulo com pontos de textura aleatórios.
    
    Args:
        surface (pygame.Surface): Superfície onde desenhar
        rect (tuple): Retângulo (x, y, largura, altura)
        base_color (tuple): Cor base (R, G, B)
        dark_color (tuple): Cor escura para sombras (R, G, B)
        light_color (tuple): Cor clara para destaques (R, G, B)
        density (float): Densidade dos pontos de textura
        point_size (tuple): Tamanho mínimo e máximo dos pontos
        tile_size (int): Tamanho do tile para escalar a densidade
    """
    x, y, w, h = rect
    num_points = int((w * h / (tile_size*tile_size)) * density) # Escala a densidade com a área
    for _ in range(num_points):
        px = random.randint(x, x + w - 1)
        py = random.randint(y, y + h - 1)
        psize = random.randint(point_size[0], point_size[1]) # Usa os elementos da tupla
        pcolor_choice = random.random()
        if pcolor_choice < TEXTURE_DARK_COLOR_THRESHOLD: pcolor = dark_color
        elif pcolor_choice < TEXTURE_LIGHT_COLOR_THRESHOLD: pcolor = light_color
        else: pcolor = base_color # Alguns pontos combinam com a cor base
        pygame.draw.circle(surface, pcolor, (px, py), psize)

def draw_crack(surface, start_pos, max_len, color, width=1):
    """Desenha uma linha de rachadura aleatória simples.
    
    Args:
        surface (pygame.Surface): Superfície onde desenhar
        start_pos (tuple): Posição inicial (x, y)
        max_len (float): Comprimento máximo da rachadura
        color (tuple): Cor da rachadura (R, G, B)
        width (int): Largura da linha
    """
    x, y = start_pos
    last_x, last_y = x, y
    length = 0
    angle = random.uniform(0, 2 * math.pi) # Ângulo inicial

    while length < max_len:
        # Muda o ângulo levemente
        angle += random.uniform(-0.5, 0.5)
        # Move um pequeno passo
        step = random.uniform(1, 3)
        next_x = last_x + math.cos(angle) * step
        next_y = last_y + math.sin(angle) * step

        # Limita aos limites da superfície (importante!)
        surf_rect = surface.get_rect()
        next_x = max(surf_rect.left, min(surf_rect.right - 1, next_x))
        next_y = max(surf_rect.top, min(surf_rect.bottom - 1, next_y))

        # Desenha o segmento usando inteiros
        pygame.draw.line(surface, color, (int(last_x), int(last_y)), (int(next_x), int(next_y)), width)

        last_x, last_y = next_x, next_y
        length += step

        # Para se atingir a borda
        if not surf_rect.collidepoint(last_x, last_y):
             break
        # Chance aleatória de parar cedo
        if random.random() < 0.05:
            break 