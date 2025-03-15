import random
import pygame
from game.settings import Settings  # ✅ DIREKT importieren
from game.gamecolors import GameColors  # ✅ Falls GameColors in einer separaten Datei liegt



class Apple:
    def __init__(self, count=1, snake=None, moving=False):
        self.__positions = []
        self.__count = count
        self.__color = GameColors.APPLE_COLOR
        self.snake = snake
        self.randomize_positions()
        self.__moving = moving  # ✅ Speichern, ob Apfel sich bewegt

    def get_positions(self):
        return self.__positions

    def move(self):
        """Bewegt den Apfel zufällig, falls `moving` aktiv ist."""
        if self.__moving:
            self.randomize_positions()
            print("[DEBUG] 🍏 Der Apfel bewegt sich!")

    def randomize_positions(self):
        self.__positions = []
        while len(self.__positions) < self.__count:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)
            if new_position not in self.__positions and new_position not in self.snake.get_positions():
                self.__positions.append(new_position)

    def relocate_apple(self, snake, obstacles):
        """Platziert den Apfel an eine neue zufällige Stelle, die nicht von der Schlange oder Hindernissen besetzt ist."""
        while True:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)

            # ✅ Sicherstellen, dass die neue Position nicht auf der Schlange oder einem Hindernis liegt
            if new_position not in snake.get_positions() and new_position not in obstacles.get_positions():
                self.__positions = [new_position]
                break  # ✅ Gültige Position gefunden, Schleife beenden

    def action(self, snake):
        snake.increase_length(1)
        snake.increase_score(3)

    def draw(self, surface):
        for pos in self.__positions:
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, self.__color, r)  # ✅ Benutze self.__color
            pygame.draw.rect(surface, (93, 216, 228), r, 1)


class FakeApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__color = GameColors.FAKE_APPLE_COLOR  # Pink

    def action(self, snake):
        print("[DEBUG] Fake Apple gegessen! Punkte halbiert.")
        halbierter_score = snake.get_score() // 2
        snake.increase_score(halbierter_score - snake.get_score())  # Score direkt setzen
        snake.flash_red()  # 🟥 Effekt: Schlange leuchtet kurz rot


class SuperApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__color = GameColors.SUPER_APPLE_COLOR  # Blau
        self.__active = False
        self.__start_time = None

    def action(self, snake):
        print("[DEBUG] Sugar Apple gegessen! Punkte werden VERDOPPELT")
        if not self.__active:
            self.__active = True
            self.__start_time = pygame.time.get_ticks()
            snake.set_double_points(True)
            snake.flash_red()


class MegaApple(Apple):
    def __init__(self, snake=None):
        super().__init__(count=1, snake=snake)
        self.__color = GameColors.MEGA_APPLE_COLOR  # Rot

    def action(self, snake):
        print("[DEBUG] MEGA APPLE wurde gegessen 50 PUNKTE für Slytherin!.")
        snake.increase_score(50)
        snake.flash_red()


class ReverseApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__color = GameColors.REVERSE_APPLE_COLOR  # Orange
        self.__reversed = False
        self.__start_time = None

    def action(self, snake):
        print("[DEBUG] Reverse Apple gegessen! Steuerung umgekehrt.")  # 🆕 Debug-Ausgabe
        if not self.__reversed:
            self.__reversed = True
            self.__start_time = pygame.time.get_ticks()
            self.reverse_controls()
            snake.flash_red()

    def reverse_controls(self):
        Settings.up, Settings.down = Settings.down, Settings.up
        Settings.left, Settings.right = Settings.right, Settings.left

    def reset_controls(self):
        Settings.up, Settings.down = (0, -1), (0, 1)
        Settings.left, Settings.right = (-1, 0), (1, 0)


class SugarApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)  # Korrekt!
        self.__color = GameColors.SUGAR_APPLE_COLOR  # Gold
        self.__start_time = None
        self.__active = False

    def action(self, snake):
        if not self.__active:
            self.__active = True
            self.__start_time = pygame.time.get_ticks()
            snake.set_speed(15)  # Geschwindigkeit erhöhen
            print("[DEBUG] Sugar Apple gegessen! Geschwindigkeit erhöht.")
            snake.flash_red()