import pygame
import sys
import random


# Farben für das Snake-Spiel
class GameColors:
    # Schlange
    BODY_COLOR = (46, 58, 89)  # Dunkles Blau für den Körper
    HEAD_COLOR = (46, 58, 89)  # Helles Grün für den Kopf

    # Früchte
    APPLE_COLOR = (231, 76, 60)  # Rot für den Apfel
    FAKE_APPLE_COLOR = (155, 89, 182)  # Lila für den Fake-Apfel
    MIN_APPLE_COLOR = (39, 174, 96)  # Grün für den Halb-Apfel


class Snake:
    def __init__(self):
        self.__length = 1
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__color = GameColors.BODY_COLOR
        self.__score = 0
        self.__invisible = False  # NEU: Unsichtbarkeit

    def turn(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.__direction:  # cannot do a 180
            self.__direction = new_direction

    def move(self):
        head_pos = self.get_head_position()
        x, y = self.__direction
        new = (((head_pos[0] + (x * Settings.grid_size)) % Settings.screen_width),
               (head_pos[1] + (y * Settings.grid_size)) % Settings.screen_height)
        if len(self.__positions) > 2 and new in self.__positions[2:]:
            self.reset()
        else:
            self.__positions.insert(0, new)
            if len(self.__positions) > self.__length:
                self.__positions.pop()

    def get_positions(self):
        return self.__positions

    def get_head_position(self):
        return self.__positions[0]

    def reset(self):
        self.reset_length()
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__score = 0

    def increase_length(self, value):
        self.__length += value

    def decrease_length(self, value):
        if self.__length > 1:  # Verhindern, dass die Länge negativ wird
            self.__length -= value
            self.__positions.pop()  # Entfernt das letzte Segment

    def reset_length(self):
        self.__length = 1

    def increase_score(self, value):
        self.__score += value

    def decrease_score(self):
        self.__score /= 2

    def get_score(self):
        return self.__score

    def reset_score(self):
        self.__score = 0

    def set_invisible(self, value):
        """Setzt die Unsichtbarkeit der Schlange."""
        self.__invisible = value

    def draw(self, surface):
        for index, pos in enumerate(self.__positions):
            if self.__invisible:
                continue  # NICHT ZEICHNEN, WENN UNSICHTBAR
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            if index == 0:  # Kopf der Schlange
                pygame.draw.rect(surface, GameColors.HEAD_COLOR, r)
            else:
                pygame.draw.rect(surface, self.__color, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)  # Rand für alle Teile


class Food:
    def __init__(self, count=3, color=(0, 0, 0), snake=None):
        self.__positions = []
        self.__count = count
        self.__color = color
        self.snake = snake  # Referenz auf die Schlange
        self.randomize_positions()

    def get_positions(self):
        return self.__positions

    def randomize_positions(self):
        self.__positions = []
        while len(self.__positions) < self.__count:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)
            # Hier wird die Position der Frucht gegen die Positionen der Schlange geprüft
            if new_position not in self.__positions and new_position not in self.snake.get_positions():
                self.__positions.append(new_position)

    def draw(self, surface):
        for pos in self.__positions:
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, self.__color, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)


class Apple(Food):
    def __init__(self, count=2, snake=None):
        super().__init__(count, GameColors.APPLE_COLOR, snake=snake)

    def action(self, snake):
        snake.increase_length(1)
        snake.increase_score(3)  # Apfel gibt 3 Punkte


class FakeApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, GameColors.FAKE_APPLE_COLOR, snake=snake)

    def action(self, snake):
        snake.increase_score(1)
        snake.increase_length(3)


class MinApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, GameColors.MIN_APPLE_COLOR, snake=snake)

    def action(self, snake):
        snake.decrease_score()  # HalfApple reduziert Score


class ReverseApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, (255, 165, 0), snake=snake)  # Orange Farbe für die Frucht
        self.__reversed = False
        self.__start_time = None
        self.__active = False  # FRUCHT IST JETZT DIREKT SICHTBAR
        self.__fruit_counter = 0  # Zähler für gefressene Früchte
        self.randomize_positions()  # Zufällige Position setzen

    def action(self, snake):
        if self.__active and not self.__reversed:  # Nur aktiv, wenn sie erscheinen darf
            self.__reversed = True
            self.__start_time = pygame.time.get_ticks()
            self.reverse_controls()
            self.__active = False  # Nach Nutzung verschwindet die Frucht
            self.__fruit_counter = 0  # Zähler zurücksetzen

    def reverse_controls(self):
        # Steuerung umkehren
        Settings.up, Settings.down = Settings.down, Settings.up
        Settings.left, Settings.right = Settings.right, Settings.left

    def reset_controls(self):
        # Steuerung zurücksetzen
        Settings.up, Settings.down = (0, -1), (0, 1)
        Settings.left, Settings.right = (-1, 0), (1, 0)
        self.__reversed = False
        self.__active = True  # Frucht erscheint wieder
        self.randomize_positions()  # Neue Position setzen

    def update(self):
        if self.__reversed:
            elapsed_time = pygame.time.get_ticks() - self.__start_time
            if elapsed_time >= 5000:  # Nach 5 Sek zurücksetzen
                self.reset_controls()

    def reset_fruit_eaten(self):
        self.__fruit_counter = 0

    def track_fruit_eaten(self):
        """Erhöht den Zähler für gefressene Früchte und aktiviert die Frucht nach 10 Früchten."""
        self.__fruit_counter += 1
        if self.__fruit_counter >= 10:
            self.__active = True

    def draw(self, surface):
        if self.__active:  # NUR ZEICHNEN, WENN AKTIV
            super().draw(surface)


class InvisibilityApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, (128, 128, 128), snake=snake)  # Grau für die Unsichtbarkeits-Frucht
        self.__invisible = False
        self.__start_time = None
        self.__active = False  # Wird erst bei 40+ Punkten sichtbar

    def action(self, snake):
        if self.__active and not self.__invisible:
            self.__invisible = True
            self.__start_time = pygame.time.get_ticks()
            self.__active = False  # Nach Nutzung verschwindet die Frucht
            self.make_invisible(snake)

    def make_invisible(self, snake):
        """Setzt die Schlange auf unsichtbar."""
        snake.set_invisible(True)

    def reset_visibility(self, snake):
        """Macht die Schlange wieder sichtbar."""
        snake.set_invisible(False)
        self.__invisible = False

    def update(self, snake):
        """Prüft, ob die Unsichtbarkeit abgelaufen ist."""
        if self.__invisible:
            elapsed_time = pygame.time.get_ticks() - self.__start_time
            if elapsed_time >= 5000:  # Nach 5 Sekunden zurücksetzen
                self.reset_visibility(snake)

    def check_spawn_condition(self, snake):
        """Aktiviert die Frucht, wenn der Score 40 oder mehr beträgt."""
        if snake.get_score() >= 40 and not self.__active:
            self.__active = True
            self.randomize_positions()  # Neue Position setzen

    def draw(self, surface):
        if self.__active:  # Nur zeichnen, wenn aktiv
            super().draw(surface)


