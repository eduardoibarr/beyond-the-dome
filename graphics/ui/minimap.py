import pygame
import math
from core.settings import (
    WIDTH, HEIGHT, WHITE, BLACK, GREEN, RED, YELLOW, BLUE, CYAN, 
    TILE_SIZE, LIGHTGREY, DARKGREY,
    MINIMAP_SIZE, MINIMAP_MARGIN, MINIMAP_TRANSPARENCY, MINIMAP_FOG_OF_WAR,
    MINIMAP_EXPLORATION_RADIUS, MINIMAP_BACKGROUND, MINIMAP_BORDER,
    MINIMAP_PLAYER, MINIMAP_ENEMIES, MINIMAP_ITEMS, MINIMAP_OBSTACLES,
    MINIMAP_RADIOACTIVE, MINIMAP_VIEWPORT
)

class MiniMap:
    def __init__(self, game, size=None, position=None):
        """
        Inicializa o mini mapa.
        
        Args:
            game: Instância do jogo principal
            size: Tamanho do mini mapa em pixels (quadrado)
            position: Posição no canto da tela (None para canto superior direito)
        """
        self.game = game
        self.size = size or MINIMAP_SIZE
        self.margin = MINIMAP_MARGIN
        
        # Posição padrão no canto superior direito
        if position is None:
            self.position = (WIDTH - self.size - self.margin, self.margin)
        else:
            self.position = position
            
        # Surface para desenhar o mini mapa
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.set_alpha(MINIMAP_TRANSPARENCY)  # Transparência
        
        # Configurações de escala
        self.world_width = game.map_width
        self.world_height = game.map_height
        self.scale_x = self.size / self.world_width
        self.scale_y = self.size / self.world_height
        
        # Use a menor escala para manter proporção
        self.scale = min(self.scale_x, self.scale_y)
        
        # Cores para diferentes elementos
        self.colors = {
            'background': MINIMAP_BACKGROUND,
            'border': MINIMAP_BORDER,
            'player': MINIMAP_PLAYER,
            'enemies': MINIMAP_ENEMIES,
            'items': MINIMAP_ITEMS,
            'obstacles': MINIMAP_OBSTACLES,
            'radioactive_zones': MINIMAP_RADIOACTIVE,
            'fog_of_war': (0, 0, 0, 150),
            'explored': (40, 40, 40),
            'viewport': MINIMAP_VIEWPORT
        }
        
        # Sistema de fog of war (opcional)
        self.fog_of_war_enabled = MINIMAP_FOG_OF_WAR
        self.explored_areas = set()
        self.exploration_radius = MINIMAP_EXPLORATION_RADIUS  # Raio em pixels do mundo
        
    def world_to_minimap(self, world_x, world_y):
        """Converte coordenadas do mundo para coordenadas do mini mapa."""
        minimap_x = world_x * self.scale
        minimap_y = world_y * self.scale
        return int(minimap_x), int(minimap_y)
        
    def update_exploration(self):
        """Atualiza as áreas exploradas baseadas na posição do jogador."""
        if not self.fog_of_war_enabled or not self.game.player:
            return
            
        player_x = self.game.player.rect.centerx
        player_y = self.game.player.rect.centery
        
        # Adiciona área ao redor do jogador como explorada
        for dx in range(-self.exploration_radius, self.exploration_radius, 20):
            for dy in range(-self.exploration_radius, self.exploration_radius, 20):
                if dx*dx + dy*dy <= self.exploration_radius*self.exploration_radius:
                    explored_x = (player_x + dx) // 40  # Grid de exploração
                    explored_y = (player_y + dy) // 40
                    self.explored_areas.add((explored_x, explored_y))
    
    def draw_fog_of_war(self):
        """Desenha o fog of war no mini mapa."""
        if not self.fog_of_war_enabled:
            return
            
        fog_surface = pygame.Surface((self.size, self.size))
        fog_surface.set_alpha(150)
        fog_surface.fill(BLACK)
        
        # Remove fog das áreas exploradas
        for explored_x, explored_y in self.explored_areas:
            world_x = explored_x * 40
            world_y = explored_y * 40
            minimap_x, minimap_y = self.world_to_minimap(world_x, world_y)
            
            if 0 <= minimap_x < self.size and 0 <= minimap_y < self.size:
                pygame.draw.circle(fog_surface, (0, 0, 0, 0), 
                                 (minimap_x, minimap_y), 8, 0)
        
        self.surface.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    
    def draw_viewport_indicator(self):
        """Desenha um retângulo mostrando a área visível na tela principal."""
        if not self.game.camera:
            return
            
        # Calcula a área visível da câmera
        camera_x = -self.game.camera.camera.x
        camera_y = -self.game.camera.camera.y
        
        # Converte para coordenadas do mini mapa
        view_x, view_y = self.world_to_minimap(camera_x, camera_y)
        view_w = int(WIDTH * self.scale)
        view_h = int(HEIGHT * self.scale)
        
        # Desenha retângulo do viewport
        if (0 <= view_x < self.size and 0 <= view_y < self.size):
            viewport_rect = pygame.Rect(view_x, view_y, view_w, view_h)
            viewport_rect.clamp_ip(pygame.Rect(0, 0, self.size, self.size))
            pygame.draw.rect(self.surface, self.colors['viewport'], viewport_rect, 2)
    
    def draw_entities(self):
        """Desenha as entidades do jogo no mini mapa."""
        # Desenha jogador
        if self.game.player:
            player_x, player_y = self.world_to_minimap(
                self.game.player.rect.centerx, 
                self.game.player.rect.centery
            )
            if 0 <= player_x < self.size and 0 <= player_y < self.size:
                pygame.draw.circle(self.surface, self.colors['player'], 
                                 (player_x, player_y), 4)
                # Desenha direção do jogador
                if hasattr(self.game.player, 'direction'):
                    angle = math.atan2(self.game.player.direction.y, self.game.player.direction.x)
                    end_x = player_x + math.cos(angle) * 8
                    end_y = player_y + math.sin(angle) * 8
                    pygame.draw.line(self.surface, self.colors['player'], 
                                   (player_x, player_y), (int(end_x), int(end_y)), 2)
        
        # Desenha inimigos
        if self.game.enemies:
            for enemy in self.game.enemies:
                enemy_x, enemy_y = self.world_to_minimap(
                    enemy.rect.centerx, 
                    enemy.rect.centery
                )
                if 0 <= enemy_x < self.size and 0 <= enemy_y < self.size:
                    # Verifica se o inimigo está em área explorada
                    if not self.fog_of_war_enabled or self.is_area_explored(enemy.rect.centerx, enemy.rect.centery):
                        pygame.draw.circle(self.surface, self.colors['enemies'], 
                                         (enemy_x, enemy_y), 2)
        
        # Desenha itens
        if self.game.items:
            for item in self.game.items:
                item_x, item_y = self.world_to_minimap(
                    item.rect.centerx, 
                    item.rect.centery
                )
                if 0 <= item_x < self.size and 0 <= item_y < self.size:
                    if not self.fog_of_war_enabled or self.is_area_explored(item.rect.centerx, item.rect.centery):
                        pygame.draw.circle(self.surface, self.colors['items'], 
                                         (item_x, item_y), 2)
        
        # Desenha obstáculos (pontos principais)
        if self.game.obstacles:
            for obstacle in self.game.obstacles:
                if hasattr(obstacle, 'rect'):
                    obs_x, obs_y = self.world_to_minimap(
                        obstacle.rect.centerx, 
                        obstacle.rect.centery
                    )
                    if 0 <= obs_x < self.size and 0 <= obs_y < self.size:
                        pygame.draw.circle(self.surface, self.colors['obstacles'], 
                                         (obs_x, obs_y), 1)
        
        # Desenha zonas radioativas
        if self.game.radioactive_zones:
            for zone in self.game.radioactive_zones:
                zone_x, zone_y = self.world_to_minimap(
                    zone.rect.centerx, 
                    zone.rect.centery
                )
                if 0 <= zone_x < self.size and 0 <= zone_y < self.size:
                    if not self.fog_of_war_enabled or self.is_area_explored(zone.rect.centerx, zone.rect.centery):
                        zone_w = max(3, int(zone.rect.width * self.scale))
                        zone_h = max(3, int(zone.rect.height * self.scale))
                        pygame.draw.ellipse(self.surface, self.colors['radioactive_zones'], 
                                          (zone_x - zone_w//2, zone_y - zone_h//2, zone_w, zone_h))
    
    def is_area_explored(self, world_x, world_y):
        """Verifica se uma área do mundo foi explorada."""
        if not self.fog_of_war_enabled:
            return True
        explored_x = world_x // 40
        explored_y = world_y // 40
        return (explored_x, explored_y) in self.explored_areas
    
    def draw_border_and_background(self):
        """Desenha o fundo e borda do mini mapa."""
        # Fundo
        self.surface.fill(self.colors['background'])
        
        # Borda
        pygame.draw.rect(self.surface, self.colors['border'], 
                        (0, 0, self.size, self.size), 2)
    
    def draw(self, screen):
        """Desenha o mini mapa na tela principal."""
        # Limpa a surface
        self.draw_border_and_background()
        
        # Atualiza exploração
        self.update_exploration()
        
        # Desenha entidades
        self.draw_entities()
        
        # Desenha viewport
        self.draw_viewport_indicator()
        
        # Aplica fog of war
        self.draw_fog_of_war()
        
        # Desenha na tela principal
        screen.blit(self.surface, self.position)
    
    def toggle_fog_of_war(self):
        """Alterna o fog of war on/off."""
        self.fog_of_war_enabled = not self.fog_of_war_enabled
    
    def handle_click(self, mouse_pos):
        """
        Permite clique no mini mapa para mover a câmera.
        
        Args:
            mouse_pos: Posição do mouse na tela
            
        Returns:
            True se o clique foi no mini mapa, False caso contrário
        """
        minimap_rect = pygame.Rect(self.position[0], self.position[1], self.size, self.size)
        
        if minimap_rect.collidepoint(mouse_pos):
            # Converte posição do clique para coordenadas do mundo
            local_x = mouse_pos[0] - self.position[0]
            local_y = mouse_pos[1] - self.position[1]
            
            world_x = local_x / self.scale
            world_y = local_y / self.scale
            
            # Move a câmera para essa posição (opcional)
            if self.game.camera:
                self.game.camera.x = -(world_x - WIDTH // 2)
                self.game.camera.y = -(world_y - HEIGHT // 2)
                
                # Aplica limites da câmera
                self.game.camera.x = min(0.0, self.game.camera.x)
                self.game.camera.y = min(0.0, self.game.camera.y)
                self.game.camera.x = max(-(self.game.map_width - WIDTH), self.game.camera.x)
                self.game.camera.y = max(-(self.game.map_height - HEIGHT), self.game.camera.y)
            
            return True
        
        return False
