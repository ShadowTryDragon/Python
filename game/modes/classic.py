import sys
import pygame

from game.ui.inputs import get_player_name
from game.objects.snake import Snake
from game.setting.settings import Settings
from game.setting.database import save_or_update_score


class ClassicSnakeGame:
    def __init__(self, player_name):
        pygame.init()
        from game import Apple  # 🆕 Apple wird erst hier importiert!
        self.__player_name = player_name
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height))
        self.__surface = pygame.Surface(self.__screen.get_size()).convert()
        self.__snake = Snake()
        self.__apple = Apple(count=1, snake=self.__snake)  # Nur normale Äpfel
        self.__running = True  # Spiel läuft
        self.__my_font = pygame.font.SysFont("monospace", 16)

    def __handle_keys(self):
        """Steuert die Schlange mit den Pfeiltasten."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.__snake.turn(Settings.up)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.__snake.turn(Settings.down)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.__snake.turn(Settings.left)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.__snake.turn(Settings.right)
                elif event.key == pygame.K_ESCAPE:
                    self.__running = False

    def __check_collisions(self):
        """Prüft, ob die Schlange sich selbst oder die Wand getroffen hat."""
        head_pos = self.__snake.get_head_position()

        # 💀 Selbst-Kollision
        if head_pos in self.__snake.get_positions()[1:]:
            print("Game Over: Die Schlange hat sich selbst getroffen!")
            self.__running = False
            return

        # 🍏 Apfel essen
        if head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)  # +3 Punkte und Länge wächst
            from game import Apple  # 🆕 Apple wird erst hier importiert!
            self.__apple = Apple(count=1, snake=self.__snake)  # Neuer Apfel

    def __draw_objects(self):
        """Zeichnet Spielfeld, Schlange und Apfel."""
        self.__screen.fill((0, 0, 0))  # Hintergrund schwarz
        self.__apple.draw(self.__screen)
        self.__snake.draw(self.__screen)

        # Punkte anzeigen
        score_text = self.__my_font.render(f"{self.__player_name} | Score: {self.__snake.get_score()}", True, (255, 255, 255))
        self.__screen.blit(score_text, (5, 10))

        pygame.display.flip()

    def main_loop(self):
        """Hauptspiel-Schleife."""
        while self.__running:
            self.__clock.tick(10)
            self.__handle_keys()
            self.__snake.move()
            self.__check_collisions()
            self.__draw_objects()

        print("Game Over: Classic Mode beendet.")
        return self.__snake.get_score()  # Finaler Score wird zurückgegeben


