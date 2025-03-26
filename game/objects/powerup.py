import pygame
import random
from game.setting.settings import Settings


class PowerUp:
    """Allgemeine Power-Up-Klasse"""

    def __init__(self):
        """Erzeugt ein zufälliges Power-Up an einer zufälligen Position."""
        self.__position = (
            random.randint(0, Settings.grid_width - 1) * Settings.grid_size,
            random.randint(0, Settings.grid_height - 1) * Settings.grid_size
        )
        self.__type = random.choice(["shield", "ammo", "speed"])  # 🎲 Zufälliges Power-Up
        self.__image = self.load_sprite()

    def __generate_random_position(self):
        """Platziert das Power-Up an eine zufällige Position."""
        x = random.randint(0, Settings.grid_width - 1) * Settings.grid_size
        y = random.randint(0, Settings.grid_height - 1) * Settings.grid_size
        return (x, y)

    def load_sprite(self):
        """Lädt das passende Icon für das Power-Up."""
        if self.__type == "shield":
            return pygame.image.load("game/icons/sprites/shield.png")
        elif self.__type == "ammo":
            return pygame.image.load("game/icons/sprites/multi_shot.png")
        elif self.__type == "speed":
            return pygame.image.load("game/icons/sprites/speed.png")

    def activate(self, snake):
        """Aktiviert den Effekt des Power-Ups auf die Schlange."""
        if self.__type == "speed":
            snake.set_speed(15)
            print("[DEBUG] ⚡ Speed Boost aktiviert!")

        elif self.__type == "shield":
            snake.activate_shield()
            print("[DEBUG] 🛡️ Schild aktiviert!")

        elif self.__type == "ammo":
            snake.increase_ammo(5)
            print("[DEBUG] 🔫 Extra Munition erhalten!")

    def get_position(self):
        return self.__position

    def draw(self, surface):
        """Zeichnet das Power-Up mit seinem Sprite."""
        surface.blit(self.__image, self.__position)
