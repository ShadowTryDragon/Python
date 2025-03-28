import pygame

from game.setting.settings import Settings


class Bullet:
    def __init__(self, position, direction, owner):
        self.__position = position
        self.__direction = direction
        self.__speed = 10
        self.__image = pygame.image.load("game/icons/sprites/bullet.png").convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size // 2, Settings.grid_size // 2))
        self.owner = owner  # 🔥 Speichert, wer die Kugel abgeschossen hat (Spieler oder Feind)

    def move(self):
        """Bewegt das Geschoss in die gewählte Richtung."""
        x, y = self.__position
        dx, dy = self.__direction

        # ✅ Position aktualisieren
        new_x = (x + dx * self.__speed) % Settings.screen_width
        new_y = (y + dy * self.__speed) % Settings.screen_height

        # ✅ Stelle sicher, dass die Position eine Liste bleibt
        self.__position = [new_x, new_y]

    def get_position(self):
        """Gibt die Position zurück."""
        return self.__position

    def draw(self, surface):
        """Zeichnet das Geschoss."""
        surface.blit(self.__image, self.__position)
