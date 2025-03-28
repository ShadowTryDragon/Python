import random

import pygame

from game.objects.bullet import Bullet
from game.setting.gamecolors import GameColors
from game.setting.settings import Settings


class Snake:
    def __init__(self, start_pos=None, name="Player", is_player=False, position=None):

        """Erstellt eine Schlange mit einer individuellen Startposition und Steuerung."""

        if start_pos is None:
            start_pos = (Settings.screen_width / 2, Settings.screen_height / 2)
        self.__name = name
        self.__length = 1
        self.__positions = [position if position else (0, 0)]  # Falls keine Position gegeben ist, (0,0) nehmen
        self.__direction = (1, 0)  # Standardrichtung: Rechts
        self.__score = 0
        self.__speed = 10
        self.__double_points = False
        self.__flash_time = None
        self.__invisible = False  # ✅ Neue Variable für Unsichtbarkeit
        self.__original_color = GameColors.BODY_COLOR
        self.__color = self.__original_color  # Standardfarbe setzen
        self.__is_player = is_player
        self.__bullets = []  # 🔫 Liste für Kugeln!
        self.__shield = False  # 🛡️ Schutzschild deaktiviert
        self.__max_bullets = 3  # 🔫 Standard-Anzahl an Kugeln
        self.__ammo = 5  # 🔫 Spieler startet mit 5 Schuss

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
        """Setzt die Bewegungsgeschwindigkeit der Schlange."""
        self.__speed = speed
        print(f"[DEBUG] 🏃 Geschwindigkeit geändert: {self.__speed}")

    def activate_shield(self):
        """Aktiviert einen Schutzschild für 5 Sekunden."""
        self.__shield_active = True
        self.__shield_timer = pygame.time.get_ticks() + 5000  # ⏳ Schild läuft 5 Sekunden
        print("[DEBUG] 🛡️ Schild aktiviert!")

    def set_random_direction(self):
        """Wechselt die Richtung zufällig."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Oben, Unten, Links, Rechts
        self.__direction = random.choice(directions)

    def update(self):
        """Überprüft, ob das Schild abgelaufen ist."""
        if self.__shield_active and pygame.time.get_ticks() > self.__shield_timer:
            self.__shield_active = False
            print("[DEBUG] ❌ Schild ist abgelaufen!")

    def is_protected(self):
        """Gibt zurück, ob die Schlange aktuell geschützt ist."""
        return self.__shield_active

    def increase_max_bullets(self, amount):
        self.__max_bullets += amount  # 🔫 Mehr Kugeln sammeln

    def increase_ammo(self, amount):
        """Erhöht die verfügbare Munition."""
        self.__ammo += amount
        print(f"[DEBUG] 🔫 Munition erhöht! Neue Munition: {self.__ammo}")

    def get_ammo(self):
        """Gibt die aktuelle Munition zurück."""
        return self.__ammo

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

    def set_direction(self, direction):
        """✅ Ändert die Bewegungsrichtung der Schlange."""
        self.__direction = direction

    def increase_max_bullets(self, amount):
        self.__max_bullets += amount  # 🔫 Mehr Kugeln sammeln

    def has_ammo(self):
        """Überprüft, ob Munition vorhanden ist."""
        return self.__ammo > 0

    def decrease_ammo(self, amount=1):
        """Reduziert die Munition um eine bestimmte Anzahl."""
        self.__ammo = max(0, self.__ammo - amount)

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

    def get_head_position(self):
        """Gibt die Kopfposition als (x, y)-Tupel zurück."""
        if not self.__positions or not isinstance(self.__positions[0], tuple):
            print(f"[ERROR] Ungültige Position: {self.__positions}")
            return (0, 0)  # ✅ Sicherheitswert zurückgeben
        return self.__positions[0]

    def die(self):
        """Tötet die Schlange, wenn kein Schild aktiv ist."""
        if self.__shield:
            print(f"[DEBUG] 🛡️ {self.__name} hat das Schild benutzt!")
            self.__shield = False  # ❌ Schild verschwindet nach erstem Treffer
        else:
            print(f"[DEBUG] 💀 {self.__name} wurde eliminiert!")
            self.__alive = False
            self.__positions = []  # Entferne die Schlange vom Spielfeld

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

    def get_positions(self):
        """Gibt eine Liste aller Positionen der Schlange zurück."""
        return self.__positions

    def draw(self, surface):
        """Zeichnet die Schlange (unsichtbar oder sichtbar)."""
        if not self.__invisible:  # ✅ Falls unsichtbar, nicht zeichnen
            for index, pos in enumerate(self.__positions):
                r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
                pygame.draw.rect(surface, self.__color if index else GameColors.HEAD_COLOR, r)
                pygame.draw.rect(surface, (93, 216, 228), r, 1)
            for bullet in self.__bullets:
                bullet.draw(surface)

    def shoot(self):
        """Erstellt eine neue Kugel, falls möglich."""
        if self.has_ammo():  # ❗ Verhindert Schießen ohne Munition
            self.decrease_ammo()
            return Bullet(self.__positions[0], self.__direction, self)  # ✅ Richtige Kugel zurückgeben
        return None  # ❌ Falls nicht geschossen werden kann

    def get_name(self):
        return self.__name
