import random
import pygame
from game.setting.settings import Settings


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

    def add_obstacle(self, x, y):
        """Fügt ein neues Hindernis hinzu"""
        self.__positions.append((x, y))
        self.__directions.append(random.choice(Settings.directions))  # Zufällige Richtung
        print(f"[DEBUG] Neues Hindernis bei {x}, {y} hinzugefügt!")

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
        from .bot import BotSnake
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