class Settings:
    screen_width = 480
    screen_height = 480

    grid_size = 20
    grid_width = screen_width / grid_size
    grid_height = screen_height / grid_size

    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)

    directions = [up, down, left, right]


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.__clock = pygame.time.Clock()  # Hier setzen wir das Attribut __clock
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height), 0, 32)
        self.__surface = pygame.Surface(self.__screen.get_size()).convert()
        self.__snake = Snake()
        self.__apple = Apple(count=1, snake=self.__snake)
        self.__fakeapple = FakeApple(count=1, snake=self.__snake)
        self.__halfapple = MinApple(count=1, snake=self.__snake)
        self.__reverse_apple = ReverseApple(count=1, snake=self.__snake)  # NEU
        self.__my_font = pygame.font.SysFont("monospace", 16)
        self.__paused = False  # Variable zur Steuerung der Pause
        self.__invisibility_apple = InvisibilityApple(count=1, snake=self.__snake)  # NEU

    def __check_collisions(self):
        head_pos = self.__snake.get_head_position()

        if head_pos in self.__apple.get_positions():
            self.__reverse_apple.track_fruit_eaten()
            self.__apple.action(self.__snake)
            self.__halfapple.randomize_positions()
            self.__apple.randomize_positions()
            self.__fakeapple.randomize_positions()
            self.__invisibility_apple.check_spawn_condition(self.__snake)  # NEU

        elif head_pos in self.__fakeapple.get_positions():
            self.__reverse_apple.track_fruit_eaten()
            self.__fakeapple.action(self.__snake)
            self.__halfapple.randomize_positions()
            self.__apple.randomize_positions()
            self.__fakeapple.randomize_positions()
            self.__invisibility_apple.check_spawn_condition(self.__snake)  # NEU

        elif head_pos in self.__halfapple.get_positions():
            self.__reverse_apple.track_fruit_eaten()
            self.__halfapple.action(self.__snake)
            self.__halfapple.randomize_positions()
            self.__apple.randomize_positions()
            self.__fakeapple.randomize_positions()
            self.__invisibility_apple.check_spawn_condition(self.__snake)  # NEU

        elif head_pos in self.__reverse_apple.get_positions():  # NEU
            self.__reverse_apple.action(self.__snake)
            self.__reverse_apple.reset_fruit_eaten()
            self.__invisibility_apple.check_spawn_condition(self.__snake)  # NEU

        elif head_pos in self.__invisibility_apple.get_positions():
            self.__invisibility_apple.action(self.__snake)
            self.__reverse_apple.track_fruit_eaten()

    def __draw_grid(self, surface):
        for y in range(0, int(Settings.grid_height)):
            for x in range(0, int(Settings.grid_width)):
                r = pygame.Rect((x * Settings.grid_size, y * Settings.grid_size),
                                (Settings.grid_size, Settings.grid_size))
                color = (93, 216, 228) if (x + y) % 2 == 0 else (84, 194, 205)
                pygame.draw.rect(surface, color, r)

    def __quit_game(self):
        pygame.quit()
        sys.exit()

    def __toggle_pause(self):
        self.__paused = not self.__paused  # Wechselt zwischen pausiert und nicht pausiert

    def __handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.__snake.turn(Settings.up)
                elif event.key == pygame.K_w:
                    self.__snake.turn(Settings.up)
                elif event.key == pygame.K_s:
                    self.__snake.turn(Settings.down)
                elif event.key == pygame.K_DOWN:
                    self.__snake.turn(Settings.down)
                elif event.key == pygame.K_LEFT:
                    self.__snake.turn(Settings.left)
                elif event.key == pygame.K_a:
                    self.__snake.turn(Settings.left)
                elif event.key == pygame.K_RIGHT:
                    self.__snake.turn(Settings.right)
                elif event.key == pygame.K_d:
                    self.__snake.turn(Settings.right)
                elif event.key == pygame.K_r:
                    self.__snake.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.__quit_game()
                elif event.key == pygame.K_q:
                    self.__quit_game()
                elif event.key == pygame.K_p:  # NEU: Pause-Taste
                    self.__paused = not self.__paused  # Toggle Pause-Status

    def __draw_objects(self):
        self.__snake.draw(self.__surface)
        self.__apple.draw(self.__surface)
        self.__fakeapple.draw(self.__surface)
        self.__halfapple.draw(self.__surface)
        self.__reverse_apple.draw(self.__surface)  # NEU
        self.__invisibility_apple.draw(self.__surface)

    def __update_screen(self):
        self.__screen.blit(self.__surface, (0, 0))
        text = self.__my_font.render("Score {0}".format(self.__snake.get_score()), True, (0, 0, 0))
        self.__screen.blit(text, (5, 10))
        pygame.display.update()

        if self.__paused:
            pause_text = self.__my_font.render("PAUSE - Press P to Resume", True, (255, 0, 0))
            self.__screen.blit(pause_text, (Settings.screen_width // 2 - 80, Settings.screen_height // 2))

    def main_loop(self):
        while True:
            self.__clock.tick(10)
            self.__handle_keys()
            if not self.__paused:  # NEU: Nur bewegen, wenn nicht pausiert
                self.__draw_grid(self.__surface)
                self.__snake.move()
                self.__check_collisions()
                self.__draw_objects()
                self.__reverse_apple.update()  # NEU
                self.__invisibility_apple.update(self.__snake)  # NEU
            self.__update_screen()


game = SnakeGame()
game.main_loop()
