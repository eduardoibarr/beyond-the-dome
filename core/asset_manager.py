import pygame
import os
import importlib.util
import json

class AssetManager:
    def __init__(self, sprite_dir="graphics/sprites", image_dir="graphics/images",
                sound_dir="assets/audio", music_dir="assets/audio"):

        self.stats = {
            'sprites_loaded': 0,
            'images_loaded': 0,
            'sounds_loaded': 0,
            'music_loaded': 0,
            'total_memory': 0
        }

        self.base_dirs = {
            'sprites': sprite_dir,
            'images': [image_dir, "assets/images"],
            'sounds': sound_dir,
            'music': music_dir
        }

        self.sprite_classes = {}
        self.images = {}
        self.animations = {}
        self.sounds = {}
        self.music = {}
        self.json_data = {}

        self._load_sprite_classes()
        self._load_images()
        self._load_sounds()
        self._load_music()

    def _load_sprite_classes(self):
        if not os.path.exists(self.base_dirs['sprites']):
            print(f"Aviso: Diretório de sprites '{self.base_dirs['sprites']}' não existe.")
            return

        for filename in os.listdir(self.base_dirs['sprites']):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(self.base_dirs['sprites'], filename)

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        class_name = ''.join(word.capitalize() for word in module_name.split('_'))

                        if hasattr(module, class_name):
                            self.sprite_classes[module_name] = getattr(module, class_name)
                            self.stats['sprites_loaded'] += 1
                            print(f"Sprite carregado: {class_name} de {filename}")
                        else:
                            print(f"Aviso: Classe {class_name} não encontrada em {filename}")
                    else:
                        print(f"Aviso: Não foi possível criar spec para {filename}")
                except Exception as e:
                    print(f"Erro ao carregar classe de sprite de {filename}: {e}")

    def _load_images(self):

        image_dirs = self.base_dirs['images'] if isinstance(self.base_dirs['images'], list) else [self.base_dirs['images']]

        for image_dir in image_dirs:
            if not os.path.exists(image_dir):
                print(f"Aviso: Diretório de imagens '{image_dir}' não existe.")
                continue

            for root, dirs, files in os.walk(image_dir):
                for file in files:
                    if file.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        try:
                            rel_path = os.path.relpath(os.path.join(root, file), image_dir)
                            key = os.path.splitext(rel_path)[0].replace('\\', '/')
                            full_path = os.path.join(root, file)
                            image = pygame.image.load(full_path).convert_alpha()

                            self.images[key] = image
                            self.images[os.path.basename(key)] = image
                            self.images[os.path.splitext(key)[0]] = image

                            if key.startswith('assets/images/'):
                                self.images[key.replace('assets/images/', '')] = image

                            self.stats['images_loaded'] += 1
                            self.stats['total_memory'] += image.get_width() * image.get_height() * 4
                        except Exception as e:
                            print(f"Erro ao carregar imagem {file}: {e}")

        self._setup_animations()

    def _setup_animations(self):

        image_dirs = self.base_dirs['images'] if isinstance(self.base_dirs['images'], list) else [self.base_dirs['images']]

        for image_dir in image_dirs:
            animations_dir = os.path.join(image_dir, 'animations')
            if not os.path.exists(animations_dir):
                continue

            for root, dirs, files in os.walk(animations_dir):
                for file in files:
                    if file.endswith('.json'):
                        try:
                            json_path = os.path.join(root, file)
                            sprite_name = os.path.splitext(file)[0]
                            spritesheet_path = os.path.join(root, f"{sprite_name}.png")

                            if not os.path.exists(spritesheet_path):
                                continue

                            spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

                            with open(json_path, 'r') as f:
                                animation_data = json.load(f)

                            for anim_name, frames_data in animation_data.items():
                                if anim_name not in self.animations:
                                    self.animations[anim_name] = []

                                for frame_data in frames_data:
                                    x, y, w, h = frame_data['x'], frame_data['y'], frame_data['w'], frame_data['h']
                                    frame = spritesheet.subsurface((x, y, w, h))
                                    self.animations[anim_name].append(frame)
                        except Exception as e:
                            print(f"Erro ao processar animação {file}: {e}")

    def _load_sounds(self):
        if not os.path.exists(self.base_dirs['sounds']):
            print(f"Aviso: Diretório de sons '{self.base_dirs['sounds']}' não existe.")
            return

        for root, dirs, files in os.walk(self.base_dirs['sounds']):
            for file in files:
                if file.endswith(('.wav', '.ogg', '.mp3')):
                    try:
                        rel_path = os.path.relpath(os.path.join(root, file), self.base_dirs['sounds'])
                        key = os.path.splitext(rel_path)[0].replace('\\', '/')
                        full_path = os.path.join(root, file)
                        self.sounds[key] = pygame.mixer.Sound(full_path)
                        self.stats['sounds_loaded'] += 1
                    except Exception as e:
                        print(f"Erro ao carregar som {file}: {e}")

    def _load_music(self):
        if not os.path.exists(self.base_dirs['music']):
            print(f"Aviso: Diretório de música '{self.base_dirs['music']}' não existe.")
            return

        for root, dirs, files in os.walk(self.base_dirs['music']):
            for file in files:
                if file.endswith(('.wav', '.ogg', '.mp3')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.base_dirs['music'])
                    key = os.path.splitext(rel_path)[0].replace('\\', '/')
                    full_path = os.path.join(root, file)
                    self.music[key] = full_path
                    self.stats['music_loaded'] += 1

    def get_sprite_class(self, name):
        return self.sprite_classes.get(name)

    def get_image(self, name):

        variations = [
            name,
            name.replace('assets/images/', ''),
            os.path.basename(name),
            os.path.splitext(name)[0],
            os.path.splitext(os.path.basename(name))[0]
        ]

        for variation in variations:
            if variation in self.images:
                return self.images[variation]

        print(f"Aviso: Imagem '{name}' não encontrada")
        return self._get_placeholder_image()

    def get_animation(self, name):
        if name in self.animations:
            return self.animations[name]
        print(f"Aviso: Animação '{name}' não encontrada")
        return []

    def get_sound(self, name):
        if name in self.sounds:
            return self.sounds[name]
        print(f"Aviso: Som '{name}' não encontrado")
        return None

    def play_sound(self, name, volume=1.0, loops=0):
        sound = self.get_sound(name)
        if sound:
            sound.set_volume(volume)
            return sound.play(loops)
        return None

    def play_music(self, name, volume=1.0, loops=-1, fade_ms=0):
        if name in self.music:
            try:
                if fade_ms > 0:
                    pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(self.music[name])
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                return True
            except Exception as e:
                print(f"Erro ao reproduzir música {name}: {e}")
        else:
            print(f"Aviso: Música '{name}' não encontrada")
        return False

    def _get_placeholder_image(self):

        image = pygame.Surface((64, 64), pygame.SRCALPHA)
        image.fill((160, 0, 160))
        pygame.draw.line(image, (255, 0, 0), (0, 0), (64, 64), 2)
        pygame.draw.line(image, (255, 0, 0), (0, 64), (64, 0), 2)
        return image

    def create_sprite(self, name, *args, **kwargs):
        sprite_class = self.get_sprite_class(name)
        if sprite_class:
            try:
                return sprite_class(*args, **kwargs)
            except Exception as e:
                print(f"Erro ao criar sprite {name}: {e}")
        return None

    def print_stats(self):
        print("\n=== AssetManager Stats ===")
        print(f"Sprites carregados: {self.stats['sprites_loaded']}")
        print(f"Imagens carregadas: {self.stats['images_loaded']}")
        print(f"Sons carregados: {self.stats['sounds_loaded']}")
        print(f"Músicas registradas: {self.stats['music_loaded']}")
        print(f"Uso estimado de memória: {self.stats['total_memory'] / (1024*1024):.2f} MB")
        print("=======================\n")

    def load_json(self, filename):
        if filename in self.json_data:
            return self.json_data[filename]

        try:

            paths_to_try = [
                filename,
                os.path.join("data", filename),
                os.path.join("assets", filename),
            ]

            for path in paths_to_try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        self.json_data[filename] = json.load(f)
                        return self.json_data[filename]

            print(f"Aviso: Arquivo JSON '{filename}' não encontrado")
            return {}

        except Exception as e:
            print(f"Erro ao carregar arquivo JSON {filename}: {e}")
            return {}
