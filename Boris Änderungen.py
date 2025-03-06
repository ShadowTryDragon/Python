import pygame
import sys
import sqlite3
import random


# === Einstellungen ===
class Settings:
    screen_width = 800  # Breite vergrößern
    screen_height = 600  # Höhe vergrößern
    grid_size = 20
    grid_width = screen_width / grid_size
    grid_height = screen_height / grid_size

    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)
    directions = [up, down, left, right]



# === Datenbank-Funktionen ===
def init_db():
    """Erstellt die Datenbank-Tabelle, falls sie nicht existiert."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_score(name, score):
    """Speichert den Spieler-Score in die Datenbank."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()


def get_highscores():
    """Liest die Top 10 Highscores aus der Datenbank."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM highscores ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores


# === Startmenü ===
class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 30)
        self.options = ["Start Game", "Bestenliste", "Beenden"]
        self.selected = 0

    def draw(self):
        self.screen.fill((0, 0, 0))
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected else (150, 150, 150)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (Settings.screen_width // 2 - text.get_width() // 2, 150 + i * 50))

        pygame.display.flip()

    def handle_keys(self):
        """Menü-Steuerung"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected  # Auswahl zurückgeben
        return None


# === Namenseingabe ===
def get_player_name(screen):
    font = pygame.font.SysFont("monospace", 30)
    name = ""

    while True:
        screen.fill((0, 0, 0))
        text = font.render("Dein Name: " + name, True, (255, 255, 255))
        screen.blit(text, (50, 200))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() and len(name) < 10:
                    name += event.unicode


