import pygame

from game.setting.settings import Settings
from game.ui.menuApple import MenuApple


class MenuSnake:
    def __init__(self,path):
        """Erstellt eine animierte Schlange, die sich langsam um die Menü-Optionen schlängelt."""
        self.length = 15 # Länge der Schlange
        self.positions = [(Settings.screen_width // 2 - 220 + i * 20, 160) for i in range(self.length)]
        self.direction = (1, 0)  # Startbewegung nach rechts
        self.speed = 10  # Langsame Bewegung
        self.move_delay = 5  # 🔄 Die Schlange bewegt sich nur alle X Frames
        self.move_counter = 0  # Zählt Frames, um Bewegung zu steuern
        self.color = (0, 255, 0)  # Schlange ist grün
        self.counter = 0


        # ✅ Pfad KORREKT um die Texte herumgelegt:
        self.path = [
            (Settings.screen_width // 2 - 250, 160),  # Start links oben
            (Settings.screen_width // 2 + 250, 160),  # Nach rechts (über den Text)
            (Settings.screen_width // 2 + 250, 550),  # Nach unten (neben dem letzten Menüpunkt)
            (Settings.screen_width // 2 - 250, 550),  # Nach links (unter dem Menü)
            (Settings.screen_width // 2 - 250, 160),  # Zurück nach oben
        ]
        self.path_index = 0  # Startpunkt im Pfad
        self.apple = MenuApple(self.path)  # ✅ Jetzt existiert `self.path`

    def move(self):
        """Bewegt die Schlange langsam entlang des definierten Pfads."""
        self.move_counter += 1
        if self.move_counter < self.move_delay:
            return  # ❌ Warten, bis genug Frames vergangen sind
        self.move_counter = 0  # 🔄 Zurücksetzen für die nächste Bewegung

        if self.path_index < len(self.path) - 1:
            next_point = self.path[self.path_index + 1]
            head_x, head_y = self.positions[0]

            # Berechne die Bewegung zur nächsten Wegmarke
            dx = next_point[0] - head_x
            dy = next_point[1] - head_y

            # Bewegungsgeschwindigkeit normalisieren
            if abs(dx) > 0:
                dx = self.speed if dx > 0 else -self.speed
            if abs(dy) > 0:
                dy = self.speed if dy > 0 else -self.speed

            new_head = (head_x + dx, head_y + dy)

            # Falls das Ziel erreicht wurde, zum nächsten Path-Index springen
            if abs(new_head[0] - next_point[0]) < self.speed and abs(new_head[1] - next_point[1]) < self.speed:
                self.path_index += 1

            # Schlange aktualisieren
            self.positions.insert(0, new_head)
            if len(self.positions) > self.length:
                self.positions.pop()

                # 🍏 Kollision mit Apfel prüfen
                if new_head == self.apple.position:
                    print(f"[DEBUG] Apfel gefressen! neuer Stand: {self.counter}")
                    self.counter += 1
                    self.apple.relocate()  # Apfel neu platzieren

        # Falls das Ende des Pfads erreicht wurde, von vorne beginnen
        if self.path_index >= len(self.path) - 1:
            self.path_index = 0

    def draw(self, screen):
        """Zeichnet die Menü-Schlange und den Apfel."""
        self.apple.draw(screen)  # 🍏 Apfel zeichnen
        for i, pos in enumerate(self.positions):
            size = 15 if i == 0 else 12  # Kopf etwas größer
            pygame.draw.circle(screen, self.color, pos, size)
