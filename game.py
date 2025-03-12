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
    """Erstellt die Datenbank-Tabellen, falls sie nicht existieren."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()

    # Normale Highscores (für Standard-Spielmodus)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score REAL NOT NULL
        )
    """)

    # Classic Mode Highscores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classic_highscores (
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

def save_classic_score(name, score):
    """Speichert den Spieler-Score für den Classic Mode in die Datenbank."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classic_highscores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()


def get_classic_highscores():
    """Liest die Top 10 Highscores aus der Classic Mode-Tabelle."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM classic_highscores ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores

def get_highscores():
    """Liest die Top 10 Highscores aus der Datenbank."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM highscores ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores

def show_classic_highscores(screen):
    font = pygame.font.SysFont("monospace", 25)
    scores = get_classic_highscores()

    while True:
        screen.fill((0, 0, 0))
        title = font.render("Classic Mode - Bestenliste", True, (255, 255, 255))
        screen.blit(title, (Settings.screen_width // 2 - 100, 50))

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



def update_highscore(name, new_score):
    """Aktualisiert den Highscore eines Spielers, falls der neue Score höher ist."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()

    # 🔍 Prüfen, ob der Spieler existiert und seinen aktuellen Highscore abrufen
    cursor.execute("SELECT score FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()

    if result:
        current_highscore = result[0]
        if new_score > current_highscore:
            cursor.execute("UPDATE highscores SET score = ? WHERE name = ?", (new_score, name))
            print(f"[DEBUG] Neuer Highscore für {name}: {new_score} (alt: {current_highscore})")
        else:
            print(f"[DEBUG] Score {new_score} ist niedriger als Highscore {current_highscore} - kein Update.")
    else:
        # Falls der Name nicht existiert, sollte er neu gespeichert werden (eigentlich nicht nötig, weil Name geprüft wurde)
        cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, new_score))
        print(f"[DEBUG] Neuer Spieler {name} mit Highscore {new_score} hinzugefügt!")

    conn.commit()
    conn.close()


# === Startmenü ===
class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 30)
        self.options = ["Start Game","Classic Mode", "Bestenliste", "Beenden"]
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

