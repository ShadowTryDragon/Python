import random
import pygame

from game.objects.powerup import PowerUp
from game.objects.snake import Snake
from game.setting.playerinputs import handle_snake_input
from game.setting.settings import Settings


class BattleRoyale:
    def __init__(self, player_name):
        pygame.init()
        self.__player_name = player_name
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__player = Snake(name=player_name, is_player=True)  # ✅ Jetzt funktioniert es!
        self.__enemies = [Snake(name=f"Enemy {i}", is_player=False) for i in range(3)]  # 🆚 3 Gegner-Schlangen
        self.__bullets = []  # 🔫 Gespeicherte Schüsse
        self.__powerups = [PowerUp() for _ in range(2)]  # ⚡ 2 zufällige Power-Ups
        self.__running = True
        self.__next_powerup_time = pygame.time.get_ticks() + random.randint(5000, 15000)  # 🎲 Nächstes Power-Up

    def spawn_powerup(self):
        """Spawnt zufällig ein Power-Up nach einer bestimmten Zeit."""
        if pygame.time.get_ticks() >= self.__next_powerup_time:
            self.__powerups.append(PowerUp())
            self.__next_powerup_time = pygame.time.get_ticks() + random.randint(5000, 15000)  # 🎲 Neues Intervall



    def check_collisions(self):
        """Prüft Kollisionen zwischen Schüssen, Gegnern & Power-Ups."""

        # 🔫 Schüsse treffen Gegner
        for bullet in self.__bullets[:]:  # Kopie der Liste zur sicheren Iteration
            for enemy in self.__enemies[:]:  # Kopie der Gegner-Liste

                if bullet.get_position() in enemy.get_positions():
                    print(f"[DEBUG] 💀 {enemy.get_name()} wurde getroffen!")
                    enemy.die()  # ✅ Gegner stirbt
                    self.__enemies.remove(enemy)  # 🗑️ Entferne Gegner
                    self.__bullets.remove(bullet)  # 🗑️ Entferne Geschoss
                    break  # ⏭️ Keine weitere Prüfung für diesen Schuss

            # 🔫 Schüsse treffen den Spieler → GAME OVER!
            if bullet.get_position() in self.__player.get_positions():
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
        while self.__running:
            self.__clock.tick(10)
            events = pygame.event.get()

            # 🎮 Steuerung übernehmen (jetzt mit Schießen!)
            self.__running, new_bullets = handle_snake_input(events, self.__player, battle_mode=True)

            # 🔫 Neue Schüsse zur Liste hinzufügen
            self.__bullets.extend(new_bullets)

            self.__player.move()
            for enemy in self.__enemies:
                enemy.move()

            for bullet in self.__bullets:
                bullet.move()

            self.check_collisions()
            self.draw_objects()

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
