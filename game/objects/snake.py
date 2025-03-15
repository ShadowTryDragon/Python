from game.gamecolors import GameColors
from game.settings import Settings
import random
import pygame


class Snake:
    def __init__(self, start_pos=None, name="Player"):

        """Erstellt eine Schlange mit einer individuellen Startposition und Steuerung."""
        if start_pos is None:
            start_pos = (Settings.screen_width / 2, Settings.screen_height / 2)
        self.__name = name
        self.__length = 1
        self.__positions = [start_pos]
        self.__direction = random.choice(Settings.directions)
        self.__score = 0
        self.__speed = 10
        self.__double_points = False
        self.__flash_time = None
        self.__invisible = False  # ✅ Neue Variable für Unsichtbarkeit

        self.__original_color = GameColors.BODY_COLOR
        self.__color = self.__original_color  # Standardfarbe setzen

    def set_invisible(self, state: bool):
        """Schaltet die Unsichtbarkeit der Schlange ein oder aus."""
        self.__invisible = state
        print(f"[DEBUG] Unsichtbarkeit: {'AN' if state else 'AUS'}")

    def is_alive(self):
        return True  # Snake stirbt nie, daher immer True
    def flash_red(self):
        """Lässt die Schlange kurz rot aufleuchten."""
        self.__color = (255, 0, 0)
        self.__flash_time = pygame.time.get_ticks()

    def update_flash(self):
        """Setzt die Farbe nach 300ms zurück."""
        if self.__flash_time and pygame.time.get_ticks() - self.__flash_time >= 300:
            self.__color = self.__original_color
            self.__flash_time = None

    def set_speed(self, speed):
        """Setzt die Bewegungsgeschwindigkeit."""
        self.__speed = speed

    def set_double_points(self, active):
        """Setzt Double Points ein oder aus."""
        self.__double_points = active

    def increase_score(self, value):
        if self.__double_points:
            value *= 2  # Verdopple Punkte, wenn SuperApple aktiv
        self.__score += value

    def turn(self, new_direction):
        """Ändert die Richtung, wenn sie nicht entgegengesetzt zur aktuellen ist."""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.__direction:
            self.__direction = new_direction

    def move(self):
        """Bewegt die Schlange in die aktuelle Richtung."""
        head_pos = self.get_head_position()
        x, y = self.__direction
        new = (((head_pos[0] + (x * Settings.grid_size)) % Settings.screen_width),
               (head_pos[1] + (y * Settings.grid_size)) % Settings.screen_height)

        self.__positions.insert(0, new)

        # Statt hier zu kollisionsprüfen, wird das in `__check_collisions()` gemacht!
        if len(self.__positions) > self.__length:
            self.__positions.pop()

    def get_positions(self):
        return self.__positions

    def get_head_position(self):
        return self.__positions[0]

    def reduce_length(self, amount):
        """Verkürzt die Schlange um `amount`, aber lässt mindestens 1 Segment übrig."""
        self.__length = max(1, self.__length - amount)  # Mindestlänge = 1
        self.__positions = self.__positions[:self.__length]  # Liste kürzen

    def reset(self):
        """Setzt die Schlange zurück auf ihre Startwerte."""
        self.__length = 1
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__score = 0

    def increase_length(self, value):
        """Verlängert die Schlange um `value` Segmente."""
        self.__length += value

    def get_score(self):
        return self.__score

    def draw(self, surface):
        """Zeichnet die Schlange (unsichtbar oder sichtbar)."""
        if not self.__invisible:  # ✅ Falls unsichtbar, nicht zeichnen
            for index, pos in enumerate(self.__positions):
                r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
                pygame.draw.rect(surface, self.__color if index else GameColors.HEAD_COLOR, r)
                pygame.draw.rect(surface, (93, 216, 228), r, 1)