def is_name_taken(name):
    """Überprüft, ob der Name bereits in der Datenbank existiert."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()  # Gibt None zurück, falls der Name nicht existiert
    conn.close()
    return result is not None  # True = Name existiert, False = Name ist neu


def get_player_name(screen):
    font = pygame.font.SysFont("monospace", 30)
    name = ""

    while True:
        screen.fill((0, 0, 0))

        # 🖊️ Standard-Text
        text = font.render("Dein Name: " + name, True, (255, 255, 255))
        screen.blit(text, (50, 200))

        # 🔴 Fehlermeldung anzeigen, falls Name bereits vergeben
        if is_name_taken(name):
            error_text = font.render("Name existiert bereits! Wähle einen anderen.", True, (255, 0, 0))
            screen.blit(error_text, (50, 250))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    if not is_name_taken(name):  # ✅ Nur weiter, wenn der Name NEU ist
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
        self.__original_color = GameColors.BODY_COLOR
        self.__color = self.__original_color  # Standardfarbe setzen

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

    def draw(self, surface, color=None):
        """Zeichnet die Schlange auf den Bildschirm."""
        if color is None:
            color = self.__color

        for index, pos in enumerate(self.__positions):
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, color if index else GameColors.HEAD_COLOR, r)
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


class Obstacle:
    def __init__(self, count=3):  # Standardmäßig 3 Hindernisse
        self.__positions = []  # Liste mit Hindernis-Positionen
        self.__directions = []  # Richtung für jedes Hindernis
        self.__count = count  # Anzahl der Hindernisse

        # 🛑 Zufällige Hindernisse auf dem Spielfeld platzieren
        for _ in range(self.__count):
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            self.__positions.append((x_pos, y_pos))

            # 🏃‍♂️ Zufällige Bewegungsrichtung setzen
            self.__directions.append(random.choice(Settings.directions))

    def move(self):
        """Bewegt die Hindernisse zufällig über das Spielfeld."""
        new_positions = []

        for i, (x, y) in enumerate(self.__positions):
            dx, dy = self.__directions[i]

            # 🔄 Neue Position berechnen (mit Spielfeldbegrenzung)
            new_x = (x + dx * Settings.grid_size) % Settings.screen_width
            new_y = (y + dy * Settings.grid_size) % Settings.screen_height

            new_positions.append((new_x, new_y))

            # 🛑 Zufällig Richtung ändern (10% Wahrscheinlichkeit)
            if random.randint(1, 10) == 1:
                self.__directions[i] = random.choice(Settings.directions)

        self.__positions = new_positions  # Neue Positionen speichern

    def get_positions(self):
        """Gibt die Positionen aller Hindernisse zurück."""
        return self.__positions

    def respawn(self):
        """Setzt alle Hindernisse an eine neue Position"""
        self.__positions = []
        for _ in range(self.__count):
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            self.__positions.append((x_pos, y_pos))
        print("[DEBUG] Hindernisse wurden respawnt!")

    def draw(self, surface):
        """Zeichnet die Hindernisse auf dem Spielfeld."""
        for pos in self.__positions:
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, (255, 0, 0), r)  # 🔴 Hindernisse sind rot
            pygame.draw.rect(surface, (0, 0, 0), r, 2)  # 🖤 Schwarzer Rand für bessere Sichtbarkeit


class HunterObstacle:
    def __init__(self):
        """Erzeugt das jagende Hindernis mit zufälliger Startposition."""
        self.__position = ((random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size),
                           (random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size))

        self.__target = None  # Ziel (Spieler oder Bob)
        self.__speed = 1  # 🏃‍♂️ Normale Geschwindigkeit
        self.__boost_end_time = 0  # 🕒 Zeit, wann der Boost endet
        self._last_target_was_bob = False  # ✅ Einfacher Unterstrich → Kein Namens-Mangling!


    def respawn(self):
        """Setzt den Hunter an eine zufällige Position zurück."""
        self.__position = ((random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size),
                           (random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size))
        print("DEBUG: Hunter wurde respawned!")

    def activate_boost(self):
        """Aktiviert den Geschwindigkeits-Boost für 5 Sekunden."""
        print("🔥 Hunter hat einen Apfel getroffen! Boost aktiviert!")
        self.__speed = 5  # 💨 Geschwindigkeit erhöhen
        self.__boost_end_time = pygame.time.get_ticks() + 5000  # ⏳ Boost dauert 5 Sekunden

    def check_boost(self):
        """Überprüft, ob der Boost abgelaufen ist."""
        if pygame.time.get_ticks() > self.__boost_end_time:
            self.__speed = 1  # 🏃‍♂️ Zur normalen Geschwindigkeit zurückkehren

    def set_target(self, target):
        """Setzt das Ziel für den Hunter (z.B. Bob oder den Spieler)."""
        if isinstance(target, BotSnake) and not target.is_alive():
            return  # ❌ Falls Bob tot ist, ignoriere ihn als Ziel

        if isinstance(target, BotSnake):  # ✅ Falls das Ziel Bob ist, merken wir es
            self._last_target_was_bob = True
        else:
            self._last_target_was_bob = False  # Falls es der Spieler ist, resetten

        self.__target = target
        print(f"[DEBUG] Hunter hat ein neues Ziel: {target}")

    def clear_target(self, new_target=None):
        """Löscht das aktuelle Ziel. Falls `new_target` gesetzt ist, wird ein neues Ziel übernommen."""
        if new_target:
            self.set_target(new_target)  # 🔄 Falls ein alternatives Ziel existiert, sofort wechseln
        else:
            self.__target = None
            print("[DEBUG] Hunter hat sein Ziel verloren.")

    def move(self):
        """Bewegt das Hindernis in Richtung des Ziels."""
        if not self.__target or not self.__target.is_alive():
            return  # ❌ Falls kein Ziel gesetzt oder Ziel tot ist, bleibt der Hunter stehen

        target_pos = self.__target.get_positions()[0]  # 🏁 Zielposition
        hunter_x, hunter_y = self.__position
        target_x, target_y = target_pos

        # 🔽 Bewegungsrichtung berechnen
        if hunter_x < target_x:
            hunter_x += Settings.grid_size
        elif hunter_x > target_x:
            hunter_x -= Settings.grid_size
        elif hunter_y < target_y:
            hunter_y += Settings.grid_size
        elif hunter_y > target_y:
            hunter_y -= Settings.grid_size

        # Neue Position setzen
        self.__position = (hunter_x, hunter_y)

        print(f"[DEBUG] Hunter bewegt sich zu {self.__target} → {self.__position}")

    def get_position(self):
        """Gibt die aktuelle Position des Hindernisses zurück."""
        return self.__position

    def draw(self, surface):
        """Zeichnet das Jagd-Hindernis als rotes Quadrat."""
        r = pygame.Rect((self.__position[0], self.__position[1]), (Settings.grid_size, Settings.grid_size))
        pygame.draw.rect(surface, (255, 0, 0), r)  # 🔴 Jäger-Hindernis ist rot
        pygame.draw.rect(surface, (0, 0, 0), r, 2)  # 🖤 Schwarzer Rand für bessere Sichtbarkeit


class BotSnake:
    def __init__(self, name="Bob"):
        self.__name = name
        self.__positions = [((Settings.screen_width // 3), (Settings.screen_height // 3))]
        self.__direction = random.choice(Settings.directions)
        self.__alive = True
        self.__respawn_time = None
        self.__stuck_time = None
        self.__hunter_obstacle = [HunterObstacle() for _ in range(2)]  # 3 Jäger
        self.__snake = Snake()  # ✅ Jetzt existiert `self.__snake`

        print(f"DEBUG: Bob initialisiert mit Position {self.__positions}")



    def is_alive(self):
        """Gibt zurück, ob Bob lebt."""
        return self.__alive

    def get_positions(self):
        """Gibt die aktuellen Positionen von Bob zurück, oder eine Default-Position wenn Bob tot ist."""
        if not self.__positions:  # Falls Bob tot ist oder keine Position hat
            return [(0, 0)]  # 🛑 Eine sichere Standardposition zurückgeben
        return self.__positions

    def move_towards_apple(self, apple_positions):
        """Bewegt sich in Richtung des nächsten Apfels."""
        if not apple_positions:
            return
        if not self.__positions:  # Falls Bob keine Position hat, Abbruch
            return
        head_x, head_y = self.__positions[0]

        target_x, target_y = apple_positions[0]  # Nimmt den ersten Apfel als Ziel

        # Richtung berechnen
        if head_x < target_x:
            self.__direction = Settings.right
        elif head_x > target_x:
            self.__direction = Settings.left
        elif head_y < target_y:
            self.__direction = Settings.down
        elif head_y > target_y:
            self.__direction = Settings.up

    def move(self):
        """Bewegt Bob in die berechnete Richtung."""
        if not self.__alive:
            return

        head_pos = self.__positions[0]
        x, y = self.__direction
        new_pos = ((head_pos[0] + (x * Settings.grid_size)) % Settings.screen_width,
                   (head_pos[1] + (y * Settings.grid_size)) % Settings.screen_height)

        # Falls Bob mit sich selbst kollidiert → sterben
        if new_pos in self.__positions[1:]:
            self.die()
            return

        self.__positions.insert(0, new_pos)
        if len(self.__positions) > 3:  # Bob bleibt klein
            self.__positions.pop()

    def die(self):
        """Bob stirbt und wird nach 20 Sekunden neu gespawnt."""
        if not self.__alive:
            return  # Falls Bob schon tot ist, mache nichts

        self.__alive = False
        self.__positions = []  # ❌ Bob verschwindet vom Spielfeld
        self.__respawn_time = pygame.time.get_ticks() + 5000  # ✅ 20 Sekunden warten
        print(f"[DEBUG] Bob ist gestorben! Respawn um {self.__respawn_time}")

    def is_dead(self):
        """Prüft, ob Bob gerade tot ist."""
        return not self.__alive

    def check_respawn(self):
        """Überprüft, ob Bob wieder erscheinen soll."""
        if self.__respawn_time is None:
            return  # Falls die Respawn-Zeit nicht gesetzt ist, nichts tun

        print(
            f"DEBUG: check_respawn() aufgerufen - Bob ist tot? {self.is_dead()} | Zeit: {pygame.time.get_ticks()} >= {self.__respawn_time}")

        if self.is_dead() and pygame.time.get_ticks() >= self.__respawn_time:
            print("[DEBUG] Bob respawnt jetzt!")
            self.respawn()  # 🛑 Hier sicherstellen, dass respawn() wirklich aufgerufen wird!

    def respawn(self):
        """Bob startet nach 20 Sekunden neu an einer zufälligen Position."""
        self.__positions = [(
            random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size,
            random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
        )]
        self.__direction = random.choice(Settings.directions)
        self.__alive = True
        self.__respawn_time = None  # ✅ Respawn-Zeit zurücksetzen
        print(
            f"[DEBUG] Bob ist neu gestartet mit Position {self.__positions}")  # 🛑 Prüfen, ob Position wirklich gesetzt wird!

        # 🔄 Alle Hunter bekommen Bob wieder als Ziel
        for hunter in self.__hunter_obstacle:
            hunter.set_target(self)
            print(f"[DEBUG] Hunter {hunter} jagt Bob wieder.")

    def draw(self, surface):
        """Zeichnet Bob auf dem Spielfeld."""
        for index, pos in enumerate(self.__positions):
            if not isinstance(pos, tuple) or len(pos) != 2:
                print(f"DEBUG: Ungültige Position {pos} in {self.__name}")  # Debugging
                continue  # Fehlerhafte Positionen überspringen

            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            color = (255, 255, 0) if index == 0 else (200, 200, 0)  # Kopf gelb, Körper dunkler
            pygame.draw.rect(surface, color, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)


# === Snake-Spiel ===
class SnakeGame:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name  # Spielername speichern
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__surface = pygame.Surface(self.__screen.get_size()).convert()
        self.__snake = Snake()
        self.__bob = BotSnake()  # 🆕 Bob hinzufügen
        self.__apple = Apple(count=1, snake=self.__snake)
        self.__my_font = pygame.font.SysFont("monospace", 16)
        self.__running = True  # Flag für Spielstatus
        self.__apple = Apple(count=1, snake=self.__snake)  # Standard-Apfel
        self.__obstacles = Obstacle(count=3)
        self.__hunter_obstacle = [HunterObstacle(), HunterObstacle()]  # Initialisierung

        # 🆕 Spezielle Effekte
        self.__double_points_end_time = None
        self.__speed_boost_end_time = None
        self.__reverse_controls_end_time = None
        self.__countdown_time = 300  # 300 Sekunden (5 Minuten)
        self.__countdown_active = True

        # Gesammelte Äpfel
        self.__collected_apples = 0

    def __update_countdown(self):
        if self.__countdown_active:
            # 🕒 Minuten und Sekunden berechnen (mit int)
            mins, secs = divmod(int(self.__countdown_time), 60)

            # ⏳ Timer-Text erstellen
            timer_text = "Time: {:02d}:{:02d}".format(mins, secs)

            # ⏬ Countdown verringern (jede Sekunde)
            if self.__countdown_time > 0:
                self.__countdown_time -= 1 / 10  # Da das Spiel mit 10 FPS läuft
            else:
                self.__running = False  # ⏳ Zeit abgelaufen -> Game Over

            return timer_text  # 🆕 Gibt den formatierten Timer-String zurück

    def spawn_random_apple(self):
        """Erzeugt einen zufälligen Spezial-Apfel."""
        apple_types = [FakeApple, SuperApple, SugarApple, ReverseApple]
        return random.choice(apple_types)(count=1, snake=self.__snake)

    def should_spawn_mega_apple(self):
        """Prüft, ob der Mega Apple erscheinen soll."""
        return self.__snake.get_score() >= 50 and random.randint(1, 10) == 1  # 10% Wahrscheinlichkeit

    def __positions_overlap(self, pos1, pos2):
        """Prüft, ob zwei Positionen sich genau oder fast genau überlappen."""
        return abs(pos1[0] - pos2[0]) < Settings.grid_size and abs(pos1[1] - pos2[1]) < Settings.grid_size

    def __check_collisions(self):
        """Prüft, ob die Schlange (und optional eine zweite) eine Kollision hat."""

        head_pos = self.__snake.get_head_position()
        bob_positions = self.__bob.get_positions()
        hunter_hit = None  # 🛑 Variable, um zu merken, ob ein Hunter Bob getroffen hat

        # 🛑 Sicherstellen, dass `hunter` und `hunter_pos` immer definiert sind
        hunter = None
        hunter_pos = (0, 0)

        for hunter in self.__hunter_obstacle:  # ✅ `hunter` wird hier sicher definiert
            hunter_pos = hunter.get_position()  # ✅ `hunter_pos` wird hier sicher definiert

        # 💀 Selbst-Kollision (Spieler)
        if head_pos in self.__snake.get_positions()[1:]:
            print("Game Over: Schlange hat sich selbst getroffen!")
            self.__running = False
            return

        # 💀 Selbst-Kollision (Bob)
        if bob_positions in self.__bob.get_positions()[1:]:
            print("DEBUG: Bob hat sich selbst getroffen!")
            self.__bob.die()  # Bob stirbt und respawnt später

        # 🛑 Spieler trifft auf ein Hindernis
        if head_pos in self.__obstacles.get_positions():
            print("Game Over: Schlange hat ein Hindernis getroffen!")
            self.__running = False
            return

        # 🛑 Falls ein Hindernis den Körper trifft → Schlange kürzen!
        for segment in self.__snake.get_positions()[1:]:  # Nur den Körper prüfen, nicht den Kopf
            if segment in self.__obstacles.get_positions():
                print("[DEBUG] Hindernis hat die Schlange getroffen! Länge -1")
                self.__snake.reduce_length(1)
                # ❗ Falls nur noch 1 Segment übrig ist → Game Over
                if len(self.__snake.get_positions()) == 1:
                    print("[DEBUG] Schlange ist zu klein! GAME OVER!")
                    self.__running = False

        # 🛑 Bob trifft auf ein Hindernis
        if bob_positions in self.__obstacles.get_positions():
            print("DEBUG: Bob hat ein Hindernis getroffen!")
            self.__bob.die()

        # 🛑 Bob kollidiert mit dem Spieler
        if bob_positions in self.__snake.get_positions():
            print("DEBUG: Bob kollidiert mit Spieler!")
            self.__bob.die()

        # 🛑 Spieler trifft auf Bob
        if head_pos in self.__bob.get_positions():
            print("Game Over: Spieler kollidiert mit Bob!")
            self.__running = False
            return

        # 🍏 Spieler frisst Apfel
        if head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)
            self.__collected_apples += 1
            for hunter in self.__hunter_obstacle:  # 🔥 Beide Hindernisse aktualisieren ihr Ziel
                hunter.set_target(self.__snake)
            print("Apfel Gesammelt")

            # Spezial-Apfel Timer setzen
            if isinstance(self.__apple, SuperApple):
                self.__double_points_end_time = pygame.time.get_ticks() + 5000
            elif isinstance(self.__apple, SugarApple):
                self.__speed_boost_end_time = pygame.time.get_ticks() + 5000
            elif isinstance(self.__apple, ReverseApple):
                self.__reverse_controls_end_time = pygame.time.get_ticks() + 5000

            # 🏆 Falls ein Mega-Apfel gegessen wurde → +5 Minuten
            if isinstance(self.__apple, MegaApple):
                self.__countdown_time += 300
                print("[DEBUG] Mega Apple gegessen! +5 Minuten hinzugefügt.")

            # ⏳ Falls genau 10, 20, 30 Äpfel gesammelt wurden → +2 Minuten
            if self.__collected_apples % 10 == 0:
                self.__countdown_time += 120
                print(f"[DEBUG] {self.__collected_apples} Äpfel gesammelt! +2 Minuten hinzugefügt.")

            # 🆕 Neuen Apfel generieren
            if self.should_spawn_mega_apple():
                self.__apple = MegaApple(snake=self.__snake)
            elif random.randint(1, 5) == 1:
                self.__apple = self.spawn_random_apple()
            else:
                self.__apple = Apple(count=1, snake=self.__snake)

            # 🛑 Falls ein Hindernis einen Apfel trifft → Apfel neu platzieren!
        for obstacle_pos in self.__obstacles.get_positions():
            if obstacle_pos in self.__apple.get_positions():
                print("[DEBUG] Apfel wurde von einem Hindernis getroffen! Neuer Apfel erscheint.")
                self.__apple.relocate_apple(self.__snake, self.__obstacles)

        # 🍏 Bob frisst Apfel
        if bob_positions and bob_positions[0] in self.__apple.get_positions():
            print("DEBUG: Bob hat einen Apfel gefressen!")
            self.__apple = Apple(count=1, snake=self.__snake)  # 🆕 Neuer Apfel erscheint
            for hunter in self.__hunter_obstacle:  # 🔥 Beide Hindernisse aktualisieren ihr Ziel
                hunter.set_target(self.__bob)

                # 🛑 Wenn Bob mit einem Hunter kollidiert (egal welcher Körperteil)
                for segment in self.__bob.get_positions():
                    for hunter in self.__hunter_obstacle:  # ✅ Stelle sicher, dass alle Hunter überprüft werden
                        hunter_pos = hunter.get_position()

                        if self.__positions_overlap(hunter_pos, segment):
                            print("[DEBUG] Hunter hat Bob erwischt! Bob stirbt!")
                            self.__bob.die()
                            hunter_hit = hunter  # ✅ Speichert das `HunterObstacle`-Objekt
                            break  # ⛔ Verhindert doppelte Treffer

                # 🔥 Wenn ein Hunter Bob getroffen hat, respawnen ALLE Hunter
                if hunter_hit is not None:
                    for h in self.__hunter_obstacle:  # ✅ Respawn für alle Hunter
                        h.clear_target()
                        h.respawn()

            # 🛑 Wenn ein Hunter die Schlange trifft (egal welcher Körperteil)
            for segment in self.__snake.get_positions():
                for hunter in self.__hunter_obstacle:
                    hunter_pos = hunter.get_position()

                    if self.__positions_overlap(hunter_pos, segment):
                        # 💀 Falls der Kopf getroffen wird → Game Over
                        if segment == self.__snake.get_head_position():
                            print("[DEBUG] Hunter hat den Spieler-Kopf getroffen! GAME OVER!")
                            self.__running = False
                        else:
                            # 🟡 Falls ein Körperteil getroffen wird → Länge um 1 reduzieren
                            print("[DEBUG] Hunter hat ein Körperteil der Schlange getroffen! Länge -1")
                            self.__snake.reduce_length(1)

                            # ❗ Falls nur noch 1 Segment übrig ist → Game Over
                            if len(self.__snake.get_positions()) == 1:
                                print("[DEBUG] Schlange ist zu klein! GAME OVER!")
                                self.__running = False

        # 🍏 Hunter trifft Apfel (BOOST!)
        for hunter in self.__hunter_obstacle:
            if hunter.get_position() in self.__apple.get_positions():
                hunter.activate_boost()  # 💨 Hunter wird schneller!

        # 🛑 Wenn ein Hunter auf ein Hindernis trifft
        for obstacle_pos in self.__obstacles.get_positions():
            if self.__positions_overlap(hunter_pos, obstacle_pos):
                print("Hunter hat ein Hindernis getroffen! Beide respawnen!")
                # 🔄 Hindernis und Hunter respawnen
                hunter.respawn()
                self.__obstacles.respawn()  # ❗ Falls `Obstacle` kein `respawn()` hat, erstelle es!

    def __update_effects(self):
        current_time = pygame.time.get_ticks()

        # 🕒 SuperApple-Effekt beenden
        if self.__double_points_end_time and current_time >= self.__double_points_end_time:
            self.__double_points_end_time = None
            self.__snake.set_double_points(False)
            print("[DEBUG] Super Apple Effekt vorbei. Punkte normal.")

        # 🕒 SugarApple-Effekt beenden (Geschwindigkeit)
        if self.__speed_boost_end_time and current_time >= self.__speed_boost_end_time:
            self.__speed_boost_end_time = None
            self.__snake.set_speed(10)
            print("[DEBUG] Sugar Apple Effekt vorbei. Geschwindigkeit normal.")

        # 🕒 ReverseApple-Effekt beenden (Steuerung)
        if self.__reverse_controls_end_time and current_time >= self.__reverse_controls_end_time:
            self.__reverse_controls_end_time = None
            Settings.up, Settings.down = (0, -1), (0, 1)
            Settings.left, Settings.right = (-1, 0), (1, 0)
            print("[DEBUG] Reverse Apple Effekt vorbei. Steuerung wieder normal.")

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
            self.__bob.move_towards_apple(self.__apple.get_positions())
            self.__bob.move()
            self.__bob.check_respawn()  # Falls Bob tot ist, respawnt er nach 20 Sek
            self.__check_collisions()
            self.__draw_objects()
            self.__update_screen()
            self.__snake.update_flash()
            self.__update_effects()
            self.__update_countdown()
            self.__obstacles.move()
            for hunter in self.__hunter_obstacle:  # 🔥 Für jedes Hindernis `move()` aufrufen
                hunter.move()

            # 🆕 Falls die Zeit abgelaufen ist, Spiel beenden
            if self.__countdown_time <= 0:
                self.__running = False

        print("Game Over: Zeit abgelaufen!")  # Debugging
        final_score, back_to_menu, new_name = self.show_game_over_screen()
        return final_score, back_to_menu, new_name

    def show_game_over_screen(self):
        """Zeigt den Game Over Bildschirm mit der Möglichkeit, mit dem gleichen Namen weiterzuspielen."""
        font = pygame.font.SysFont("monospace", 30)
        final_score = self.__snake.get_score()

        while True:
            self.__screen.fill((0, 0, 0))

            # 🎮 Game Over Nachricht
            text1 = font.render("GAME OVER", True, (255, 0, 0))
            text2 = font.render(f"Score: {final_score}", True, (255, 255, 255))
            text3 = font.render("Enter: Neustart | N: Neuer Name | M: Menü", True, (200, 200, 200))

            self.__screen.blit(text1, (Settings.screen_width // 2 - text1.get_width() // 2, 100))
            self.__screen.blit(text2, (Settings.screen_width // 2 - text2.get_width() // 2, 160))
            self.__screen.blit(text3, (Settings.screen_width // 2 - text3.get_width() // 2, 220))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # 🎮 Mit gleichem Namen weiterspielen
                        print(f"Spiel wird mit {self.__player_name} neugestartet...")
                        return final_score, False, self.__player_name  # Gleiches Spiel, gleicher Name
                    elif event.key == pygame.K_n:  # ✏️ Neuer Name wählen
                        print("Neuen Namen eingeben...")
                        return final_score, False, None  # Name muss neu eingegeben werden
                    elif event.key == pygame.K_m:  # 🏠 Zurück ins Menü
                        print("Zurück ins Menü.")
                        return final_score, True, None  # Spieler geht ins Menü zurück

    def __draw_objects(self):
        self.__screen.fill((0, 0, 0))
        self.__apple.draw(self.__screen)
        self.__snake.draw(self.__screen)
        self.__bob.draw(self.__screen)  # 🆕 Bob wird gezeichnet
        self.__obstacles.draw(self.__screen)
        for hunter in self.__hunter_obstacle:  # 🔥 Beide Jäger zeichnen!
            hunter.draw(self.__screen)

    def __update_screen(self):
        # 🎮 Score-Text definieren
        score_text = f"{self.__player_name} | Score: {self.__snake.get_score()}"

        # 🕒 Minuten & Sekunden für den Timer berechnen
        mins, secs = divmod(int(self.__countdown_time), 60)
        timer_text = f"Time: {mins:02d}:{secs:02d}"

        # 🖊️ Beide Texte kombinieren
        full_text = score_text + " | " + timer_text

        # 🖥️ Text rendern
        text_surface = self.__my_font.render(full_text, True, (255, 255, 255))

        # 📍 Text oben links zeichnen
        self.__screen.blit(text_surface, (5, 10))

        pygame.display.update()


# === Spiel starten ===
def start_game(screen):
    player_name = get_player_name(screen)  # 🆕 Initialen Namen holen

    while True:
        game = SnakeGame(player_name)
        final_score, back_to_menu, new_name = game.main_loop()

        if final_score is not None:
            if new_name == player_name:  # 🎮 Spieler bleibt beim gleichen Namen → Highscore updaten
                update_highscore(player_name, final_score)
            else:  # 🆕 Neuer Name → Highscore separat speichern
                save_score(player_name, final_score)

        if back_to_menu:  # 🏠 Falls Spieler "M" drückt, zurück ins Menü
            break

        if new_name is None:  # 🎮 Falls Spieler "N" drückt, neuen Namen wählen
            player_name = get_player_name(screen)  # Spieler gibt neuen Namen ein


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

        if choice == 0:  # Start Game (mit allen Features)
            start_game(screen)
        elif choice == 1:  # Classic Mode
            from classic import start_classic_mode
            start_classic_mode()  # ✅ Startet jetzt Classic Mode aus `classic_mode.py`
        elif choice == 2:  # Bestenliste
            show_highscores(screen)
        elif choice == 3:  # Beenden
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
