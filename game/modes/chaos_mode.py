import pygame
import random

from game.objects.mine import Mine
from game.settings import Settings
from game.objects.snake import Snake
from game.objects.apple import Apple
from game.objects.obstacles import Obstacle
from game.playerinputs import handle_snake_input

class ChaosMode:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name
        self.__mines = []  # ✅ Liste für Minen
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__snake = Snake()
        self.__apple = Apple(count=4, snake=self.__snake)
        self.__obstacle = Obstacle(count=random.randint(2, 6))  # ✅ Hindernisse beim Start erzeugen
        self.__running = True
        self.__event_timer = pygame.time.get_ticks() + random.randint(20000, 30000)  # Erstes Event nach 20-30 Sekunden
        self.__speed_boost_active = False
        self.__slow_motion_active = False
        self.__reverse_active = False

    def trigger_random_event(self):
        """Löst ein zufälliges Ereignis aus und setzt Timer für die Deaktivierung"""
        event_type = random.choice(
            ["tornado", "meteor", "stealth", "speed", "slow", "mines", "reverse", "no_apples", "hunting_apple"])

        if event_type == "tornado":
            print("[CHAOS] 🌪 Tornado! Alle Äpfel neu platziert!")
            self.__apple.randomize_positions()

        elif event_type == "meteor":
            num_obstacles = random.randint(2, 6)
            print(f"[CHAOS] 🌠 Meteor! {num_obstacles} neue Hindernisse erscheinen!")

            for _ in range(num_obstacles):
                x = random.randint(0, Settings.grid_width - 1) * Settings.grid_size
                y = random.randint(0, Settings.grid_height - 1) * Settings.grid_size
                self.__obstacle.add_obstacle(x, y)

            pygame.time.set_timer(pygame.USEREVENT + 6, 20000, loops=1)  # ✅ Hindernisse nach 20 Sekunden entfernen

        elif event_type == "stealth":
            print("[CHAOS] 🕵️ Stealth Mode! Die Schlange ist unsichtbar!")
            self.__snake.set_invisible(True)
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000, loops=1)  # ✅ Unsichtbarkeit nach 5 Sekunden beenden

        elif event_type == "speed":
            print("[CHAOS] 🏁 Speed Boost! Die Schlange ist doppelt so schnell!")
            self.__clock.tick(15)
            pygame.time.set_timer(pygame.USEREVENT + 2, 10000,
                                  loops=1)  # ✅ Geschwindigkeit nach 10 Sekunden normalisieren

        elif event_type == "slow":
            print("[CHAOS] ⏳ Slow Motion! Alles läuft langsamer!")
            self.__clock.tick(5)
            pygame.time.set_timer(pygame.USEREVENT + 3, 5000,
                                  loops=1)  # ✅ Normalgeschwindigkeit nach 5 Sekunden wiederherstellen

        elif event_type == "mines":
            print("[CHAOS] 💣 Minen erscheinen auf dem Spielfeld!")
            for _ in range(5):
                x = random.randint(0, Settings.grid_width - 1) * Settings.grid_size
                y = random.randint(0, Settings.grid_height - 1) * Settings.grid_size
                self.__mines.append(Mine(x, y))
            pygame.time.set_timer(pygame.USEREVENT + 7, 20000, loops=1)  # ✅ Minen nach 20 Sekunden entfernen

        elif event_type == "reverse":
            print("[CHAOS] 🔄 Reverse-Steuerung! Links & Rechts sind vertauscht!")
            Settings.left, Settings.right = Settings.right, Settings.left
            Settings.up, Settings.down = Settings.down, Settings.up
            pygame.time.set_timer(pygame.USEREVENT + 4, 7000, loops=1)  # ✅ Steuerung nach 7 Sekunden normalisieren

        elif event_type == "no_apples":
            print("[CHAOS] ❌ Keine Äpfel für 10 Sekunden!")
            self.__apple = None
            pygame.time.set_timer(pygame.USEREVENT + 5, 10000, loops=1)  # ✅ Nach 10 Sekunden neue Äpfel generieren

        elif event_type == "hunting_apple":
            print("[CHAOS] 🏹 Jagd-Modus! Ein Apfel bewegt sich!")
            self.__apple = Apple(count=1, snake=self.__snake, moving=True)
            pygame.time.set_timer(pygame.USEREVENT + 8, 15000, loops=1)  # ✅ Jagd-Apfel nach 15 Sekunden entfernen

        self.__event_timer = pygame.time.get_ticks() + random.randint(20000, 30000)  # Nächstes Event in 20-30 Sekunden

    def main_loop(self):
        """Hauptspiel-Schleife für den Chaos Modus"""
        while self.__running:
            self.__clock.tick(10)
            events = pygame.event.get()
            self.__running = handle_snake_input(events, self.__snake)
            self.__obstacle.move()

            # Prüfe zufällige Events
            if pygame.time.get_ticks() >= self.__event_timer:
                self.trigger_random_event()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.__running = False

                elif event.type == pygame.USEREVENT + 1:  # ✅ Unsichtbarkeit beenden
                    print("[CHAOS] 🕵️ Unsichtbarkeit ist vorbei!")
                    self.__snake.set_invisible(False)
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # ❌ Timer stoppen
                    pygame.event.clear(pygame.USEREVENT + 1)  # ✅ Alle ausstehenden Events entfernen

                elif event.type == pygame.USEREVENT + 2:  # ✅ Geschwindigkeit normalisieren
                    print("[CHAOS] 🏁 Speed Boost ist vorbei!")
                    self.__clock.tick(10)
                    self.__speed_boost_active = False  # ✅ Variable zurücksetzen
                    pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                    pygame.event.clear(pygame.USEREVENT + 2)  # ✅ Alle ausstehenden Events entfernen

                elif event.type == pygame.USEREVENT + 3:  # ✅ Slow Motion beenden
                    print("[CHAOS] ⏳ Slow Motion ist vorbei!")
                    self.__clock.tick(10)
                    self.__slow_motion_active = False
                    pygame.time.set_timer(pygame.USEREVENT + 3, 0)
                    pygame.event.clear(pygame.USEREVENT + 3)

                elif event.type == pygame.USEREVENT + 4:  # ✅ Steuerung normalisieren
                    print("[CHAOS] 🔄 Reverse-Steuerung beendet!")
                    Settings.left, Settings.right = (-1, 0), (1, 0)
                    Settings.up, Settings.down = (0, -1), (0, 1)
                    self.__reverse_active = False
                    pygame.time.set_timer(pygame.USEREVENT + 4, 0)
                    pygame.event.clear(pygame.USEREVENT + 4)

                elif event.type == pygame.USEREVENT + 5:  # ✅ Äpfel wieder generieren
                    print("[CHAOS] 🍏 Äpfel sind wieder da!")
                    self.__apple = Apple(count=1, snake=self.__snake)
                    pygame.time.set_timer(pygame.USEREVENT + 5, 0)
                    pygame.event.clear(pygame.USEREVENT + 5)

                elif event.type == pygame.USEREVENT + 6:  # ✅ Meteor-Hindernisse entfernen
                    print("[CHAOS] ⏳ Meteor-Hindernisse verschwinden wieder!")
                    self.__obstacle.respawn()
                    pygame.time.set_timer(pygame.USEREVENT + 6, 0)
                    pygame.event.clear(pygame.USEREVENT + 6)

                elif event.type == pygame.USEREVENT + 7:  # ✅ Minen entfernen
                    print("[CHAOS] 💣 Minen verschwinden wieder!")
                    self.__mines = []  # ✅ Minen aus der Liste entfernen
                    pygame.time.set_timer(pygame.USEREVENT + 7, 0)
                    pygame.event.clear(pygame.USEREVENT + 7)

                elif event.type == pygame.USEREVENT + 8:  # ✅ Jagd-Apfel entfernen
                    print("[CHAOS] 🏹 Jagd-Apfel verschwunden!")
                    self.__apple = Apple(count=1, snake=self.__snake)
                    pygame.time.set_timer(pygame.USEREVENT + 8, 0)
                    pygame.event.clear(pygame.USEREVENT + 8)

            self.__snake.move()
            if self.__apple:
                self.__check_collisions()

            self.__draw_objects()

    def __check_collisions(self):
        """Prüft Kollisionen mit Hindernissen & Äpfeln"""
        head_pos = self.__snake.get_head_position()

        # ✅ Kollisionscheck mit Hindernissen (Hindernis-Positionen abrufen!)
        for pos in self.__obstacle.get_positions():  # ✅ Richtige Iteration!
            if pos == head_pos:
                print("[CHAOS] 💀 Du bist gegen ein Hindernis gestoßen! GAME OVER!")
                self.__running = False

                # ✅ Kollisionscheck mit Minen
                for mine in self.__mines:
                    if mine.get_position() == head_pos:
                        mine.trigger_explosion()  # 🔥 Explosion starten!

                # ✅ Aktualisiere Minenstatus nach der Bewegung
                for mine in self.__mines[:]:  # Durch eine Kopie iterieren, um sicher zu entfernen
                    explosion = mine.update(self.__snake)
                    if explosion == "explode":
                        print("[💀] BOOM! Spieler getroffen! GAME OVER!")
                        self.__running = False  # ❌ Spiel beenden!

        # ✅ Apfel essen (Falls der Kopf auf einem Apfel landet)
        if self.__apple and head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)
            self.__apple.randomize_positions()

        # Apfel essen
        if self.__apple and head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)
            self.__apple.randomize_positions()

    def __draw_objects(self):
        """Zeichnet Spielfeld-Elemente"""
        self.__screen.fill((0, 0, 0))

        if self.__apple:
            self.__apple.draw(self.__screen)


        # ✅ Richtige Hindernis-Darstellung
        for pos in self.__obstacle.get_positions():
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(self.__screen, (255, 0, 0), r)  # 🔴 Hindernisse rot
            pygame.draw.rect(self.__screen, (0, 0, 0), r, 2)  # 🖤 Schwarzer Rand

            # ✅ Minen korrekt zeichnen
            for mine in self.__mines:
                mine.update(self.__snake)  # 🔄 Blinken aktualisieren & Explosion prüfen
                mine.draw(self.__screen)

        self.__snake.draw(self.__screen)
        pygame.display.flip()

