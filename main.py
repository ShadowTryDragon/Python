import pygame

from ui.highscore import show_highscores
from ui.menu import Menu
from ui.inputs import get_player_name  # ✅ Namenseingabe importieren
from game.database import init_db, save_score, update_highscore
from game.snake_game import SnakeGame
from game.classic import start_classic_mode

def start_game(screen):
    """Startet das Spiel mit übergebenem `screen`."""
    player_name = get_player_name(screen)  # ✅ `screen` direkt übergeben

    while True:
        game = SnakeGame(player_name)
        final_score, back_to_menu, new_name = game.main_loop()

        if final_score is not None:
            if new_name == player_name:
                update_highscore(player_name, final_score)
            else:
                save_score(player_name, final_score)

        if back_to_menu:  # 🏠 Falls Spieler "M" drückt, zurück ins Menü
            break

        if new_name is None:  # 🎮 Falls Spieler "N" drückt, neuen Namen wählen
            player_name = get_player_name(screen)  # ✅ `screen` bleibt gleich


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Snake Menü")
    init_db()

    menu = Menu(screen)

    while True:
        menu.draw()
        choice = menu.handle_keys()

        if choice == 0:  # Start Game
            start_game(screen)  # ✅ `screen` wird weitergegeben
        elif choice == 1:  # Classic Mode
            start_classic_mode()
        elif choice == 2:  # Bestenliste anzeigen
            show_highscores(screen, mode="normal")
        elif choice == 3:  # Beenden
            pygame.quit()
            break

if __name__ == "__main__":
    main()
