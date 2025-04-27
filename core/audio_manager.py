import pygame
import os
import threading

class AudioManager:
    def __init__(self):
        """Inicializa o mixer de áudio e carrega os sons."""
        # pygame.mixer.init()
        self.audio = {}
        self.load_audio()

    def load_audio(self):
        """Carrega os recursos de áudio do jogo."""
        # Verifica se o diretório de áudio existe
        base_dir = os.path.dirname(os.path.dirname(__file__)) # Raiz do projeto
        audio_dir = os.path.join(base_dir, 'assets', 'audio') # Caminho atualizado para assets/audio
        if not os.path.exists(audio_dir):
            print(f"Diretório de áudio não encontrado: {audio_dir}")
            return

        sounds_to_load = {
            'intro': 'intro.mp3',
            'pistol_fire': 'beretta-m9.mp3',
            # Adicione outros sons aqui:
            # 'pistol_reload_start': 'reload_start.wav',
            # 'pistol_reload_end': 'reload_end.wav',
            # 'pistol_empty': 'empty_click.wav',
            # 'player_hurt': 'player_hurt.wav',
            # 'enemy_hurt': 'enemy_hurt.wav',
            # 'footstep': 'footstep.wav',
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
        """Reproduz um arquivo de áudio com o volume especificado."""
        if key in self.audio:
            sound = self.audio[key]
            sound.set_volume(volume)
            loops = -1 if loop else 0
            sound.play(loops=loops)
            return sound
        else:
            # print(f"Áudio '{key}' não carregado.") # Menos verboso
            return None

    def stop(self, sound=None, fadeout_ms=500):
        """Para a reprodução de áudio com fade out opcional."""
        if sound and isinstance(sound, pygame.mixer.Sound):
            sound.fadeout(fadeout_ms)
        elif sound is None: # Para todos os sons
             pygame.mixer.stop()
        # else: som específico não encontrado ou inválido

    def fade(self, sound, start_vol, end_vol, duration_ms):
        """Atenua o volume de um som ao longo de uma duração (usando threading)."""
        if not sound or not isinstance(sound, pygame.mixer.Sound):
            return

        def _fade_task():
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

        # Executa a atenuação em uma thread separada para evitar bloquear o loop do jogo
        fade_thread = threading.Thread(target=_fade_task, daemon=True)
        fade_thread.start() 
