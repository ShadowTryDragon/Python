import pygame
import sqlite3

def is_name_taken(name):
    """Überprüft, ob der Name bereits in der Datenbank existiert."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None  # True = Name existiert, False = Name ist neu

def get_player_name(screen):
    """Ermöglicht die Eingabe eines Spielernamens."""
    font = pygame.font.SysFont("monospace", 30)
    name = ""

    while True:
        screen.fill((0, 0, 0))
        text = font.render(f"Dein Name: {name}", True, (255, 255, 255))
        screen.blit(text, (50, 200))

        # 🔴 Fehlermeldung anzeigen, falls Name existiert
        if is_name_taken(name):
            error_text = font.render("Name existiert bereits! Wähle einen anderen.", True, (255, 0, 0))
            screen.blit(error_text, (50, 250))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None  # Falls das Fenster geschlossen wird
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name and not is_name_taken(name):
                    return name  # ✅ Name zurückgeben
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() and len(name) < 10:
                    name += event.unicode
