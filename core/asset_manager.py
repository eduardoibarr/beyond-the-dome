import pygame
import os
import importlib.util
import json

class AssetManager:
    """Gerenciador central de recursos do jogo, responsável por carregar e gerenciar sprites, imagens, sons e músicas."""
    def __init__(self, sprite_dir="graphics/sprites", image_dir="graphics/images", 
                sound_dir="assets/audio", music_dir="assets/audio"):
        # Inicializa contador para estatísticas PRIMEIRO
        self.stats = {
            'sprites_loaded': 0,    # Contador de sprites carregados
            'images_loaded': 0,     # Contador de imagens carregadas
            'sounds_loaded': 0,     # Contador de sons carregados
            'music_loaded': 0,      # Contador de músicas carregadas
            'total_memory': 0       # Estimativa aproximada de uso de memória
        }
        
        # Diretórios base para diferentes tipos de recursos
        self.base_dirs = {
            'sprites': sprite_dir,  # Diretório para classes de sprites
            'images': image_dir,    # Diretório para imagens estáticas
            'sounds': sound_dir,    # Diretório para efeitos sonoros
            'music': music_dir      # Diretório para arquivos de música
        }
        
        # Caches para diferentes tipos de recursos
        self.sprite_classes = {}    # Cache de classes de sprites
        self.images = {}           # Cache de imagens estáticas
        self.animations = {}       # Cache de sequências de animação
        self.sounds = {}           # Cache de efeitos sonoros
        self.music = {}            # Cache de arquivos de música
        self.json_data = {}        # Cache de dados JSON
        
        # Carrega todos os recursos
        self._load_sprite_classes()  # Carrega classes de sprites
        self._load_images()          # Carrega imagens estáticas
        self._load_sounds()          # Carrega efeitos sonoros
        self._load_music()           # Carrega arquivos de música
        
    def _load_sprite_classes(self):
        """Carrega todas as classes de sprites dos arquivos .py no diretório de sprites.
        Cada arquivo deve conter uma classe com o mesmo nome do arquivo (em CamelCase).
        """
        if not os.path.exists(self.base_dirs['sprites']):
            print(f"Aviso: Diretório de sprites '{self.base_dirs['sprites']}' não existe.")
            return
            
        for filename in os.listdir(self.base_dirs['sprites']):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]  # remove .py
                file_path = os.path.join(self.base_dirs['sprites'], filename)

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Procura por classes no módulo - assume que o nome da classe
                        # segue a convenção CamelCase do nome do arquivo
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
        """Carrega todas as imagens do diretório de imagens.
        Suporta formatos: PNG, JPG, JPEG, BMP.
        """
        if not os.path.exists(self.base_dirs['images']):
            print(f"Aviso: Diretório de imagens '{self.base_dirs['images']}' não existe.")
            return
            
        # Carrega imagens individuais
        for root, dirs, files in os.walk(self.base_dirs['images']):
            for file in files:
                if file.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    try:
                        rel_path = os.path.relpath(os.path.join(root, file), self.base_dirs['images'])
                        key = os.path.splitext(rel_path)[0].replace('\\', '/') # Normaliza caminhos para uso como chaves
                        full_path = os.path.join(root, file)
                        self.images[key] = pygame.image.load(full_path).convert_alpha()
                        self.stats['images_loaded'] += 1
                        self.stats['total_memory'] += self.images[key].get_width() * self.images[key].get_height() * 4 # Estimativa
                    except Exception as e:
                        print(f"Erro ao carregar imagem {file}: {e}")
                        
        # Carrega spritesheet e prepara animações
        self._setup_animations()

    def _setup_animations(self):
        """Configura dicionários de animação a partir de spritesheets e arquivos de metadados.
        Cada animação é definida por um arquivo JSON que especifica os frames no spritesheet.
        """
        animations_dir = os.path.join(self.base_dirs['images'], 'animations')
        if not os.path.exists(animations_dir):
            return
            
        # Procura por spritesheets e seus metadados
        for root, dirs, files in os.walk(animations_dir):
            for file in files:
                if file.endswith('.json'):
                    try:
                        json_path = os.path.join(root, file)
                        sprite_name = os.path.splitext(file)[0]
                        spritesheet_path = os.path.join(root, f"{sprite_name}.png")
                        
                        if not os.path.exists(spritesheet_path):
                            continue
                            
                        # Carrega spritesheet
                        spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
                        
                        # Carrega dados JSON
                        with open(json_path, 'r') as f:
                            animation_data = json.load(f)
                            
                        # Cria frames para cada animação
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
        """Carrega todos os efeitos sonoros do diretório de sons.
        Suporta formatos: WAV, OGG, MP3.
        """
        if not os.path.exists(self.base_dirs['sounds']):
            print(f"Aviso: Diretório de sons '{self.base_dirs['sounds']}' não existe.")
            return
            
        for root, dirs, files in os.walk(self.base_dirs['sounds']):
            for file in files:
                if file.endswith(('.wav', '.ogg', '.mp3')):
                    try:
                        rel_path = os.path.relpath(os.path.join(root, file), self.base_dirs['sounds'])
                        key = os.path.splitext(rel_path)[0].replace('\\', '/') # Normaliza caminhos
                        full_path = os.path.join(root, file)
                        self.sounds[key] = pygame.mixer.Sound(full_path)
                        self.stats['sounds_loaded'] += 1
                    except Exception as e:
                        print(f"Erro ao carregar som {file}: {e}")

    def _load_music(self):
        """Registra caminhos para arquivos de música (não carrega na memória).
        Suporta formatos: WAV, OGG, MP3.
        """
        if not os.path.exists(self.base_dirs['music']):
            print(f"Aviso: Diretório de música '{self.base_dirs['music']}' não existe.")
            return
            
        for root, dirs, files in os.walk(self.base_dirs['music']):
            for file in files:
                if file.endswith(('.wav', '.ogg', '.mp3')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.base_dirs['music'])
                    key = os.path.splitext(rel_path)[0].replace('\\', '/') # Normaliza caminhos
                    full_path = os.path.join(root, file)
                    self.music[key] = full_path
                    self.stats['music_loaded'] += 1

    def get_sprite_class(self, name):
        """Retorna uma classe de sprite pelo nome.
        Args:
            name (str): Nome da classe de sprite a ser recuperada.
        Returns:
            class: A classe de sprite solicitada ou None se não encontrada.
        """
        return self.sprite_classes.get(name)

    def get_image(self, name):
        """Retorna uma imagem pelo nome.
        Args:
            name (str): Nome da imagem a ser recuperada.
        Returns:
            pygame.Surface: A imagem solicitada ou uma imagem placeholder se não encontrada.
        """
        if name in self.images:
            return self.images[name]
        print(f"Aviso: Imagem '{name}' não encontrada")
        return self._get_placeholder_image()

    def get_animation(self, name):
        """Retorna uma lista de frames de animação pelo nome.
        Args:
            name (str): Nome da animação a ser recuperada.
        Returns:
            list: Lista de frames da animação ou lista vazia se não encontrada.
        """
        if name in self.animations:
            return self.animations[name]
        print(f"Aviso: Animação '{name}' não encontrada")
        return []

    def get_sound(self, name):
        """Retorna um efeito sonoro pelo nome.
        Args:
            name (str): Nome do efeito sonoro a ser recuperado.
        Returns:
            pygame.mixer.Sound: O efeito sonoro solicitado ou None se não encontrado.
        """
        if name in self.sounds:
            return self.sounds[name]
        print(f"Aviso: Som '{name}' não encontrado")
        return None

    def play_sound(self, name, volume=1.0, loops=0):
        """Reproduz um efeito sonoro pelo nome.
        Args:
            name (str): Nome do efeito sonoro a ser reproduzido.
            volume (float): Volume do som (0.0 a 1.0).
            loops (int): Número de repetições (-1 para loop infinito).
        Returns:
            pygame.mixer.Channel: Canal de áudio onde o som está sendo reproduzido.
        """
        sound = self.get_sound(name)
        if sound:
            sound.set_volume(volume)
            return sound.play(loops)
        return None

    def play_music(self, name, volume=1.0, loops=-1, fade_ms=0):
        """Reproduz um arquivo de música pelo nome.
        Args:
            name (str): Nome do arquivo de música a ser reproduzido.
            volume (float): Volume da música (0.0 a 1.0).
            loops (int): Número de repetições (-1 para loop infinito).
            fade_ms (int): Tempo de fade in/out em milissegundos.
        Returns:
            bool: True se a música foi reproduzida com sucesso, False caso contrário.
        """
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
        """Retorna uma imagem placeholder para recursos ausentes.
        Returns:
            pygame.Surface: Uma superfície roxa com um X vermelho.
        """
        # Cria uma superfície roxa com um X vermelho
        image = pygame.Surface((64, 64), pygame.SRCALPHA)
        image.fill((160, 0, 160))
        pygame.draw.line(image, (255, 0, 0), (0, 0), (64, 64), 2)
        pygame.draw.line(image, (255, 0, 0), (0, 64), (64, 0), 2)
        return image

    def create_sprite(self, name, *args, **kwargs):
        """Cria uma instância de um sprite pelo nome.
        Args:
            name (str): Nome da classe de sprite a ser instanciada.
            *args: Argumentos posicionais para o construtor do sprite.
            **kwargs: Argumentos nomeados para o construtor do sprite.
        Returns:
            Sprite: Uma instância do sprite solicitado ou None se não encontrado.
        """
        sprite_class = self.get_sprite_class(name)
        if sprite_class:
            try:
                return sprite_class(*args, **kwargs)
            except Exception as e:
                print(f"Erro ao criar sprite {name}: {e}")
        return None

    def print_stats(self):
        """Imprime estatísticas sobre os recursos carregados.
        Mostra quantidade de sprites, imagens, sons e músicas carregados,
        além do uso estimado de memória.
        """
        print("\n=== AssetManager Stats ===")
        print(f"Sprites carregados: {self.stats['sprites_loaded']}")
        print(f"Imagens carregadas: {self.stats['images_loaded']}")
        print(f"Sons carregados: {self.stats['sounds_loaded']}")
        print(f"Músicas registradas: {self.stats['music_loaded']}")
        print(f"Uso estimado de memória: {self.stats['total_memory'] / (1024*1024):.2f} MB")
        print("=======================\n")
        
    def load_json(self, filename):
        """Carrega dados de um arquivo JSON.
        Args:
            filename (str): Nome do arquivo JSON a ser carregado.
        Returns:
            dict: Dados carregados do arquivo JSON ou dicionário vazio se não encontrado.
        """
        if filename in self.json_data:
            return self.json_data[filename]
            
        try:
            # Tenta várias localizações possíveis
            paths_to_try = [
                filename,  # caminho absoluto
                os.path.join("data", filename),  # na pasta data
                os.path.join("assets", filename),  # na pasta assets
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