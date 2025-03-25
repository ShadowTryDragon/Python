import random
import pygame
import pygame.sndarray
from game.objects.apple import Apple
from game.objects.mine import Mine
from game.objects.obstacles import Obstacle
from game.objects.snake import Snake
from game.setting.playerinputs import handle_snake_input
from game.setting.settings import Settings

class ChaosMode:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name
        self.__mines = []
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__snake = Snake()
        self.__apple = Apple(count=4, snake=self.__snake)
        self.__obstacle = Obstacle(count=random.randint(2, 6))
        self.__running = True
        self.__reverse_active = False
        self.__speed_boost_active = False
        self.__slow_motion_active = False
        self.bg_color = [30, 30, 30]
        self.color_transition_speed = 0.002
        self.target_color = [random.randint(50, 255) for _ in range(3)]
        self.__obstacle_sprite = pygame.image.load("game/icons/sprites/obstacle.png").convert_alpha()
        self.__obstacle_sprite = pygame.transform.scale(self.__obstacle_sprite,
                                                        (Settings.grid_size, Settings.grid_size))
        self.__active_effects = {}  # 🎯 Hält alle aktiven Effekte & Endzeiten
        self.__event_timer = pygame.time.get_ticks() + random.randint(20000, 30000)

    def trigger_random_event(self):
        """Löst ein zufälliges Ereignis aus und setzt Timer für die Deaktivierung"""
        event_type = random.choice([
            "tornado", "meteor", "stealth", "speed", "slow",
            "mines", "reverse", "no_apples", "hunting_apple"
        ])

        duration = {
            "stealth": 5000,
            "speed": 10000,
            "slow": 5000,
            "reverse": 7000,
            "no_apples": 10000,
            "hunting_apple": 15000,
            "meteor": 20000,
            "mines": 20000
        }.get(event_type, 5000)  # Standardwert 5 Sekunden falls nicht definiert

        if event_type == "tornado":
            print("[CHAOS] 🌪 Tornado! Alle Äpfel neu platziert!")
            self.__apple.randomize_positions()

        elif event_type == "meteor":
            print("[CHAOS] 🌠 Meteor! Neue Hindernisse erscheinen!")
            for _ in range(min(random.randint(2, 6), 10)):
                x = random.randint(0, Settings.grid_width - 1) * Settings.grid_size
                y = random.randint(0, Settings.grid_height - 1) * Settings.grid_size
                self.__obstacle.add_obstacle(x, y)
            self.start_effect("meteor", duration)

        elif event_type == "stealth":
            print("[CHAOS] 🕵️ Stealth Mode! Die Schlange ist unsichtbar!")
            self.__snake.set_invisible(True)
            self.start_effect("stealth", duration)

        elif event_type == "speed":
            print("[CHAOS] 🏁 Speed Boost! Die Schlange ist schneller!")
            self.__speed_boost_active = True
            self.start_effect("speed", duration)

        elif event_type == "slow":
            print("[CHAOS] ⏳ Slow Motion! Alles läuft langsamer!")
            self.__slow_motion_active = True
            self.start_effect("slow", duration)

        elif event_type == "mines":
            if len(self.__mines) < 10:
                print("[CHAOS] 💣 Minen erscheinen!")
                for _ in range(5):
                    x = random.randint(0, Settings.grid_width - 1) * Settings.grid_size
                    y = random.randint(0, Settings.grid_height - 1) * Settings.grid_size
                    self.__mines.append(Mine(x, y))
            self.start_effect("mines", duration)

        elif event_type == "reverse":
            print("[CHAOS] 🔄 Reverse-Steuerung aktiviert!")
            Settings.left, Settings.right = Settings.right, Settings.left
            Settings.up, Settings.down = Settings.down, Settings.up
            self.start_effect("reverse", duration)

        elif event_type == "no_apples":
            print("[CHAOS] ❌ Keine Äpfel für 10 Sekunden!")
            self.saved_apple_positions = self.__apple.get_positions()
            self.__apple._positions = []
            self.start_effect("no_apples", duration)

        elif event_type == "hunting_apple":
            print("[CHAOS] 🏹 Jagd-Apfel!")
            self.__apple = Apple(count=1, snake=self.__snake, moving=True)
            self.start_effect("hunting_apple", duration)

        self.__event_timer = pygame.time.get_ticks() + random.randint(20000, 30000)

    def main_loop(self):
        """Hauptspiel-Schleife"""
        while self.__running:
            self.__clock.tick(15 if self.__speed_boost_active else 5 if self.__slow_motion_active else 10)
            self.__running = handle_snake_input(pygame.event.get(), self.__snake, battle_mode=False)
            self.__obstacle.move()

            if pygame.time.get_ticks() >= self.__event_timer:
                self.trigger_random_event()

            self.__snake.move()
            if self.__apple:
                self.__check_collisions()
            self.__draw_objects()

    def start_effect(self, effect_name, duration):
        """Startet einen Effekt und setzt einen Timer."""
        end_time = pygame.time.get_ticks() + duration
        self.__active_effects[effect_name] = end_time
        pygame.time.set_timer(pygame.USEREVENT + len(self.__active_effects), duration, loops=1)

    def handle_events(self):
        """Behandelt Chaos-Events und beendet sie automatisch."""
        current_time = pygame.time.get_ticks()

        for effect, end_time in list(self.__active_effects.items()):
            if current_time >= end_time:
                self.stop_effect(effect)
                del self.__active_effects[effect]  # Lösche den Effekt aus der Liste

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.__running = False

    def stop_effect(self, effect_name):
        """Beendet einen laufenden Effekt."""
        print(f"[CHAOS] ❌ Effekt beendet: {effect_name}")

        if effect_name == "stealth":
            self.__snake.set_invisible(False)

        elif effect_name == "speed":
            self.__speed_boost_active = False

        elif effect_name == "slow":
            self.__slow_motion_active = False

        elif effect_name == "reverse":
            Settings.left, Settings.right = (-1, 0), (1, 0)
            Settings.up, Settings.down = (0, -1), (0, 1)

        elif effect_name == "no_apples":
            if hasattr(self, "saved_apple_positions"):
                self.__apple._positions = self.saved_apple_positions
                del self.saved_apple_positions
            else:
                self.__apple.randomize_positions()

        elif effect_name == "hunting_apple":
            self.__apple = Apple(count=1, snake=self.__snake)

        elif effect_name == "meteor":
            self.__obstacle.respawn()

        elif effect_name == "mines":
            self.__mines = []

        pygame.time.set_timer(pygame.USEREVENT + len(self.__active_effects), 0)  # ❌ Timer deaktivieren

    def __check_collisions(self):
        """Prüft Kollisionen mit Hindernissen, Minen & Äpfeln"""
        head_pos = self.__snake.get_head_position()

        if head_pos in self.__obstacle.get_positions():
            print("[CHAOS] 💀 Hindernis getroffen! GAME OVER!")
            self.__running = False

        for mine in self.__mines[:]:
            if mine.get_position() == head_pos:
                mine.trigger_explosion()
                self.__running = False

        if self.__apple and head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)
            self.__apple.randomize_positions()

    def __draw_objects(self):
        """Zeichnet alle Spielobjekte mit animiertem Hintergrund."""
        self.animate_background()  # 🌈 Hintergrundfarbe animieren
        self.__screen.fill(tuple(map(int, self.bg_color)))  # 🎨 Hintergrund setzen

        if self.__apple:
            self.__apple.draw(self.__screen)  # 🍏 Äpfel zeichnen

        # ✅ Hindernisse korrekt zeichnen
        for pos in self.__obstacle.get_positions():
            self.__screen.blit(self.__obstacle_sprite, pos)  # 🖼 Hindernis-Sprite zeichnen

        # ✅ Minen korrekt zeichnen
        for mine in self.__mines:
            mine.update(self.__snake)  # 🔄 Blinken & Explosion prüfen
            mine.draw(self.__screen)

        self.__snake.draw(self.__screen)  # 🐍 Schlange zeichnen
        pygame.display.flip()  # 🖥 Bildschirm aktualisieren

    def animate_background(self):
        """Sanfter Übergang der Hintergrundfarbe."""
        for i in range(3):  # Für R, G, B-Werte
            self.bg_color[i] += (self.target_color[i] - self.bg_color[i]) * self.color_transition_speed

        # Falls die Ziel-Farbe fast erreicht wurde, eine neue Farbe wählen
        if all(abs(self.bg_color[i] - self.target_color[i]) < 5 for i in range(3)):
            self.target_color = [random.randint(50, 255) for _ in range(3)]


