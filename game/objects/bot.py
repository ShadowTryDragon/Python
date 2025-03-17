
import random
import pygame
from game.setting.settings import Settings



class BotSnake:
    def __init__(self, name="Bob"):
        self.__name = name
        self.__positions = [((Settings.screen_width // 3), (Settings.screen_height // 3))]
        self.__direction = random.choice(Settings.directions)
        self.__alive = True
        self.__respawn_time = None
        self.__stuck_time = None
        from game.objects.obstacles import HunterObstacle
        self.__hunter_obstacle = [HunterObstacle() for _ in range(2)]  # 3 Jäger
        from game.objects.snake import Snake
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
