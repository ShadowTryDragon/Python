import pygame
import random
import sys

from game.objects.snake import Snake
from game.settings import Settings
from game.objects.bot import BotSnake
from game.objects.apple import Apple, FakeApple,SuperApple,ReverseApple,SugarApple,MegaApple
from game.objects.obstacles import HunterObstacle, Obstacle
from game.playerinputs import handle_snake_input


class SnakeGame:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name  # Spielername speichern
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__surface = pygame.Surface(self.__screen.get_size()).convert()
        self.__hunter_obstacle = [HunterObstacle(), HunterObstacle()]  # Initialisierung
        self.__snake = Snake()
        self.__bob = BotSnake()  # 🆕 Bob hinzufügen
        self.__apple = Apple(count=1, snake=self.__snake)
        self.__my_font = pygame.font.SysFont("monospace", 16)
        self.__running = True  # Flag für Spielstatus
        self.__apple = Apple(count=1, snake=self.__snake)  # Standard-Apfel
        self.__obstacles = Obstacle(count=3)

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
        """Prüft, ob zwei Positionen sich genau überlappen."""
        overlap_x = abs(pos1[0] - pos2[0]) < (Settings.grid_size // 2)  # Genauere Toleranz
        overlap_y = abs(pos1[1] - pos2[1]) < (Settings.grid_size // 2)

        return overlap_x and overlap_y

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

                # 🛑 Wenn ein Hunter die Schlange trifft (aber nur noch, wenn der Kopf getroffen wird)
                for hunter in self.__hunter_obstacle:
                    hunter_pos = hunter.get_position()

                    # 💀 Prüfen, ob der Kopf getroffen wurde
                    if self.__positions_overlap(hunter_pos, self.__snake.get_head_position()):
                        print("[DEBUG] Hunter hat den Spieler-Kopf getroffen! GAME OVER!")
                        self.__running = False
                        return  # ✅ Spiel sofort beenden

                # 🔥 Wenn ein Hunter Bob getroffen hat, respawnen ALLE Hunter
                if hunter_hit is not None:
                    for h in self.__hunter_obstacle:  # ✅ Respawn für alle Hunter
                        h.clear_target()
                        h.respawn()



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



    def main_loop(self):
        while self.__running:
            self.__clock.tick(10)
            events = pygame.event.get()
            self.__draw_objects()
            self.__running = handle_snake_input(events, self.__snake)
            self.__check_collisions()
            self.__obstacles.move()
            self.__snake.move()
            self.__bob.move_towards_apple(self.__apple.get_positions())
            self.__bob.move()
            self.__bob.check_respawn()  # Falls Bob tot ist, respawnt er nach 20 Sek
            self.__update_screen()
            self.__snake.update_flash()
            self.__update_effects()
            self.__update_countdown()
            for hunter in self.__hunter_obstacle:  # 🔥 Für jedes Hindernis `move()` aufrufen
                hunter.move()

            # 🆕 Falls die Zeit abgelaufen ist, Spiel beenden
            if self.__countdown_time <= 0:
                self.__running = False

        final_score, back_to_menu, new_name = self.show_game_over_screen()
        return final_score, back_to_menu, new_name

    def show_game_over_screen(self):
        """Zeigt den Game Over Bildschirm mit Animation & schönerem Design."""
        font_large = pygame.font.SysFont("monospace", 50, bold=True)
        font_small = pygame.font.SysFont("monospace", 25)

        final_score = self.__snake.get_score()
        blink = True  # Für blinkenden Text
        blink_timer = 0  # Zeit für Blinken

        while True:
            self.__screen.fill((30, 30, 30))  # 🎨 Dunkelgrauer Hintergrund für einen besseren Look

            # 🔴 Game Over Text
            text1 = font_large.render("GAME OVER", True, (255, 50, 50))
            self.__screen.blit(text1, (Settings.screen_width // 2 - text1.get_width() // 2, 100))

            # 🏆 Score Anzeige
            text2 = font_small.render(f"Score: {final_score}", True, (255, 255, 255))
            self.__screen.blit(text2, (Settings.screen_width // 2 - text2.get_width() // 2, 170))

            # ✨ Blinkender Hinweis (alle 500ms)
            current_time = pygame.time.get_ticks()
            if current_time - blink_timer > 500:  # Blinkt alle 500ms
                blink = not blink
                blink_timer = current_time

            if blink:
                text_blink = font_small.render("Drücke eine Taste", True, (255, 255, 100))
                self.__screen.blit(text_blink, (Settings.screen_width // 2 - text_blink.get_width() // 2, 230))

            # 🎮 Menüoptionen
            text3 = font_small.render("Enter: Neustart | N: Neuer Name | M: Menü", True, (200, 200, 200))
            self.__screen.blit(text3, (Settings.screen_width // 2 - text3.get_width() // 2, 300))

            pygame.display.flip()

            # 🕹️ Event Handling für Eingaben
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Neustart
                        return final_score, False, None
                    elif event.key == pygame.K_n:  # Neuer Name wählen
                        return final_score, False, "new_name"
                    elif event.key == pygame.K_m:  # Zurück zum Menü
                        return final_score, True, None

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
