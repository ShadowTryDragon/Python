import pygame
import sqlite3

from game import Settings

def is_name_taken(name):
    """Überprüft, ob der Name bereits in der Datenbank existiert."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None  # True = Name existiert, False = Name ist neu

def get_player_name(screen):
    """Schöne Namenseingabe mit verbesserter Optik, 20 Zeichen & Menü-Option."""
    font = pygame.font.SysFont("monospace", 35, bold=True)
    font_small = pygame.font.SysFont("monospace", 20)

    name = ""
    blink = True  # Blinke-Effekt für den Cursor
    blink_timer = 0
    max_length = 20  # ✅ Zeichenanzahl erhöht auf 20

    while True:
        screen.fill((30, 30, 30))  # 🎨 Hintergrundfarbe dunkelgrau

        # 📝 Text "Gib deinen Namen ein:"
        title_text = font.render("Gib deinen Namen ein:", True, (255, 255, 255))
        screen.blit(title_text, (Settings.screen_width // 2 - title_text.get_width() // 2, 80))

        # ⌨️ Eingabe-Anzeige mit blinkendem Cursor
        current_time = pygame.time.get_ticks()
        if current_time - blink_timer > 500:  # Blinkt alle 500ms
            blink = not blink
            blink_timer = current_time

        display_name = name + ("_" if blink else "")  # Blinke-Effekt mit Unterstrich
        name_text = font.render(display_name, True, (100, 200, 255))  # Hellblau
        screen.blit(name_text, (Settings.screen_width // 2 - name_text.get_width() // 2, 160))

        # 🚨 Fehlermeldung falls Name bereits existiert
        if is_name_taken(name):
            error_text = font_small.render("❌ Name existiert bereits! Wähle einen anderen.", True, (255, 100, 100))
            screen.blit(error_text, (Settings.screen_width // 2 - error_text.get_width() // 2, 220))

        # ℹ️ Hinweis zur Eingabe
        hint_text = font_small.render("↵ Enter: Bestätigen | ⌫ Backspace: Löschen | ESC: Menü", True, (200, 200, 200))
        screen.blit(hint_text, (Settings.screen_width // 2 - hint_text.get_width() // 2, 280))

        pygame.display.flip()

        # 🎮 Event Handling für Eingaben
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None  # Falls das Fenster geschlossen wird
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name and not is_name_taken(name):
                    return name  # ✅ Name zurückgeben
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]  # Letztes Zeichen entfernen
                elif event.key == pygame.K_ESCAPE:
                    return None  # ✅ Zurück zum Menü
                elif event.unicode.isprintable() and len(name) < max_length:
                    name += event.unicode  # ✅ Leerzeichen und Zeichen erlaubt
