import random

import pygame

from game.objects.powerup import PowerUp
from game.objects.snake import Snake
from game.setting.playerinputs import handle_snake_input
from game.setting.settings import Settings
from game.ui.inputs import get_player_name


class BattleRoyale:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__bullets = []  # 🔫 Gespeicherte Schüsse
        self.__powerups = [PowerUp() for _ in range(2)]  # ⚡ 2 zufällige Power-Ups
        self.__running = True
        # 🐍 Spieler an zufälliger Position spawnen
        self.__player = Snake(name=player_name, is_player=True, position=self.get_random_position())

        # 🆚 Gegner-Schlangen zufällig spawnen
        self.__enemies = [Snake(name=f"Enemy {i}", is_player=False, position=self.get_random_position()) for i in
                          range(3)]
        self.__next_powerup_time = pygame.time.get_ticks() + random.randint(5000, 15000)  # 🎲 Nächstes Power-Up

    def move_enemies(self):
        for enemy in self.__enemies:
            if random.randint(0, 10) > 8:
                enemy.set_random_direction()
                enemy.move()




    def get_random_position(self):
        """✅ Gibt eine zufällige Position im Spielfeld zurück."""
        grid_x = random.randint(0, (Settings.screen_width // Settings.grid_size) - 1) * Settings.grid_size
        grid_y = random.randint(0, (Settings.screen_height // Settings.grid_size) - 1) * Settings.grid_size
        return (grid_x, grid_y)
    def spawn_powerup(self):
        """Spawnt zufällig ein Power-Up nach einer bestimmten Zeit."""
        if pygame.time.get_ticks() >= self.__next_powerup_time:
            self.__powerups.append(PowerUp())
            self.__next_powerup_time = pygame.time.get_ticks() + random.randint(5000, 15000)  # 🎲 Neues Intervall

    def check_collision(self, bullet, target):
        """Prüft, ob eine Kugel den Gegner oder den Spieler trifft (Abstand <= halbe Grid-Größe)."""
        bullet_x, bullet_y = bullet.get_position()

        for segment_x, segment_y in target.get_positions():
            distance = ((bullet_x - segment_x) ** 2 + (bullet_y - segment_y) ** 2) ** 0.5  # 🧮 Abstand berechnen
            if distance < Settings.grid_size // 2:  # ✅ Falls Kugel nah genug ist
                return True
        return False

    def check_collisions(self):
        """Prüft Kollisionen zwischen Schüssen, Gegnern & Power-Ups."""

        # 🔫 Schüsse treffen Gegner
        for bullet in self.__bullets[:]:  # Kopie der Liste zur sicheren Iteration
            for enemy in self.__enemies[:]:  # Kopie der Gegner-Liste
                if bullet.get_position() in enemy.get_positions() and bullet.owner != enemy:
                    print(f"[DEBUG] 💀 {enemy.get_name()} wurde getroffen!")
                    enemy.die()  # ✅ Gegner stirbt
                    self.__enemies.remove(enemy)  # 🗑️ Entferne Gegner
                    self.__bullets.remove(bullet)  # 🗑️ Entferne Geschoss
                    break  # ⏭️ Keine weitere Prüfung für diesen Schuss

            # 🔫 Schüsse treffen den Spieler → GAME OVER!
            if self.check_collision(bullet, self.__player):
                print("[DEBUG] ❌ SPIELER WURDE GETROFFEN! GAME OVER!")
                self.__running = False  # 🛑 Spiel beenden
                return

        # ⚡ Power-Ups einsammeln
        for powerup in self.__powerups[:]:
            if self.__player.get_head_position() == powerup.get_position():
                print(f"[DEBUG] ⚡ {self.__player_name} hat ein Power-Up eingesammelt!")
                powerup.activate(self.__player)
                self.__powerups.remove(powerup)

    def main_loop(self):
        """Battle Royale Spielschleife"""
        self.__dead_enemies = []  # 💀 Liste der toten Feinde für den Respawn

        while self.__running:
            self.__clock.tick(10)
            events = pygame.event.get()

            # 🎮 Steuerung übernehmen (jetzt mit begrenzter Munition!)
            self.__running, new_bullets = handle_snake_input(events, self.__player, battle_mode=True)

            # 🔫 Nur neue Schüsse hinzufügen, wenn Munition vorhanden ist
            if self.__player.has_ammo():
                self.__bullets.extend(new_bullets)
                self.__player.decrease_ammo(len(new_bullets))  # 🔻 Munition verringern

            self.__player.move()
            for enemy in self.__enemies:
                if random.random() < 0.1:  # 10% Chance, die Richtung zu ändern
                    enemy.set_random_direction()
                enemy.move()

                # 🆕 Lasse den Gegner mit einer Wahrscheinlichkeit von 2% schießen
                if random.random() < 0.02:
                    bullet = enemy.shoot()
                    if bullet:  # Nur hinzufügen, wenn nicht None
                        self.__bullets.append(bullet)

                # 🔫 Gegner schießen zufällig
                if random.randint(1, 100) > 98:  # 2% Chance pro Frame
                    self.__bullets.append(enemy.shoot())

            for bullet in self.__bullets:
                bullet.move()

            self.check_collisions()
            self.spawn_powerup()
            self.handle_enemy_respawn()  # 🏴‍☠️ Tote Feinde wiederbeleben
            # 🏆 Game Over prüfen
            if not self.__running:
                game_over, new_name = self.show_game_over_screen(victory=False)
                return game_over, new_name  # 🔄 Entscheidung über Neustart oder Menü

            # 🏅 Sieg prüfen (alle Gegner besiegt)
            if len(self.__enemies) == 0:
                game_over, new_name = self.show_game_over_screen(victory=True)
                return game_over, new_name  # 🔄 Entscheidung über Neustart oder Menü

            self.draw_objects()

    def handle_enemy_respawn(self):
        """Belebt besiegte Feinde nach 10 Sekunden wieder."""
        current_time = pygame.time.get_ticks()
        for enemy, death_time in self.__dead_enemies[:]:
            if current_time - death_time > 10000:  # ⏳ 10 Sekunden vergangen
                self.__enemies.append(enemy)
                self.__dead_enemies.remove((enemy, death_time))

    def show_game_over_screen(self, victory=False, sys=None):
        """Zeigt den Game Over Bildschirm mit Animation & schönerem Design."""
        font_large = pygame.font.SysFont("monospace", 50, bold=True)
        font_small = pygame.font.SysFont("monospace", 25)

        blink = True  # Für blinkenden Text
        blink_timer = 0  # Zeit für Blinken

        # 🏆 Sieg oder Niederlage?
        game_over_text = "DU HAST GEWONNEN!" if victory else "GAME OVER"
        text_color = (50, 255, 50) if victory else (255, 50, 50)  # Grün für Sieg, Rot für Niederlage

        while True:
            self.__screen.fill((20, 20, 20))  # 🎨 Dunkelgrauer Hintergrund

            # 🔴 Game Over oder Sieg-Text
            text1 = font_large.render(game_over_text, True, text_color)
            self.__screen.blit(text1, (Settings.screen_width // 2 - text1.get_width() // 2, 100))

            # 👾 Verbleibende Gegner oder Score
            if victory:
                text2 = font_small.render("Alle Gegner besiegt!", True, (255, 255, 255))
            else:
                text2 = font_small.render(f"Verbleibende Gegner: {len(self.__enemies)}", True, (255, 255, 255))

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
                        return False, None
                    elif event.key == pygame.K_n:  # Neuer Name wählen
                        new_name = get_player_name(self.__screen)  # 🎯 Neuen Namen abfragen
                        if new_name is None:
                            return True, None  # Falls ESC gedrückt → Zurück zum Menü
                        return False, new_name  # ✅ Richtiger neuer Name

                    elif event.key == pygame.K_m:  # Zurück zum Menü
                        return True, None

    def draw_objects(self):
        """Zeichnet alle Objekte auf dem Bildschirm."""
        self.__screen.fill((0, 0, 0))

        self.__player.draw(self.__screen)
        for enemy in self.__enemies:
            enemy.draw(self.__screen)

        for bullet in self.__bullets:
            bullet.draw(self.__screen)

        for powerup in self.__powerups:
            powerup.draw(self.__screen)

        pygame.display.flip()
