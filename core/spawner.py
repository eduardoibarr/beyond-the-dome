import pygame
import random
from core.settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE

def _is_obstacle_at(game, tile_x, tile_y):
    check_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    for obstacle in game.obstacles:
        if obstacle.rect.colliderect(check_rect):
            return True
    return False

def spawn_initial_enemies(game, asset_manager):
    print("Iniciando geração de inimigos...")

    RaiderClass = asset_manager.get_sprite_class('raider')
    WildDogClass = asset_manager.get_sprite_class('wild_dog')
    FriendlyScavengerClass = asset_manager.get_sprite_class('friendly_scavenger')

    if not RaiderClass or not WildDogClass:
        print("ERRO: Falha ao carregar as classes de inimigos do AssetManager!")
        return

    world_width_tiles = MAP_WIDTH // TILE_SIZE
    world_height_tiles = MAP_HEIGHT // TILE_SIZE

    player_spawn_tile_x = game.player.rect.centerx // TILE_SIZE
    player_spawn_tile_y = game.player.rect.centery // TILE_SIZE

    min_spawn_dist_from_player = 20

    num_raiders = 10
    print(f"  Gerando {num_raiders} Saqueadores...")
    for i in range(num_raiders):
        attempts = 0
        while attempts < 100:
            attempts += 1

            x = random.randint(5, world_width_tiles - 6)
            y = random.randint(5, world_height_tiles - 6)

            dist_from_player = abs(x - player_spawn_tile_x) + abs(y - player_spawn_tile_y)
            if dist_from_player > min_spawn_dist_from_player:

                if not _is_obstacle_at(game, x, y):
                    RaiderClass(game, x * TILE_SIZE, y * TILE_SIZE)
                    break

    num_packs = 5
    dogs_per_pack_min = 2
    dogs_per_pack_max = 4
    pack_radius = 3
    print(f"  Gerando {num_packs} matilhas de Cães Selvagens...")

    for i in range(num_packs):
        attempts = 0
        pack_placed = False

        while attempts < 50:
            attempts += 1

            pack_x = random.randint(10, world_width_tiles - 11)
            pack_y = random.randint(10, world_height_tiles - 11)

            dist_from_player = abs(pack_x - player_spawn_tile_x) + abs(pack_y - player_spawn_tile_y)
            if dist_from_player > min_spawn_dist_from_player + 5:

                if not _is_obstacle_at(game, pack_x, pack_y):

                    pack_size = random.randint(dogs_per_pack_min, dogs_per_pack_max)
                    dogs_spawned_in_pack = 0

                    for _ in range(pack_size):
                        dog_attempts = 0
                        while dog_attempts < 20:
                            dog_attempts += 1

                            dog_x = pack_x + random.randint(-pack_radius, pack_radius)
                            dog_y = pack_y + random.randint(-pack_radius, pack_radius)

                            dog_x = max(1, min(world_width_tiles - 2, dog_x))
                            dog_y = max(1, min(world_height_tiles - 2, dog_y))

                            if not _is_obstacle_at(game, dog_x, dog_y):
                                WildDogClass(game, dog_x * TILE_SIZE, dog_y * TILE_SIZE)
                                dogs_spawned_in_pack += 1
                                break
                    pack_placed = True
                    break

    if FriendlyScavengerClass:
        print("  Gerando Saqueador Amigável...")

        friendly_min_dist = 10
        friendly_max_dist = 20

        attempts = 0
        while attempts < 100:
            attempts += 1

            angle = random.uniform(0, 2 * 3.14159)

            dist = random.randint(friendly_min_dist, friendly_max_dist)

            offset_x = int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            offset_y = int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)

            friendly_x = player_spawn_tile_x + offset_x
            friendly_y = player_spawn_tile_y + offset_y

            friendly_x = max(1, min(world_width_tiles - 2, friendly_x))
            friendly_y = max(1, min(world_height_tiles - 2, friendly_y))

            if not _is_obstacle_at(game, friendly_x, friendly_y):
                FriendlyScavengerClass(game, friendly_x * TILE_SIZE, friendly_y * TILE_SIZE)
                print(f"  Saqueador Amigável gerado em ({friendly_x}, {friendly_y})")
                break

        if attempts >= 100:
            print("  AVISO: Não foi possível gerar o Saqueador Amigável após 100 tentativas.")
    else:
        print("  AVISO: Classe FriendlyScavenger não encontrada no AssetManager.")

    print("Geração de inimigos concluída com sucesso!")
