import pygame
import random
from core.settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

def _is_obstacle_at(game, tile_x, tile_y):
    """Verifica se existe algum sprite de obstáculo nas coordenadas de tile fornecidas.
    
    Args:
        game: Instância do jogo contendo os grupos de sprites
        tile_x (int): Coordenada X do tile a ser verificado
        tile_y (int): Coordenada Y do tile a ser verificado
        
    Returns:
        bool: True se houver um obstáculo na posição, False caso contrário
    """
    check_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    for obstacle in game.obstacles:
        if obstacle.rect.colliderect(check_rect):
            return True
    return False

def spawn_initial_enemies(game, asset_manager):
    """Gera os inimigos iniciais distribuídos pelo mapa.
    
    Esta função é responsável por criar os inimigos iniciais do jogo, incluindo:
    - Saqueadores (Raiders) distribuídos aleatoriamente
    - Matilhas de Cães Selvagens (Wild Dogs) agrupados em packs
    - Saqueador Amigável (novo) em uma posição relativamente próxima ao jogador
    
    Args:
        game: Instância do jogo onde os inimigos serão spawnados
        asset_manager: Gerenciador de assets para carregar as classes dos inimigos
    """
    print("Iniciando geração de inimigos...")

    # Obtém as classes dos inimigos do gerenciador de assets
    RaiderClass = asset_manager.get_sprite_class('raider')
    WildDogClass = asset_manager.get_sprite_class('wild_dog')
    FriendlyScavengerClass = asset_manager.get_sprite_class('friendly_scavenger')

    if not RaiderClass or not WildDogClass:
        print("ERRO: Falha ao carregar as classes de inimigos do AssetManager!")
        return

    # Calcula dimensões do mundo em tiles
    world_width_tiles = MAP_WIDTH // TILE_SIZE
    world_height_tiles = MAP_HEIGHT // TILE_SIZE
    
    # Obtém posição de spawn do jogador em tiles
    player_spawn_tile_x = game.player.rect.centerx // TILE_SIZE
    player_spawn_tile_y = game.player.rect.centery // TILE_SIZE
    
    # Define distância mínima de spawn dos inimigos em relação ao jogador
    min_spawn_dist_from_player = 20

    # Geração de Saqueadores
    num_raiders = 10
    print(f"  Gerando {num_raiders} Saqueadores...")
    for i in range(num_raiders):
        attempts = 0
        while attempts < 100:  # Limite de tentativas para encontrar posição válida
            attempts += 1
            # Gera posição aleatória dentro dos limites do mapa
            x = random.randint(5, world_width_tiles - 6)
            y = random.randint(5, world_height_tiles - 6)
            
            # Verifica distância do jogador
            dist_from_player = abs(x - player_spawn_tile_x) + abs(y - player_spawn_tile_y)
            if dist_from_player > min_spawn_dist_from_player:
                # Verifica se a posição está livre de obstáculos
                if not _is_obstacle_at(game, x, y):
                    RaiderClass(game, x * TILE_SIZE, y * TILE_SIZE)
                    break

    # Geração de matilhas de Cães Selvagens
    num_packs = 5
    dogs_per_pack_min = 2
    dogs_per_pack_max = 4
    pack_radius = 3  # Raio máximo de dispersão dos cães em uma matilha
    print(f"  Gerando {num_packs} matilhas de Cães Selvagens...")
    
    for i in range(num_packs):
        attempts = 0
        pack_placed = False
        
        while attempts < 50:  # Limite de tentativas para encontrar posição válida para a matilha
            attempts += 1
            # Gera posição central da matilha
            pack_x = random.randint(10, world_width_tiles - 11)
            pack_y = random.randint(10, world_height_tiles - 11)
            
            # Verifica distância do jogador
            dist_from_player = abs(pack_x - player_spawn_tile_x) + abs(pack_y - player_spawn_tile_y)
            if dist_from_player > min_spawn_dist_from_player + 5:
                # Verifica se a posição central está livre
                if not _is_obstacle_at(game, pack_x, pack_y):
                    # Determina tamanho da matilha
                    pack_size = random.randint(dogs_per_pack_min, dogs_per_pack_max)
                    dogs_spawned_in_pack = 0
                    
                    # Gera os cães da matilha
                    for _ in range(pack_size):
                        dog_attempts = 0
                        while dog_attempts < 20:  # Limite de tentativas para cada cão
                            dog_attempts += 1
                            # Gera posição relativa à matilha
                            dog_x = pack_x + random.randint(-pack_radius, pack_radius)
                            dog_y = pack_y + random.randint(-pack_radius, pack_radius)
                            
                            # Garante que o cão fique dentro dos limites do mapa
                            dog_x = max(1, min(world_width_tiles - 2, dog_x))
                            dog_y = max(1, min(world_height_tiles - 2, dog_y))
                            
                            # Verifica se a posição está livre
                            if not _is_obstacle_at(game, dog_x, dog_y):
                                WildDogClass(game, dog_x * TILE_SIZE, dog_y * TILE_SIZE)
                                dogs_spawned_in_pack += 1
                                break
                    pack_placed = True
                    break
    
    # Geração do Saqueador Amigável
    if FriendlyScavengerClass:
        print("  Gerando Saqueador Amigável...")
        # Queremos que o Saqueador Amigável esteja em uma distância média - nem muito longe nem muito perto
        friendly_min_dist = 10  # Mais próximo que outros inimigos
        friendly_max_dist = 20  # Não tão longe
        
        attempts = 0
        while attempts < 100:
            attempts += 1
            # Gera ângulo aleatório
            angle = random.uniform(0, 2 * 3.14159)
            # Gera distância aleatória dentro do intervalo desejado
            dist = random.randint(friendly_min_dist, friendly_max_dist)
            
            # Calcula posição baseada em coordenadas polares
            offset_x = int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            offset_y = int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            
            # Posição final
            friendly_x = player_spawn_tile_x + offset_x
            friendly_y = player_spawn_tile_y + offset_y
            
            # Garante que a posição está dentro dos limites do mapa
            friendly_x = max(1, min(world_width_tiles - 2, friendly_x))
            friendly_y = max(1, min(world_height_tiles - 2, friendly_y))
            
            # Verifica se a posição está livre de obstáculos
            if not _is_obstacle_at(game, friendly_x, friendly_y):
                FriendlyScavengerClass(game, friendly_x * TILE_SIZE, friendly_y * TILE_SIZE)
                print(f"  Saqueador Amigável gerado em ({friendly_x}, {friendly_y})")
                break
            
        if attempts >= 100:
            print("  AVISO: Não foi possível gerar o Saqueador Amigável após 100 tentativas.")
    else:
        print("  AVISO: Classe FriendlyScavenger não encontrada no AssetManager.")
    
    print("Geração de inimigos concluída com sucesso!") 
