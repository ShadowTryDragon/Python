import pygame
from game.setting.database import get_highscores, get_classic_highscores

def show_highscores(screen, mode="both"):  # ✅ Mode hinzugefügt!
    """Zeigt die Highscores für Normal & Classic an."""
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_score = pygame.font.SysFont("monospace", 25)

    # 🏆 Highscores abrufen
    normal_scores = get_highscores() if mode in ["both", "normal"] else []
    classic_scores = get_classic_highscores() if mode in ["both", "classic"] else []

    while True:
        screen.fill((30, 30, 30))  # 🎨 Hintergrund

        # 🏆 Titel anzeigen
        title_text = font_title.render("🏆 HIGHSCORES 🏆", True, (255, 255, 0))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 30))

        if normal_scores:
            normal_text = font_title.render("Normal Mode", True, (100, 200, 255))
            screen.blit(normal_text, (screen.get_width() // 4 - normal_text.get_width() // 2, 100))

        if classic_scores:
            classic_text = font_title.render("Classic Mode", True, (255, 150, 100))
            screen.blit(classic_text, (3 * screen.get_width() // 4 - classic_text.get_width() // 2, 100))

        if normal_scores and classic_scores:
            pygame.draw.line(screen, (255, 255, 255), (screen.get_width() // 2, 100),
                             (screen.get_width() // 2, screen.get_height() - 100), 2)

        for i, (name, score) in enumerate(normal_scores[:10]):
            text = font_score.render(f"{i+1}. {name}: {score}", True, (200, 200, 200))
            screen.blit(text, (screen.get_width() // 4 - text.get_width() // 2, 160 + i * 30))

        for i, (name, score) in enumerate(classic_scores[:10]):
            text = font_score.render(f"{i+1}. {name}: {score}", True, (200, 200, 200))
            screen.blit(text, (3 * screen.get_width() // 4 - text.get_width() // 2, 160 + i * 30))

        exit_text = font_score.render("↩ ENTER / ESC zum Menü", True, (255, 255, 255))
        screen.blit(exit_text, (screen.get_width() // 2 - exit_text.get_width() // 2, screen.get_height() - 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    return  # Zurück zum Menü
