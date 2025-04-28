from level.generator import LevelGenerator

def create_level(game):
    """
    Função wrapper que cria e retorna um novo nível.
    
    Args:
        game: Referência ao objeto principal do jogo
        
    Returns:
        tuple: As coordenadas de spawn do jogador (x, y)
    """
    generator = LevelGenerator(game)
    return generator.create_level()

