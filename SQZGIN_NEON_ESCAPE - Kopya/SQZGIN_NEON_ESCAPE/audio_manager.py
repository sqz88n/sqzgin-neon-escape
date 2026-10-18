"""Harici ses dosyası gerektirmeyen, hata toleranslı ses yöneticisi."""
import math, array
try:
    import pygame
except ImportError:
    pygame = None

class AudioManager:
    def __init__(self, profile):
        self.profile = profile
        self.enabled = False
        self.sounds = {}
        if pygame:
            try:
                if pygame.mixer.get_init() is None:
                    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                self.enabled = True
                for name, freq in {"coin":880, "dash":220, "hit":95, "click":520, "power":660}.items():
                    self.sounds[name] = self._tone(freq, 0.08 if name != "hit" else 0.18)
            except pygame.error:
                self.enabled = False

    def _tone(self, freq, duration):
        rate = 22050
        samples = array.array("h")
        for i in range(int(rate * duration)):
            fade = max(0, 1 - i / (rate * duration))
            samples.append(int(5000 * fade * math.sin(2 * math.pi * freq * i / rate)))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        if self.enabled and self.profile.get("settings", {}).get("sfx", 0) > 0:
            try:
                sound = self.sounds.get(name)
                if sound:
                    sound.set_volume(float(self.profile["settings"].get("sfx", .8)) *
                                     float(self.profile["settings"].get("master", .7)))
                    sound.play()
            except (pygame.error, KeyError, TypeError):
                pass
