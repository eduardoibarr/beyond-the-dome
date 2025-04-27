import pygame
import os
import threading

class AudioManager:
    def __init__(self):
        """Initializes the audio mixer and loads sounds."""
        pygame.mixer.init()
        self.audio = {}
        self.load_audio()

    def load_audio(self):
        """Loads game audio resources."""
        # Check if audio directory exists
        base_dir = os.path.dirname(os.path.dirname(__file__)) # Project root
        audio_dir = os.path.join(base_dir, 'assets', 'audio') # Updated path to assets/audio
        if not os.path.exists(audio_dir):
            print(f"Audio directory not found: {audio_dir}")
            return

        sounds_to_load = {
            'intro': 'intro.mp3',
            'pistol_fire': 'beretta-m9.mp3',
            # Add other sounds here:
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
                    print(f"Audio loaded successfully: {filename}")
                except Exception as e:
                    print(f"Error loading audio '{filename}': {e}")
            else:
                print(f"Audio file not found: {path}")

    def play(self, key, volume=1.0, loop=False):
        """Plays an audio file with the specified volume."""
        if key in self.audio:
            sound = self.audio[key]
            sound.set_volume(volume)
            loops = -1 if loop else 0
            sound.play(loops=loops)
            return sound
        else:
            # print(f"Audio '{key}' not loaded.") # Less verbose
            return None

    def stop(self, sound=None, fadeout_ms=500):
        """Stops audio playback with optional fade out."""
        if sound and isinstance(sound, pygame.mixer.Sound):
            sound.fadeout(fadeout_ms)
        elif sound is None: # Stop all sounds
             pygame.mixer.stop()
        # else: specific sound not found or invalid

    def fade(self, sound, start_vol, end_vol, duration_ms):
        """Fades the volume of a sound over a duration (using threading)."""
        if not sound or not isinstance(sound, pygame.mixer.Sound):
            return

        def _fade_task():
            start_time = pygame.time.get_ticks()
            while True:
                elapsed = pygame.time.get_ticks() - start_time
                if elapsed >= duration_ms:
                    sound.set_volume(max(0.0, min(1.0, end_vol)))
                    break # Fade complete

                progress = elapsed / duration_ms
                current_vol = start_vol + (end_vol - start_vol) * progress
                sound.set_volume(max(0.0, min(1.0, current_vol)))
                pygame.time.delay(20) # Small delay to prevent busy-waiting

        # Run fading in a separate thread to avoid blocking game loop
        fade_thread = threading.Thread(target=_fade_task, daemon=True)
        fade_thread.start() 