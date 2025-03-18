import os

import pygame

from game.modes.chaos_mode import ChaosMode
from game.ui.highscore import show_highscores
from game.ui.menu import Menu
from game.ui.inputs import get_player_name  # ✅ Namenseingabe importieren
from game.setting.database import init_db, save_or_update_score
from game.modes.snake_game import SnakeGame
from game.modes.classic import start_classic_mode


def play_music(music_path):
    """Spielt eine Hintergrundmusik in Dauerschleife."""
    if not os.path.exists(music_path):  # Falls Datei fehlt, Debug-Warnung
        print(f"[ERROR] ❌ Musikdatei nicht gefunden: {music_path}")
        return

    pygame.mixer.init()  # 🎵 Mixer initialisieren (nur 1x nötig!)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)  # 🎧 Lautstärke anpassen (0.0 - 1.0)
    pygame.mixer.music.play(-1)  # 🔄 Dauerschleife (-1)

def start_game(screen):
    play_music("game/audio/game_music.mp3")
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
    game = ChaosMode(player_name)  # ✅ Chaos-Modus starten
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
        elif choice == 2:  # ✅ Chaos Modus
            start_chaos_mode(screen)  # CHAOS MODUS starten
        elif choice == 3:  # ✅ Bestenliste
            show_highscores(screen, mode="both")
        elif choice == 4:  # ✅ Beenden
            pygame.quit()
            break

if __name__ == "__main__":
    main()
