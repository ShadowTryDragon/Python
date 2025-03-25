import pygame
from game.setting.settings import Settings

class Bullet:
    def __init__(self, position, direction):
        self.__position = position
        self.__direction = direction
        self.__speed = 10
        self.__image = pygame.image.load("game/icons/sprites/bullet.png").convert_alpha()
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))

    def move(self):
        """Bewegt das Geschoss in die gewählte Richtung."""
        x, y = self.__position
        dx, dy = self.__direction
        self.__position = ((x + dx * self.__speed) % Settings.screen_width,
                           (y + dy * self.__speed) % Settings.screen_height)

    def get_position(self):
        """Gibt die Position zurück."""
        return self.__position

    def draw(self, surface):
        """Zeichnet das Geschoss."""
        surface.blit(self.__image, self.__position)
