import pygame
from ui.menu import Menu
from ui.inputs import get_player_name  # ✅ Namenseingabe importieren
from game.database import init_db
from game.snake_game import SnakeGame
from game.classic import start_classic_mode

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Snake Menü")
    init_db()

    menu = Menu(screen)

    while True:
        menu.draw()
        choice = menu.handle_keys()

        if choice == 0:  # Start Normal Mode
            player_name = get_player_name(screen)  # ✅ Spielername holen
            game = SnakeGame(player_name)
            game.start_game()
        elif choice == 1:  # Start Classic Mode
            start_classic_mode()
        elif choice == 2:  # Bestenliste
            from ui.highscore import show_highscores
            show_highscores(screen)
        elif choice == 3:  # Beenden
            pygame.quit()
            break

if __name__ == "__main__":
    main()
