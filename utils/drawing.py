import pygame
import random
import math
from settings import (
    TEXTURE_DENSITY_DEFAULT,
    TEXTURE_POINT_SIZE_MIN,
    TEXTURE_POINT_SIZE_MAX,
    TEXTURE_DARK_COLOR_THRESHOLD,
    TEXTURE_LIGHT_COLOR_THRESHOLD,
    TILE_SIZE # Assuming TILE_SIZE is needed here from settings
)

def simple_noise(x, y, seed, scale=1.0):
    """
    Simple pseudo-random noise function.
    NOTE: For much better terrain, consider using a dedicated noise library
          like 'perlin-noise' or 'opensimplex'. This is very basic.
    Args:
        x (float): X coordinate.
        y (float): Y coordinate.
        seed (float): Seed value for randomness.
        scale (float): Controls the frequency/detail of the noise. Larger scale = larger features.
    Returns:
        float: Noise value between roughly -1.0 and 1.0.
    """
    # Combine sine and cosine functions with different frequencies and seeds
    # to create a pseudo-random but somewhat smooth pattern.
    val = (math.sin(x / scale * 0.1 + seed) * math.cos(y / scale * 0.1 + seed * 0.7) * 0.5 +
           math.sin((x + y) / scale * 0.2 + seed * 1.3) * 0.3 +
           math.sin(math.sqrt(x * x + y * y) / scale * 0.1 + seed * 2.5) * 0.2)
    # Normalize roughly to -1 to 1 range (approximation)
    return max(-1.0, min(1.0, val * 1.5)) # Adjust multiplier if needed

def draw_gradient_rect(surface, rect, color1, color2, vertical=True):
    """Draws a rectangle with a vertical or horizontal gradient."""
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
    """Draws a rectangle with random texture points."""
    x, y, w, h = rect
    num_points = int((w * h / (tile_size*tile_size)) * density) # Scale density with area
    for _ in range(num_points):
        px = random.randint(x, x + w - 1)
        py = random.randint(y, y + h - 1)
        psize = random.randint(point_size[0], point_size[1]) # Use tuple elements
        pcolor_choice = random.random()
        if pcolor_choice < TEXTURE_DARK_COLOR_THRESHOLD: pcolor = dark_color
        elif pcolor_choice < TEXTURE_LIGHT_COLOR_THRESHOLD: pcolor = light_color
        else: pcolor = base_color # Some points match base
        pygame.draw.circle(surface, pcolor, (px, py), psize)

def draw_crack(surface, start_pos, max_len, color, width=1):
    """Draws a simple randomized crack line."""
    x, y = start_pos
    last_x, last_y = x, y
    length = 0
    angle = random.uniform(0, 2 * math.pi) # Initial angle

    while length < max_len:
        # Change angle slightly
        angle += random.uniform(-0.5, 0.5)
        # Move a small step
        step = random.uniform(1, 3)
        next_x = last_x + math.cos(angle) * step
        next_y = last_y + math.sin(angle) * step

        # Clamp to surface bounds (important!)
        surf_rect = surface.get_rect()
        next_x = max(surf_rect.left, min(surf_rect.right - 1, next_x))
        next_y = max(surf_rect.top, min(surf_rect.bottom - 1, next_y))

        # Draw segment using integers
        pygame.draw.line(surface, color, (int(last_x), int(last_y)), (int(next_x), int(next_y)), width)

        last_x, last_y = next_x, next_y
        length += step

        # Stop if it hits the edge
        if not surf_rect.collidepoint(last_x, last_y):
             break
        # Random chance to stop early
        if random.random() < 0.05:
            break 