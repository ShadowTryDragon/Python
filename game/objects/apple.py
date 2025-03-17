import random
import pygame
from game.setting.settings import Settings  # ✅ DIREKT importieren
from game.setting.gamecolors import GameColors  # ✅ Falls GameColors in einer separaten Datei liegt



class Apple:
    def __init__(self, count=1, snake=None, moving=False):
        self._positions = []
        self.__count = count
        self.snake = snake
        self.randomize_positions()
        self.__moving = moving  # ✅ Speichern, ob Apfel sich bewegt

        # 🎨 Apfel-Sprite laden & vergrößern (20% größer)
        original_size = Settings.grid_size
        new_size = int(original_size * 2)  # 20% größer

        self.__image = pygame.image.load("game/icons/sprites/apple.png")
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))

    def get_positions(self):
        """Gibt die aktuellen Apfel-Positionen zurück."""
        if not self._positions or any(not isinstance(pos, tuple) for pos in self._positions):
            print(f"[ERROR] ❌ Fehlerhafte Apfel-Positionen: {self._positions}")  # 🛑 Debug-Ausgabe
        return self._positions if self._positions else []  # Stelle sicher, dass eine Liste zurückgegeben wird

    def move(self):
        """Bewegt den Apfel zufällig, falls `moving` aktiv ist."""
        if self.__moving:
            self.randomize_positions()
            print("[DEBUG] 🍏 Der Apfel bewegt sich!")

    def randomize_positions(self):
        """Platziert den Apfel zufällig auf dem Spielfeld, aber nicht auf der Schlange."""
        self._positions = []  # Leere Liste setzen
        attempts = 0  # 🔄 Debug-Zähler für Platzierungsversuche

        while len(self._positions) < self.__count:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)

            # Falls die Position nicht belegt ist, füge sie hinzu
            if new_position not in self._positions and self.snake and new_position not in self.snake.get_positions():
                self._positions.append(new_position)
            else:
                attempts += 1  # Erhöhe die Anzahl der Versuche

            if attempts > 100:  # Falls 100 Versuche erfolglos → Stoppen
                print("[DEBUG] ❌ Konnte keine freie Position für den Apfel finden!")
                break


    def relocate_apple(self, snake, obstacles):
        """Platziert den Apfel an eine neue zufällige Stelle, die nicht von der Schlange oder Hindernissen besetzt ist."""
        while True:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)

            # ✅ Sicherstellen, dass die neue Position nicht auf der Schlange oder einem Hindernis liegt
            if new_position not in snake.get_positions() and new_position not in obstacles.get_positions():
                self._positions = [new_position]
                break  # ✅ Gültige Position gefunden, Schleife beenden

    def action(self, snake):
        snake.increase_length(1)
        snake.increase_score(3)

    def draw(self, surface):
        for pos in self._positions:
            offset = (Settings.grid_size - self.__image.get_width()) // 2  # Mittig platzieren
            surface.blit(self.__image, (pos[0] + offset, pos[1] + offset))


class FakeApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__image = pygame.image.load("game/icons/sprites/apple.png")
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))

    def action(self, snake):
        print("[DEBUG] Fake Apple gegessen! Punkte halbiert.")
        halbierter_score = snake.get_score() // 2
        snake.increase_score(halbierter_score - snake.get_score())  # Score direkt setzen
        snake.flash_red()  # 🟥 Effekt: Schlange leuchtet kurz rot

    def draw(self, surface):
        for pos in self._positions:
            surface.blit(self.__image, pos)


class SuperApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__color = GameColors.SUPER_APPLE_COLOR  # Blau
        self.__active = False
        self.__start_time = None
        self.__image = pygame.image.load("game/icons/sprites/super_apple.png")
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))

    def action(self, snake):
        print("[DEBUG] Sugar Apple gegessen! Punkte werden VERDOPPELT")
        if not self.__active:
            self.__active = True
            self.__start_time = pygame.time.get_ticks()
            snake.set_double_points(True)
            snake.flash_red()

    def draw(self, surface):
        for pos in self._positions:
            surface.blit(self.__image, pos)


class MegaApple(Apple):
    def __init__(self, snake=None):
        super().__init__(count=1, snake=snake)
        self.__image = pygame.image.load("game/icons/sprites/mega_apple.png")
        self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))

    def action(self, snake):
        print("[DEBUG] MEGA APPLE wurde gegessen 50 PUNKTE für Slytherin!.")
        snake.increase_score(50)
        snake.flash_red()


    def draw(self, surface):
        for pos in self._positions:
            surface.blit(self.__image, pos)


class ReverseApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__reversed = False
        self.__start_time = None

    def action(self, snake):
        print("[DEBUG] Reverse Apple gegessen! Steuerung umgekehrt.")  # 🆕 Debug-Ausgabe
        if not self.__reversed:
            self.__reversed = True
            self.__start_time = pygame.time.get_ticks()
            self.__image = pygame.image.load("game/icons/sprites/reverse_apple.png")
            self.__image = pygame.transform.scale(self.__image, (Settings.grid_size, Settings.grid_size))
            self.reverse_controls()
            snake.flash_red()

    def reverse_controls(self):
        Settings.up, Settings.down = Settings.down, Settings.up
        Settings.left, Settings.right = Settings.right, Settings.left

    def reset_controls(self):
        Settings.up, Settings.down = (0, -1), (0, 1)
        Settings.left, Settings.right = (-1, 0), (1, 0)


    def draw(self, surface):
        for pos in self._positions:
            surface.blit(self.__image, pos)


class SugarApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)  # Korrekt!
        self.__start_time = None
        self.__active = False

    def action(self, snake):
        if not self.__active:
            self.__active = True
            self.__start_time = pygame.time.get_ticks()
            snake.set_speed(15)  # Geschwindigkeit erhöhen
            print("[DEBUG] Sugar Apple gegessen! Geschwindigkeit erhöht.")
            snake.flash_red()
