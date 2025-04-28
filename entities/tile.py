import pygame
import random
import math
from core.settings import *
from utils.drawing import draw_gradient_rect, draw_textured_rect, draw_crack

class Tile(pygame.sprite.Sprite):
    """Classe base para todos os tiles estáticos do mapa."""
    def __init__(self, game, x, y, groups, kind='floor'):
        """
        Inicializa um sprite de Tile.
        Args:
            game: Referência ao objeto principal do jogo.
            x (int): Índice da coluna do tile.
            y (int): Índice da linha do tile.
            groups (pygame.sprite.Group): Grupo(s) de sprite(s) para adicionar este tile.
            kind (str): O tipo de tile (ex: 'floor', 'grass', 'wall').
        """
        self.groups = groups
        super().__init__(self.groups) # Inicializa Sprite
        self.game = game
        self.kind = kind
        self.x = x * TILE_SIZE # Posição no mundo em pixels
        self.y = y * TILE_SIZE # Posição no mundo em pixels
        self.tile_x = x # Posição na grade
        self.tile_y = y # Posição na grade
        
        # Animation timer for water
        self.animation_timer = random.uniform(0, 2 * math.pi) # Offset animation start

        # Armazena em cache a imagem BASE gerada - gera apenas uma vez
        self.image_base = self._create_tile_image()
        # A imagem ativa é inicialmente a imagem base
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def _create_tile_image(self):
        """
        Cria a pygame.Surface para o tile com base em seu tipo e nível de detalhe.
        Retorna:
            pygame.Surface: A imagem renderizada para o tile.
        """
        # Cria uma superfície com suporte à transparência
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        width, height = TILE_SIZE, TILE_SIZE
        rect = surf.get_rect()

        # --- Tile de Grama ---
        if self.kind == 'grass':
            # Gradiente base
            draw_gradient_rect(surf, rect, GRASS_LIGHT, GRASS_COLOR)
            # Variações de textura
            draw_textured_rect(surf, rect, GRASS_COLOR, GRASS_DARK, GRASS_LIGHT, density=40, point_size=(1, 3))
            # Detalhes de folhas (Nível de Detalhe 3+)
            if DETAIL_LEVEL >= 3:
                for _ in range(10):
                    x_start = random.randint(0, width - 1)
                    y_start = random.randint(height // 2, height - 1) # Começa mais abaixo
                    leaf_len = random.randint(3, 8)
                    angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2) # Aponta principalmente para cima
                    end_x = x_start + math.cos(angle) * leaf_len
                    end_y = y_start + math.sin(angle) * leaf_len
                    # Prende aos limites
                    end_x = max(0, min(width - 1, end_x))
                    end_y = max(0, min(height - 1, end_y))
                    pygame.draw.line(surf, GRASS_LIGHT, (x_start, y_start), (int(end_x), int(end_y)), 1)

        # --- Tile de Terra ---
        elif self.kind == 'dirt':
            # Gradiente base
            draw_gradient_rect(surf, rect, DIRT_LIGHT, DIRT_COLOR)
            # Variações de textura
            draw_textured_rect(surf, rect, DIRT_COLOR, DIRT_DARK, DIRT_LIGHT, density=50, point_size=(1, 4))
            # Pedrinhas (Nível de Detalhe 3+)
            if DETAIL_LEVEL >= 3:
                for _ in range(random.randint(3, 7)):
                    x_pos = random.randint(3, width - 4)
                    y_pos = random.randint(3, height - 4)
                    size = random.randint(2, 4)
                    # Randomiza levemente a cor da pedra
                    stone_color = (max(0, min(255, 150 + random.randint(-25, 25))),
                                   max(0, min(255, 150 + random.randint(-25, 25))),
                                   max(0, min(255, 150 + random.randint(-25, 25))))
                    stone_dark = (max(0, stone_color[0]-30), max(0, stone_color[1]-30), max(0, stone_color[2]-30))
                    # Sombra simples (se habilitado)
                    if ENABLE_SHADOWS:
                         shadow_color = (*DIRT_DARK, 100) # Usa alfa para transparência
                         shadow_offset_x = 1
                         shadow_offset_y = 1
                         pygame.draw.circle(surf, shadow_color, (x_pos + shadow_offset_x, y_pos + shadow_offset_y), size)
                    # Desenha a pedra com leve gradiente/destaque
                    pygame.draw.circle(surf, stone_dark, (x_pos, y_pos), size)
                    pygame.draw.circle(surf, stone_color, (x_pos, y_pos-1), size-1) # Destaque no topo

        # --- Tile de Concreto ---
        elif self.kind == 'concrete' or self.kind == 'concrete_oil_stain':
            # Gradiente base
            draw_gradient_rect(surf, rect, CONCRETE_LIGHT, CONCRETE_COLOR)
            # Variações/Manchas
            draw_textured_rect(surf, rect, CONCRETE_COLOR, CONCRETE_DARK, CONCRETE_LIGHT, density=45, point_size=(1, 5))
            # Rachaduras (Nível de Detalhe 2+)
            if DETAIL_LEVEL >= 2:
                for _ in range(random.randint(0, 2)): # 0 a 2 rachaduras
                    start_x = random.randint(5, width - 6)
                    start_y = random.randint(5, height - 6)
                    crack_len = random.randint(width // 4, width * 2 // 3)
                    draw_crack(surf, (start_x, start_y), crack_len, CONCRETE_DARK, 1)
            # Juntas de dilatação (Nível de Detalhe 3+)
            if DETAIL_LEVEL >= 3 and random.random() < 0.15: # Menor chance
                if random.random() < 0.5: # Horizontal
                    joint_y = random.randint(height // 4, 3 * height // 4)
                    pygame.draw.line(surf, CONCRETE_DARK, (0, joint_y), (width, joint_y), 2)
                    pygame.draw.line(surf, CONCRETE_LIGHT, (0, joint_y+1), (width, joint_y+1), 1) # Destaque abaixo
                else: # Vertical
                    joint_x = random.randint(width // 4, 3 * width // 4)
                    pygame.draw.line(surf, CONCRETE_DARK, (joint_x, 0), (joint_x, height), 2)
                    pygame.draw.line(surf, CONCRETE_LIGHT, (joint_x+1, 0), (joint_x+1, height), 1) # Destaque à direita

            # Manchas de óleo (Aplicado visualmente se marcado pelo gerador)
            if self.kind == 'concrete_oil_stain':
                stain_radius = random.randint(width // 5, width // 2)
                stain_x = width // 2 + random.randint(-width//5, width//5)
                stain_y = height // 2 + random.randint(-height//5, height//5)
                # Desenha múltiplas camadas para um efeito de mancha mais profundo
                for i in range(3):
                    r_outer = stain_radius * (1.0 - i*0.2)
                    r_inner = stain_radius * (0.6 - i*0.2)
                    alpha_outer = int(OIL_STAIN_COLOR[3] * 0.6 * (1.0 - i*0.3))
                    alpha_inner = int(OIL_STAIN_COLOR[3] * (1.0 - i*0.2))

                    for r in range(int(r_outer), 0, -1):
                        if r > r_inner: # Parte externa, mais fraca
                            alpha = int(alpha_outer * ( (r - r_inner) / (r_outer - r_inner) )**0.5) # Desvanece
                        else: # Parte interna, mais escura
                            alpha = int(alpha_inner * (r / r_inner)**1.5) # Desvanece para o centro

                        alpha = max(0, min(255, alpha))
                        if alpha > 0:
                            pygame.draw.circle(surf, (*OIL_STAIN_COLOR[:3], alpha), (stain_x, stain_y), r)
        
        # --- Tile de Água ---
        elif self.kind == 'water':
            # Gradiente base
            draw_gradient_rect(surf, rect, WATER_HIGHLIGHT, WATER_COLOR)
            # Textura leve
            draw_textured_rect(surf, rect, WATER_COLOR, WATER_DARK, WATER_HIGHLIGHT, density=25, point_size=(1, 2))

        # --- Tile Padrão/Desconhecido ---
        else:
            surf.fill(RED) # Preenche com vermelho para indicar um tipo desconhecido
            pygame.draw.line(surf, WHITE, (0, 0), (width, height), 2)
            pygame.draw.line(surf, WHITE, (width, 0), (0, height), 2)
            # Tenta adicionar texto para o tipo desconhecido
            try:
                font = pygame.font.Font(None, TILE_SIZE // 2) # Fonte básica
                text_surf = font.render(f"{self.kind[:4]}?", True, WHITE)
                text_rect = text_surf.get_rect(center=rect.center)
                surf.blit(text_surf, text_rect)
            except Exception: # Ignora erros de fonte
                pass

        return surf 

    def update(self, dt):
        """Atualiza o tile, aplicando animação para tipos específicos como água."""
        if self.kind == 'water':
            # Ripple animation using sine wave based on time and position
            self.animation_timer += dt * 1.5 # Speed of animation
            
            # Calculate ripple intensity (0 to 1)
            # Add tile_x and tile_y to offset waves spatially
            ripple = (math.sin(self.animation_timer + self.tile_x * 0.5 + self.tile_y * 0.3) + 1) / 2 
            
            # Create a semi-transparent overlay
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            highlight_alpha = int(60 * ripple) # Max alpha for highlight
            dark_alpha = int(40 * (1 - ripple)) # Max alpha for dark part
            
            # Draw subtle highlights and shadows
            overlay.fill((*WATER_HIGHLIGHT[:3], highlight_alpha), special_flags=pygame.BLEND_RGBA_ADD)
            overlay.fill((*WATER_DARK[:3], dark_alpha), special_flags=pygame.BLEND_RGBA_SUB)
            
            # Blit the base image and the overlay onto the active image
            self.image = self.image_base.copy() # Start fresh from base
            self.image.blit(overlay, (0, 0))
