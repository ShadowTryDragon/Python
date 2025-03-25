
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

    def handle_input(self):
        """Steuert die Spielerbewegung und das Schießen."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.__player.turn(Settings.left)
        elif keys[pygame.K_RIGHT]:
            self.__player.turn(Settings.right)
        elif keys[pygame.K_UP]:
            self.__player.turn(Settings.up)
        elif keys[pygame.K_DOWN]:
            self.__player.turn(Settings.down)

        # 🔫 Schießen mit der Leertaste
        if keys[pygame.K_SPACE]:
            self.__bullets.append(self.__player.shoot())

    def check_collisions(self):
        """Prüft Kollisionen mit Schlangen & Power-Ups."""
        for bullet in self.__bullets:
            for enemy in self.__enemies:
                if bullet.get_position() in enemy.get_positions():
                    enemy.die()
                    self.__bullets.remove(bullet)

        for powerup in self.__powerups:
            if self.__player.get_head_position() == powerup.get_position():
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
