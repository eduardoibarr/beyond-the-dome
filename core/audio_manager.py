import pygame
import os
import threading

class AudioManager:
    """Gerenciador central de áudio do jogo, responsável por controlar a reprodução de sons e músicas.
    Pode trabalhar de forma independente ou em conjunto com o AssetManager.
    """
    def __init__(self, asset_manager=None):
        """Inicializa o gerenciador de áudio.
        Args:
            asset_manager (AssetManager, optional): Referência ao AssetManager para carregar recursos.
        """
        # A inicialização básica do mixer já é feita na Game.__init__
        self.asset_manager = asset_manager
        self.playing_sounds = {}  # Mantém referência aos sons atualmente em reprodução
        
        # Carrega sons diretamente apenas se não tiver AssetManager
        if not self.asset_manager:
            self.audio = {}
            self.load_audio()
        else:
            # Já usará os sons do AssetManager
            self.audio = None

    def load_audio(self):
        """Carrega os recursos de áudio do jogo (quando não usa AssetManager).
        Carrega sons e músicas do diretório assets/audio.
        """
        # Verifica se o diretório de áudio existe
        base_dir = os.path.dirname(os.path.dirname(__file__)) # Raiz do projeto
        audio_dir = os.path.join(base_dir, 'assets', 'audio') # Caminho atualizado para assets/audio
        if not os.path.exists(audio_dir):
            print(f"Diretório de áudio não encontrado: {audio_dir}")
            return

        # Mapeamento de chaves para nomes de arquivos
        sounds_to_load = {
            'music/intro': 'intro.mp3',          # Música de introdução
            'beretta-m9': 'beretta-m9.mp3',      # Som da arma
        }

        for key, filename in sounds_to_load.items():
            path = os.path.join(audio_dir, filename)
            if os.path.exists(path):
                try:
                    self.audio[key] = pygame.mixer.Sound(path)
                    print(f"Áudio carregado com sucesso: {filename}")
                except Exception as e:
                    print(f"Erro ao carregar áudio '{filename}': {e}")
            else:
                print(f"Arquivo de áudio não encontrado: {path}")

    def play(self, key, volume=1.0, loop=False):
        """Reproduz um arquivo de áudio com o volume especificado.
        Args:
            key (str): Chave do áudio a ser reproduzido.
            volume (float): Volume do áudio (0.0 a 1.0).
            loop (bool): Se True, o áudio será reproduzido em loop.
        Returns:
            pygame.mixer.Sound: O objeto de som reproduzido ou None se falhar.
        """
        loops = -1 if loop else 0
        
        # Se tiver AssetManager, usa-o para tocar o som
        if self.asset_manager:
            if key.startswith('music/'):
                # Remove o prefixo 'music/' e passa para o método de música
                music_key = key[6:] if key.startswith('music/') else key
                return self.asset_manager.play_music(music_key, volume, loops)
            else:
                sound = self.asset_manager.play_sound(key, volume, loops)
                if sound:
                    self.playing_sounds[key] = sound
                return sound
        
        # Fallback para método antigo
        elif self.audio and key in self.audio:
            try:
                sound = self.audio[key]
                sound.set_volume(volume)
                sound.play(loops=loops)
                self.playing_sounds[key] = sound
                return sound
            except Exception as e:
                print(f"Erro ao reproduzir áudio '{key}': {e}")
                return None
        else:
            print(f"Áudio '{key}' não carregado.")
            return None

    def stop(self, sound=None, fadeout_ms=500):
        """Para a reprodução de áudio com fade out opcional.
        Args:
            sound (pygame.mixer.Sound, optional): Som específico a ser parado. Se None, para todos.
            fadeout_ms (int): Tempo de fade out em milissegundos.
        """
        try:
            if sound and isinstance(sound, pygame.mixer.Sound):
                sound.fadeout(fadeout_ms)
            elif sound is None: # Para todos os sons
                pygame.mixer.stop()
                # Limpa lista de sons tocando
                self.playing_sounds.clear()
        except Exception as e:
            print(f"Erro ao parar áudio: {e}")

    def stop_music(self, fadeout_ms=500):
        """Para a música com fade out opcional.
        Args:
            fadeout_ms (int): Tempo de fade out em milissegundos.
        """
        try:
            pygame.mixer.music.fadeout(fadeout_ms)
        except Exception as e:
            print(f"Erro ao parar música: {e}")

    def fade(self, sound, start_vol, end_vol, duration_ms):
        """Atenua o volume de um som ao longo de uma duração (usando threading).
        Args:
            sound (pygame.mixer.Sound): Som a ser atenuado.
            start_vol (float): Volume inicial (0.0 a 1.0).
            end_vol (float): Volume final (0.0 a 1.0).
            duration_ms (int): Duração da atenuação em milissegundos.
        """
        if not sound or not isinstance(sound, pygame.mixer.Sound):
            return

        def _fade_task():
            """Tarefa executada em thread separada para realizar a atenuação do volume."""
            try:
                start_time = pygame.time.get_ticks()
                while True:
                    elapsed = pygame.time.get_ticks() - start_time
                    if elapsed >= duration_ms:
                        sound.set_volume(max(0.0, min(1.0, end_vol)))
                        break # Atenuação completa

                    progress = elapsed / duration_ms
                    current_vol = start_vol + (end_vol - start_vol) * progress
                    sound.set_volume(max(0.0, min(1.0, current_vol)))
                    pygame.time.delay(20) # Pequeno atraso para evitar espera ocupada
            except Exception as e:
                print(f"Erro durante fade de áudio: {e}")

        # Executa a atenuação em uma thread separada para evitar bloquear o loop do jogo
        fade_thread = threading.Thread(target=_fade_task, daemon=True)
        fade_thread.start() 
