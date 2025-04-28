import pygame
import random
import math
from core.settings import *
from entities.tile import Tile
from utils.drawing import draw_gradient_rect

class RadioactiveZone(Tile):
    """
    Classe para tiles representando zonas radioativas.
    Herda de Tile. O jogador sofre dano de radiação enquanto estiver dentro.
    Adiciona-se ao grupo de zonas radioativas do jogo.
    """
    def __init__(self, game, x, y, groups):
        """
        Inicializa um tile de RadioactiveZone.
        Args:
            game: Referência ao objeto principal do jogo.
            x (int): Índice da coluna do tile.
            y (int): Índice da linha do tile.
            groups (pygame.sprite.Group): Grupo(s) de sprite(s) para adicionar este tile.
        """
        super().__init__(game, x, y, groups, 'radioactive')
        # Adiciona este sprite ao grupo de zonas radioativas do jogo
        if hasattr(game, 'radioactive_zones') and isinstance(game.radioactive_zones, pygame.sprite.Group):
            game.radioactive_zones.add(self)
        else:
            print(f"Aviso: Objeto do jogo faltando ou com grupo 'radioactive_zones' inválido ao criar RadioactiveZone em ({x},{y})")
        
        # Registrar nos sistemas de partículas (sistema antigo e novo sistema de névoa)
        if hasattr(game, 'particle_systems'):
            # Registrar no sistema antigo de partículas
            if hasattr(game.particle_systems, 'radioactive'):
                game.particle_systems.radioactive.register_zone(self)
                # Criar algumas partículas iniciais nesta zona (menos que antes)
                game.particle_systems.radioactive.add_particles(
                    self.rect.centerx, self.rect.centery, count=3, parent_zone=self
                )
            
            # Registrar no NOVO sistema de névoa radioativa
            if hasattr(game.particle_systems, 'radioactive_fog'):
                game.particle_systems.radioactive_fog.register_zone(self)
                # Adicionar névoa inicial nesta zona
                game.particle_systems.radioactive_fog.add_fog_clouds(
                    self.rect.centerx, self.rect.centery, 
                    count=4,               # Número de nuvens iniciais 
                    radius=TILE_SIZE*0.8,  # Raio da área de distribuição
                    parent_zone=self
                )
    
    def _create_tile_image(self):
        """
        Sobrescreve o método da classe base para criar uma imagem para a zona radioativa.
        Agora possui um visual mais simples já que a névoa será renderizada separadamente 
        pelo sistema de névoa radioativa.
        
        Retorna:
            pygame.Surface: A imagem renderizada para a zona radioativa.
        """
        # Criar superfície com transparência
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base com gradiente mais transparente
        base_color_with_alpha = (*RADIOACTIVE_BASE, 40)  # Verde escuro com mais transparência
        light_color_with_alpha = (*RADIOACTIVE_BASE_LIGHT, 70)  # Verde mais claro com transparência
        
        # Retângulo base com gradiente
        rect = surf.get_rect()
        draw_gradient_rect(surf, rect, light_color_with_alpha, base_color_with_alpha)
        
        # Adicionar símbolo de radioativo
        symbol_radius = TILE_SIZE // 3
        symbol_center = (TILE_SIZE // 2, TILE_SIZE // 2)
        
        # Desenhar o símbolo radioativo (três pás)
        for angle in range(0, 360, 120):
            rad_angle = math.radians(angle)
            end_x = symbol_center[0] + math.cos(rad_angle) * symbol_radius
            end_y = symbol_center[1] + math.sin(rad_angle) * symbol_radius
            pygame.draw.line(surf, RADIOACTIVE_SYMBOL, symbol_center, (end_x, end_y), 2)
        
        # Desenhar o círculo central
        pygame.draw.circle(surf, RADIOACTIVE_SYMBOL, symbol_center, symbol_radius // 3)
        
        # Removemos a névoa daqui, já que será renderizada pelo sistema de névoa
        
        return surf
    
    def update(self, dt):
        """
        Atualiza a zona radioativa. Aplica efeito de radiação ao jogador se houver sobreposição.
        Args:
            dt (float): Delta time em segundos.
        """
        # Opcional: Verificar sobreposição com o jogador para aplicar dano de radiação
        if hasattr(self.game, 'player') and self.rect.colliderect(self.game.player.rect):
            # Implementação de dano por radiação pode ser adicionada aqui
            pass
            
    def kill(self):
        """Remove a zona radioativa e desregistra do sistema de partículas."""
        # Desregistrar dos sistemas de partículas antes de remover
        if hasattr(self.game, 'particle_systems'):
            # Desregistrar do sistema antigo
            if hasattr(self.game.particle_systems, 'radioactive'):
                self.game.particle_systems.radioactive.unregister_zone(self)
            
            # Desregistrar do novo sistema de névoa
            if hasattr(self.game.particle_systems, 'radioactive_fog'):
                self.game.particle_systems.radioactive_fog.unregister_zone(self)
                
        super().kill()  # Chamar o método kill da classe base
