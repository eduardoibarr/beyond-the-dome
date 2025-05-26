import pygame

class Spritesheet:
    def __init__(self, filename):

        try:
            self.sheet = pygame.image.load(filename)
        except pygame.error as e:
            print(f"Não foi possível carregar a folha de sprites: {filename}")
            print(e)
            raise SystemExit(e)

    def get_image(self, x, y, width, height, scale=1, colorkey=None):

        image = pygame.Surface((width, height), pygame.SRCALPHA)

        image.blit(self.sheet, (0, 0), (x, y, width, height))

        if scale != 1:
            image = pygame.transform.scale(image,
                                          (int(width * scale), int(height * scale)))

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        return image

    def load_strip(self, rect, image_count, colorkey=None):

        frames = []
        x, y, width, height = rect

        for i in range(image_count):
            frames.append(self.get_image(x + i * width, y, width, height, colorkey=colorkey))

        return frames

    def load_grid(self, rect, cols, rows, colorkey=None):

        frames = []
        x, y, width, height = rect

        for row in range(rows):
            for col in range(cols):
                frames.append(self.get_image(
                    x + col * width,
                    y + row * height,
                    width, height,
                    colorkey=colorkey
                ))

        return frames
