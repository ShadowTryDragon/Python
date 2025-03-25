import pygame
import random
from game.setting.settings import Settings

class PowerUp:
    def __init__(self):
        """Erstellt ein zufälliges Power-Up."""
        self.__position = (random.randint(0, Settings.screen_width - Settings.grid_size),
                           random.randint(0, Settings.screen_height - Settings.grid_size))
        self.__effect = random.choice(["speed", "shield", "multi_shot"])
        self.__image = pygame.image.load(f"game/icons/sprites/{self.__effect}.png").convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))

    def get_position(self):
        """Gibt die Position des Power-Ups zurück."""
        return self.__position

    def activate(self, snake):
        """Aktiviert den Effekt des Power-Ups für die Schlange."""
        if self.__effect == "speed":
            snake.set_speed(20)
        elif self.__effect == "shield":
            snake.set_invisible(True)
        elif self.__effect == "triple_shot":
            snake.enable_triple_shot()

        print(f"[DEBUG] {self.__effect} aktiviert!")

    def draw(self, surface):
        """Zeichnet das Power-Up."""
        surface.blit(self.__image, self.__position)
