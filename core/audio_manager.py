import pygame
import os
import threading

class AudioManager:
    def __init__(self, asset_manager=None):

        self.asset_manager = asset_manager
        self.playing_sounds = {}

        if not self.asset_manager:
            self.audio = {}
            self.load_audio()
        else:

            self.audio = None

    def load_audio(self):

        base_dir = os.path.dirname(os.path.dirname(__file__))
        audio_dir = os.path.join(base_dir, 'assets', 'audio')
        if not os.path.exists(audio_dir):
            print(f"Diretório de áudio não encontrado: {audio_dir}")
            return

        sounds_to_load = {
            'music/intro': 'intro.mp3',
            'beretta-m9': 'beretta-m9.mp3',
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
        loops = -1 if loop else 0

        if self.asset_manager:
            if key.startswith('music/'):

                music_key = key[6:] if key.startswith('music/') else key
                return self.asset_manager.play_music(music_key, volume, loops)
            else:
                sound = self.asset_manager.play_sound(key, volume, loops)
                if sound:
                    self.playing_sounds[key] = sound
                return sound

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
        try:
            if sound and isinstance(sound, pygame.mixer.Sound):
                sound.fadeout(fadeout_ms)
            elif sound is None:
                pygame.mixer.stop()

                self.playing_sounds.clear()
        except Exception as e:
            print(f"Erro ao parar áudio: {e}")

    def stop_music(self, fadeout_ms=500):
        try:
            pygame.mixer.music.fadeout(fadeout_ms)
        except Exception as e:
            print(f"Erro ao parar música: {e}")

    def fade(self, sound, start_vol, end_vol, duration_ms):
        if not sound or not isinstance(sound, pygame.mixer.Sound):
            return

        def _fade_task():
            try:
                start_time = pygame.time.get_ticks()
                while True:
                    elapsed = pygame.time.get_ticks() - start_time
                    if elapsed >= duration_ms:
                        sound.set_volume(max(0.0, min(1.0, end_vol)))
                        break

                    progress = elapsed / duration_ms
                    current_vol = start_vol + (end_vol - start_vol) * progress
                    sound.set_volume(max(0.0, min(1.0, current_vol)))
                    pygame.time.delay(20)
            except Exception as e:
                print(f"Erro durante fade de áudio: {e}")

        fade_thread = threading.Thread(target=_fade_task, daemon=True)
        fade_thread.start()
