import os

import pygame

from game.modes.chaos_mode import ChaosMode
from game.ui.highscore import show_highscores
from game.ui.menu import Menu
from game.ui.inputs import get_player_name  # ✅ Namenseingabe importieren
from game.setting.database import init_db, save_or_update_score
from game.modes.snake_game import SnakeGame
from game.modes.classic import start_classic_mode
from game.modes.battle import BattleRoyale







im_menue = True  # Startet im Menü


def start_game(screen):
    """Startet das Spiel mit übergebenem `screen`."""
    player_name = get_player_name(screen)  # ✅ `screen` direkt übergeben

    if player_name is None:  # Falls ESC gedrückt wurde
        return  # ⏪ Zurück ins Menü

    while True:
        game = SnakeGame(player_name)
        final_score, back_to_menu, new_name = game.main_loop()

        if final_score is not None:
            if new_name is None:  # ✅ Falls kein neuer Name gewählt wurde, alten beibehalten
                new_name = player_name

            # 🏆 Score nur speichern oder updaten, wenn nötig
            save_or_update_score(new_name, final_score, mode="normal")

        if back_to_menu:  # 🏠 Falls Spieler "M" drückt, zurück ins Menü
            break

        # 🎮 Falls Spieler "N" drückt, neuen Namen wählen
        if new_name is None:
            new_name = get_player_name(screen)  # 🔄 Spieler gibt neuen Namen ein
            if new_name is None:  # Falls ESC gedrückt wurde, zurück ins Menü
                break

        player_name = new_name  # ✅ Den neuen oder alten Namen für den nächsten Durchgang speichern

def start_chaos_mode(screen):
    """Startet den Chaos-Modus."""
    player_name = get_player_name(screen)
    if player_name is None:  # Falls ESC gedrückt wurde
        return  # Zurück zum Menü

    while True:
        game = ChaosMode(player_name)
        final_score, back_to_menu, new_name = game.main_loop()

        if final_score is not None:
            if new_name is None:
                new_name = player_name

            save_or_update_score(new_name, final_score, mode="chaos")  # ✅ Chaos-Score speichern

        if back_to_menu:
            break  # Zurück zum Menü

        if new_name is None:
            new_name = get_player_name(screen)
            if new_name is None:
                break

        player_name = new_name

def start_battle_royale_mode(screen):
    """Startet den Battle-Royale-Modus."""
    player_name = get_player_name(screen)

    if player_name is None:  # Falls ESC gedrückt wurde
        return  # ⏪ Zurück ins Menü
    game = BattleRoyale(player_name)  # ✅ Battle-Royale-Modus starten
    game.main_loop()


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Snake Menü")
    init_db()

    menu = Menu(screen)

    while True:
        menu.draw()
        choice = menu.handle_keys()

        if choice == 0:  # ✅ Normaler Modus
            start_game(screen)
        elif choice == 1:  # ✅ Classic Mode
            start_classic_mode()
        elif choice == 2:  # Battle Royale Mode
            start_chaos_mode(screen)
        elif choice == 3:  # ✅ Bestenliste
            show_highscores(screen)
        elif choice == 4:  # ✅ Beenden
            pygame.quit()
            break

if __name__ == "__main__":
    main()
