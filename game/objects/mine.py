import pygame
import random
from game.setting.settings import Settings

class Mine:
    def __init__(self, x, y):
        """Erstellt eine Mine an einer bestimmten Position."""
        self.__position = (x, y)
        self.__color = (255, 255, 0)  # 🟡 Standardfarbe: Gelb
        self.__active = True
        self.__blink_time = None  # 🕒 Startzeit für Blinken
        self.__exploding = False

    def get_position(self):
        """Gibt die Position der Mine zurück."""
        return self.__position

    def trigger_explosion(self):
        """Startet den Blink-Effekt vor der Explosion."""
        if self.__active and not self.__exploding:
            print("[💥] Mine wurde ausgelöst! Blink-Phase startet!")
            self.__blink_time = pygame.time.get_ticks()  # 🕒 Startzeit merken
            self.__exploding = True

    def update(self):
        """Überprüft, ob die Explosion starten soll."""
        if self.__exploding:
            elapsed_time = pygame.time.get_ticks() - self.__blink_time
            if elapsed_time > 1000:  # 🔥 Nach 1 Sekunde explodieren
                print("[💀] BOOM! Mine explodiert!")
                self.__active = False  # ❌ Mine wird entfernt
            elif elapsed_time % 200 < 100:  # ⚡ Blinken alle 200ms
                self.__color = (255, 0, 0)  # 🔴 Rot blinken
            else:
                self.__color = (255, 255, 0)  # 🟡 Zurück zu Gelb

    def draw(self, surface):
        """Zeichnet die Mine auf das Spielfeld."""
        if self.__active:
            r = pygame.Rect(self.__position, (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, self.__color, r)
            pygame.draw.rect(surface, (0, 0, 0), r, 2)  # Schwarzer Rand für Kontrast
