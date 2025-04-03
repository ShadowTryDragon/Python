


import pygame
from game.setting.gamecolors import *
from game.setting.database import get_highscores, get_classic_highscores, get_chaos_highscores


def show_highscores(screen):
    """Zeigt eine schön formatierte Highscore-Tabelle für alle Spielmodi an."""
    pygame.font.init()

    import game.setting.gamecolors as colors





    # Farben definieren 🎨



    # Fonts laden 📜
    title_font = pygame.font.SysFont("Arial", 50, bold=True)
    header_font = pygame.font.SysFont("Arial", 30, bold=True)
    score_font = pygame.font.SysFont("Arial", 25)
    footer_font = pygame.font.SysFont("Arial", 20, italic=True)

    # Highscores abrufen
    normal_scores = get_highscores()[:10]
    classic_scores = get_classic_highscores()[:10]
    chaos_scores = get_chaos_highscores()[:10]

    # Fenstergröße ermitteln
    width, height = screen.get_size()
    column_width = width // 3
    padding = 30  # Abstand vom oberen Rand

    running = True
    while running:
        screen.fill(colors.GameColors.BG_COLOR)  # Hintergrund setzen

        # Titel zentriert oben anzeigen
        title_text = title_font.render("HIGHSCORES", True, colors.GameColors.TEXT_TITLE)
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 20))

        # Spaltenüberschriften
        headers = [("Normal Mode", colors.GameColors.NORMAL_COLOR), ("Classic Mode", colors.GameColors.CLASSIC_COLOR), ("Chaos Mode", colors.GameColors.CHAOS_COLOR)]
        for i, (text, color) in enumerate(headers):
            header_text = header_font.render(text, True, color)
            x_pos = i * column_width + column_width // 2 - header_text.get_width() // 2
            screen.blit(header_text, (x_pos, padding + 50))

        # Horizontale Linie unter den Überschriften
        pygame.draw.line(screen, colors.GameColors.LINE_COLOR, (50, padding + 90), (width - 50, padding + 90), 2)

        # Highscores anzeigen
        max_scores = max(len(normal_scores), len(classic_scores), len(chaos_scores))
        for i in range(max_scores):
            y_pos = padding + 120 + i * 30  # Abstand zwischen den Einträgen

            for j, scores in enumerate([normal_scores, classic_scores, chaos_scores]):
                if i < len(scores):
                    name, score = scores[i]

                    # Namen kürzen, wenn er länger als 10 Zeichen ist
                    if len(name) > 10:
                        name = name[:7] + "..."  # 7 Zeichen + "..."

                    score_text = score_font.render(f"{i + 1}. {name}: {score}", True, colors.GameColors.TEXT_COLOR)
                    x_pos = j * column_width + column_width // 2 - score_text.get_width() // 2
                    screen.blit(score_text, (x_pos, y_pos))

        # Vertikale Trennlinien
        pygame.draw.line(screen, colors.GameColors.LINE_COLOR, (column_width, padding + 80), (column_width, height - 80), 2)
        pygame.draw.line(screen, colors.GameColors.LINE_COLOR, (2 * column_width, padding + 80), (2 * column_width, height - 80), 2)

        # Fußzeile
        footer_text = footer_font.render("↩ ENTER / ESC zum Menü", True, colors.GameColors.TEXT_COLOR)
        screen.blit(footer_text, (width // 2 - footer_text.get_width() // 2, height - 50))

        pygame.display.flip()  # Bildschirm aktualisieren

        # Event-Handling (Schließen oder zurück zum Menü)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    running = False



