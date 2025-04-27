import pygame
import random
from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from sprites import Raider, WildDog # Assuming these are needed

def _is_obstacle_at(game, tile_x, tile_y):
    """Checks if any obstacle sprite exists at the given tile coordinates."""
    check_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    for obstacle in game.obstacles:
        if obstacle.rect.colliderect(check_rect):
            return True
    return False

def spawn_initial_enemies(game):
    """Spawns initial enemies across the map."""
    print("Spawning enemies...")
    world_width_tiles = MAP_WIDTH // TILE_SIZE
    world_height_tiles = MAP_HEIGHT // TILE_SIZE
    player_spawn_tile_x = game.player.rect.centerx // TILE_SIZE
    player_spawn_tile_y = game.player.rect.centery // TILE_SIZE
    min_spawn_dist_from_player = 20

    # Spawn Raiders
    num_raiders = 10
    print(f"  Spawning {num_raiders} Raiders...")
    for i in range(num_raiders):
        attempts = 0
        while attempts < 100:
            attempts += 1
            x = random.randint(5, world_width_tiles - 6)
            y = random.randint(5, world_height_tiles - 6)
            dist_from_player = abs(x - player_spawn_tile_x) + abs(y - player_spawn_tile_y)
            if dist_from_player > min_spawn_dist_from_player:
                if not _is_obstacle_at(game, x, y):
                    Raider(game, x * TILE_SIZE, y * TILE_SIZE)
                    break

    # Spawn Wild Dog packs
    num_packs = 5
    dogs_per_pack_min = 2
    dogs_per_pack_max = 4
    pack_radius = 3
    print(f"  Spawning {num_packs} Wild Dog packs...")
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
                                WildDog(game, dog_x * TILE_SIZE, dog_y * TILE_SIZE)
                                dogs_spawned_in_pack += 1
                                break
                    pack_placed = True
                    break
    print("Enemy spawning complete.") 