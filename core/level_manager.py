"""
Módulo que integra os componentes do nível do jogo.
Este arquivo serve como ponto de entrada para o sistema de níveis,
importando e instanciando os módulos necessários.
"""

# Use relative import for settings within the same package
from .settings import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, # Tile size and map dimensions
    # Add other constants you need from settings
)

# Import from other packages using absolute paths from the project root
from graphics.camera import Camera
from level.generator import LevelGenerator
from entities.tile import Tile
from entities.obstacle import Obstacle, Water
from entities.radioactive_zone import RadioactiveZone

def create_level(game):
    """
    Função wrapper que cria e retorna um novo nível.
    
    Args:
        game: Referência ao objeto principal do jogo
        
    Returns:
        tuple: As coordenadas de spawn do jogador (x, y)
    """
    # Directly use the LevelGenerator from the level package
    generator = LevelGenerator(game)
    return generator.create_level()

