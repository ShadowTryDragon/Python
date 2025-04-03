import pygame
import sqlite3

from game import Settings

def is_name_taken(name, mode):
    """Überprüft, ob der Name bereits in der Highscore-Tabelle des jeweiligen Modus existiert."""
    table_name = f"{mode}_highscores"  # Tabellenname basierend auf dem Modus
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT 1 FROM {table_name} WHERE name = ?", (name,))
        result = cursor.fetchone()
    except sqlite3.OperationalError:
        print(f"⚠️ Fehler: Die Tabelle {table_name} existiert nicht!")
        result = None  # Falls die Tabelle nicht existiert, keine Sperrung des Namens

    conn.close()
    return result is not None  # True = Name existiert, False = Name ist neu


def get_player_name(screen, mode):
    """Namenseingabe mit Modus-spezifischer Überprüfung."""
    font = pygame.font.SysFont("monospace", 35, bold=True)
    font_small = pygame.font.SysFont("monospace", 20)

    name = ""
    blink = True
    blink_timer = 0
    max_length = 20

    while True:
        screen.fill((30, 30, 30))

        # Titel
        title_text = font.render("Gib deinen Namen ein:", True, (255, 255, 255))
        screen.blit(title_text, (Settings.screen_width // 2 - title_text.get_width() // 2, 80))

        # Blinken des Cursors
        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > 500:
            blink = not blink
            blink_timer = current_time

        display_name = name + ("_" if blink else "")
        name_text = font.render(display_name, True, (100, 200, 255))
        screen.blit(name_text, (Settings.screen_width // 2 - name_text.get_width() // 2, 160))

        # Falls Name schon existiert
        if is_name_taken(name, mode):
            error_text = font_small.render("❌ Name existiert bereits in diesem Modus!", True, (255, 100, 100))
            screen.blit(error_text, (Settings.screen_width // 2 - error_text.get_width() // 2, 220))

        # Hinweise zur Steuerung
        hint_text = font_small.render("↵ Enter: Bestätigen | ⌫ Backspace: Löschen | ESC: Menü", True, (200, 200, 200))
        screen.blit(hint_text, (Settings.screen_width // 2 - hint_text.get_width() // 2, 280))

        pygame.display.flip()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name and not is_name_taken(name, mode):
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.unicode.isprintable() and len(name) < max_length:
                    name += event.unicode

