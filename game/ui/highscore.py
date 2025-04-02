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

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS chaos_highscores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        """)

    conn.commit()
    conn.close()

import sqlite3

def save_or_update_score(name, score, mode="normal"):
    """Speichert den Score nur, wenn der Name nicht existiert oder wenn der neue Score höher ist."""
    if mode == "normal":
        table = "highscores"
    elif mode == "classic":
        table = "classic_highscores"
    elif mode == "chaos":
        table = "chaos_highscores"
    else:
        print("[ERROR] ❌ Ungültiger Modus!")
        return

    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT score FROM {table} WHERE name = ?", (name,))
    result = cursor.fetchone()

    if result:
        current_highscore = result[0]
        if score > current_highscore:
            cursor.execute(f"UPDATE {table} SET score = ? WHERE name = ?", (score, name))
            print(f"[DEBUG] Neuer Highscore für {name} im {mode}-Modus: {score} (alt: {current_highscore})")
        else:
            print(f"[DEBUG] Score {score} ist niedriger als Highscore {current_highscore} - kein Update.")
    else:
        cursor.execute(f"INSERT INTO {table} (name, score) VALUES (?, ?)", (name, score))
        print(f"[DEBUG] Neuer Spieler {name} mit Highscore {score} im {mode}-Modus hinzugefügt!")

    conn.commit()
    conn.close()


def get_chaos_highscores():
    """Liest die Top 10 Highscores aus der Chaos Mode-Tabelle."""
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM chaos_highscores ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores



def get_highscores(mode="normal"):
    """Holt die Highscores aus der richtigen Tabelle."""
    table = "highscores" if mode == "normal" else "classic_highscores"
    conn = sqlite3.connect("highscores.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, score FROM {table} ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores



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