# === Bestenliste anzeigen ===
def show_highscores(screen):
    font = pygame.font.SysFont("monospace", 25)
    scores = get_highscores()

    while True:
        screen.fill((0, 0, 0))
        title = font.render("Bestenliste", True, (255, 255, 255))
        screen.blit(title, (Settings.screen_width // 2 - 80, 50))

        for i, (name, score) in enumerate(scores):
            text = font.render(f"{name}: {score}", True, (200, 200, 200))
            screen.blit(text, (100, 100 + i * 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Zurück zum Menü

# === Farben für das Spiel (JETZT KORREKT POSITIONIERT) ===
class GameColors:
    BODY_COLOR = (46, 58, 89)  # Dunkelblau für Snake-Körper
    HEAD_COLOR = (0, 255, 0)  # Grün für Snake-Kopf
    APPLE_COLOR = (231, 76, 60)  # Rot für normalen Apfel

    # Spezial-Äpfel Farben
    FAKE_APPLE_COLOR = (255, 105, 180)  # Pink für Fake Apple
    SUPER_APPLE_COLOR = (0, 0, 255)  # Blau für SuperApple
    SUGAR_APPLE_COLOR = (255, 215, 0)  # Gold für SugarApple
    MEGA_APPLE_COLOR = (255, 0, 0)  # Rot für MegaApple
    REVERSE_APPLE_COLOR = (255, 165, 0)  # Orange für ReverseApple



# === Snake-Klasse ===
class Snake:

    def __init__(self):
        self.__length = 1
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__score = 0
        self.__speed = 10
        self.__double_points = False
        self.__original_color = GameColors.BODY_COLOR
        self.__flash_time = None
        self.__original_color = GameColors.BODY_COLOR  # Originalfarbe speichern
        self.__color = self.__original_color  # Standardfarbe setzen

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
        if (new_direction[0] * -1, new_direction[1] * -1) != self.__direction:
            self.__direction = new_direction

    def move(self):
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

    def reset(self):
        self.__length = 1
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__score = 0

    def increase_length(self, value):
        self.__length += value

    def increase_score(self, value):
        self.__score += value

    def get_score(self):
        return self.__score

    def draw(self, surface):
        for index, pos in enumerate(self.__positions):
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, self.__color if index else GameColors.HEAD_COLOR, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)

# === Apfel-Klasse ===
class Apple:
    def __init__(self, count=1, snake=None):
        self.__positions = []
        self.__count = count
        self.__color = GameColors.APPLE_COLOR
        self.snake = snake
        self.randomize_positions()

    def get_positions(self):
        return self.__positions

    def randomize_positions(self):
        self.__positions = []
        while len(self.__positions) < self.__count:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)
            if new_position not in self.__positions and new_position not in self.snake.get_positions():
                self.__positions.append(new_position)

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
        if not self.__active:
            self.__active = True
            self.__start_time = pygame.time.get_ticks()
            snake.set_double_points(True)
            snake.flash_red()

    def update(self, snake):
        """Deaktiviert den Effekt nach 5 Sekunden."""
        if self.__active and pygame.time.get_ticks() - self.__start_time >= 5000:
            self.__active = False
            snake.set_double_points(False)

class MegaApple(Apple):
    def __init__(self, snake=None):
        super().__init__(count=1, snake=snake)
        self.__color = GameColors.MEGA_APPLE_COLOR  # Rot

    def action(self, snake):
        snake.increase_score(50)
        snake.flash_red()

class ReverseApple(Apple):
    def __init__(self, count=1, snake=None):
        super().__init__(count, snake=snake)
        self.__color = GameColors.REVERSE_APPLE_COLOR  # Orange
        self.__reversed = False
        self.__start_time = None

    def action(self, snake):
        if not self.__reversed:
            self.__reversed = True
            self.__start_time = pygame.time.get_ticks()
            self.reverse_controls()
            snake.flash_red()

    def reverse_controls(self):
        Settings.up, Settings.down = Settings.down, Settings.up
        Settings.left, Settings.right = Settings.right, Settings.left

    def update(self):
        """Deaktiviert die Steuerungsumkehr nach 5 Sekunden."""
        if self.__reversed and pygame.time.get_ticks() - self.__start_time >= 5000:
            self.__reversed = False
            self.reset_controls()

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
            snake.flash_red()

    def update(self, snake):
        if self.__active and pygame.time.get_ticks() - self.__start_time >= 5000:
            self.__active = False
            snake.set_speed(10)  # Geschwindigkeit zurücksetzen





# === Snake-Spiel ===
class SnakeGame:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name  # Spielername speichern
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__surface = pygame.Surface(self.__screen.get_size()).convert()
        self.__snake = Snake()
        self.__apple = Apple(count=1, snake=self.__snake)
        self.__my_font = pygame.font.SysFont("monospace", 16)
        self.__running = True  # Flag für Spielstatus
        self.__apple = Apple(count=1, snake=self.__snake)  # Standard-Apfel


    def spawn_random_apple(self):
        """Erzeugt einen zufälligen Spezial-Apfel."""
        apple_types = [FakeApple, SuperApple, SugarApple, ReverseApple]
        return random.choice(apple_types)(count=1, snake=self.__snake)

    def should_spawn_mega_apple(self):
        """Prüft, ob der Mega Apple erscheinen soll."""
        return self.__snake.get_score() >= 50 and random.randint(1, 10) == 1  # 10% Wahrscheinlichkeit

    def __check_collisions(self):
        head_pos = self.__snake.get_head_position()

        # 🍏 Apfel essen
        if head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)  # Apfel-Effekt aktivieren

            # 🆕 Apfel neu generieren
            if self.should_spawn_mega_apple():
                self.__apple = MegaApple(snake=self.__snake)
            elif random.randint(1, 5) == 1:  # 20% Wahrscheinlichkeit für Spezial-Apfel
                self.__apple = self.spawn_random_apple()
            else:
                self.__apple = Apple(count=1, snake=self.__snake)  # Normaler Apfel

        # 💀 Prüfen, ob die Schlange sich selbst trifft
        if head_pos in self.__snake.get_positions()[1:]:
            print("Game Over: Schlange hat sich selbst getroffen!")  # Debugging
            self.__running = False  # Spiel sicher stoppen

    def __handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.__snake.turn(Settings.up)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.__snake.turn(Settings.down)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.__snake.turn(Settings.left)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.__snake.turn(Settings.right)
                elif event.key == pygame.K_ESCAPE:
                    self.__running = False

    def main_loop(self):
        while self.__running:
            self.__clock.tick(10)
            self.__handle_keys()
            self.__snake.move()
            self.__check_collisions()
            self.__draw_objects()
            self.__update_screen()
            self.__snake.update_flash()

        print("Game Over: main_loop() beendet.")  # Debugging
        final_score = self.show_game_over_screen()  # 🎮 Game Over Bildschirm anzeigen
        return final_score  # Score zurückgeben für Highscore-Speicherung

    def show_game_over_screen(self):
        """Zeigt den Game Over Bildschirm mit der Option, ins Menü zurückzukehren."""
        font = pygame.font.SysFont("monospace", 30)
        final_score = self.__snake.get_score()  # Punktzahl speichern

        while True:
            self.__screen.fill((0, 0, 0))
            text1 = font.render("GAME OVER", True, (255, 0, 0))
            text2 = font.render(f"Score: {final_score}", True, (255, 255, 255))
            text3 = font.render("Enter: Neu starten | ESC: Beenden | M: Menü", True, (200, 200, 200))

            self.__screen.blit(text1, (Settings.screen_width // 2 - text1.get_width() // 2, 100))
            self.__screen.blit(text2, (Settings.screen_width // 2 - text2.get_width() // 2, 160))
            self.__screen.blit(text3, (Settings.screen_width // 2 - text3.get_width() // 2, 220))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("Spiel wird neugestartet...")  # Debugging
                        return final_score, False  # 🆕 False bedeutet: Spiel neu starten
                    elif event.key == pygame.K_m:  # 🆕 Taste M für Menü
                        print("Zurück zum Menü.")  # Debugging
                        return final_score, True  # 🆕 True bedeutet: Zurück ins Menü
                    elif event.key == pygame.K_ESCAPE:
                        print("Spiel beendet.")  # Debugging
                        pygame.quit()
                        sys.exit()

    def __draw_objects(self):
        self.__screen.fill((0, 0, 0))
        self.__apple.draw(self.__screen)
        self.__snake.draw(self.__screen)

    def __update_screen(self):
        text = self.__my_font.render(f"{self.__player_name} | Score: {self.__snake.get_score()}", True, (255, 255, 255))
        self.__screen.blit(text, (5, 10))
        pygame.display.update()


# === Spiel starten ===
def start_game(screen):
    while True:  # 🆕 Diese Schleife sorgt für echten Neustart nach Game Over
        player_name = get_player_name(screen)
        game = SnakeGame(player_name)
        final_score, back_to_menu = game.main_loop()  # 🆕 Menü-Option abrufen

        if final_score is not None:
            save_score(player_name, final_score)  # 💾 Score speichern

        if back_to_menu:  # 🆕 Falls der Spieler "M" drückt, zurück ins Menü
            break


# === Hauptfunktion ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
    pygame.display.set_caption("Snake Menü")
    init_db()

    menu = Menu(screen)

    while True:
        menu.draw()
        choice = menu.handle_keys()

        if choice == 0:  # Start Game
            start_game(screen)
        elif choice == 1:  # Bestenliste
            show_highscores(screen)
        elif choice == 2:  # Beenden
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
