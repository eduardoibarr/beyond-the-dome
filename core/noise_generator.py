import noise
import random
import numpy as np

class NoiseGenerator:
    def __init__(self, seed=None, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0):
        self.seed = seed if seed is not None else random.randint(0, 1000)
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity

        self.noise_cache = {}

    def get_noise_2d(self, x, y):

        cache_key = (int(x), int(y))
        if cache_key in self.noise_cache:
            return self.noise_cache[cache_key]

        value = 0
        amplitude = 1.0
        frequency = 1.0

        for _ in range(self.octaves):
            nx = x / self.scale * frequency
            ny = y / self.scale * frequency

            value += noise.pnoise2(nx, ny, octaves=1, persistence=self.persistence,
                                 lacunarity=self.lacunarity, repeatx=1024, repeaty=1024,
                                 base=self.seed) * amplitude

            amplitude *= self.persistence
            frequency *= self.lacunarity

        value = max(-1.0, min(1.0, value))

        self.noise_cache[cache_key] = value
        return value

    def get_noise_2d_array(self, width, height, x_offset=0, y_offset=0):
        noise_array = np.zeros((height, width))

        for y in range(height):
            for x in range(width):
                noise_array[y][x] = self.get_noise_2d(x + x_offset, y + y_offset)

        return noise_array

    def get_terrain_height(self, x, y, min_height=0, max_height=1):
        noise_value = self.get_noise_2d(x, y)

        return min_height + (noise_value + 1) * (max_height - min_height) / 2

    def get_terrain_type(self, x, y, thresholds):
        noise_value = self.get_noise_2d(x, y)

        terrain_type = None
        for name, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if noise_value >= threshold:
                terrain_type = name
                break

        return terrain_type if terrain_type else list(thresholds.keys())[0]
