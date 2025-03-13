import sqlite3
import sys
import pygame
from game import Settings

def init_db():
    """Erstellt die Tabellen für beide Spielmodi."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classic_highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_score(name, score, mode="normal"):
    """Speichert den Score in die richtige Tabelle."""
    table = "highscores" if mode == "normal" else "classic_highscores"
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table} (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()

def get_highscores(mode="normal"):
    """Holt die Highscores aus der richtigen Tabelle."""
    table = "highscores" if mode == "normal" else "classic_highscores"
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, score FROM {table} ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores

def save_classic_score(name, score):
    """Speichert den Spieler-Score für den Classic Mode in die Datenbank."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO classic_highscores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()

def get_classic_highscores():
    """Liest die Top 10 Highscores aus der Classic Mode-Tabelle."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM classic_highscores ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores

def show_classic_highscores(screen):
    font = pygame.font.SysFont("monospace", 25)
    scores = get_classic_highscores()

    while True:
        screen.fill((0, 0, 0))
        title = font.render("Classic Mode - Bestenliste", True, (255, 255, 255))
        screen.blit(title, (Settings.screen_width // 2 - 100, 50))

        for i, (name, score) in enumerate(scores):
            text = font.render(f"{name}: {score}", True, (200, 200, 200))
            screen.blit(text, (100, 100 + i * 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Zurück zum Menü



def update_highscore(name, new_score):
    """Aktualisiert den Highscore eines Spielers, falls der neue Score höher ist."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()

    # 🔍 Prüfen, ob der Spieler existiert und seinen aktuellen Highscore abrufen
    cursor.execute("SELECT score FROM highscores WHERE name = ?", (name,))
    result = cursor.fetchone()

    if result:
        current_highscore = result[0]
        if new_score > current_highscore:
            cursor.execute("UPDATE highscores SET score = ? WHERE name = ?", (new_score, name))
            print(f"[DEBUG] Neuer Highscore für {name}: {new_score} (alt: {current_highscore})")
        else:
            print(f"[DEBUG] Score {new_score} ist niedriger als Highscore {current_highscore} - kein Update.")
    else:
        # Falls der Name nicht existiert, sollte er neu gespeichert werden (eigentlich nicht nötig, weil Name geprüft wurde)
        cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, new_score))
        print(f"[DEBUG] Neuer Spieler {name} mit Highscore {new_score} hinzugefügt!")

    conn.commit()
    conn.close()
