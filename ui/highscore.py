import pygame
from game.database import get_highscores  # ✅ Holt Highscores aus der DB

def show_highscores(screen, mode="normal"):
    """Zeigt die Highscores auf dem Bildschirm an."""
    font = pygame.font.SysFont("monospace", 25)
    scores = get_highscores(mode)  # ✅ "normal" oder "classic"

    while True:
        screen.fill((0, 0, 0))
        title = font.render("Highscores" if mode == "normal" else "Classic Highscores", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - 80, 50))

        for i, (name, score) in enumerate(scores):
            text = font.render(f"{i+1}. {name}: {score}", True, (200, 200, 200))
            screen.blit(text, (100, 100 + i * 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    return  # Zurück zum Menü
