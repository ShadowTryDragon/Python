import pygame
from game.settings import Settings

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 30)
        self.options = ["Start Game", "Classic Mode", "Bestenliste", "Beenden"]
        self.selected = 0

    def draw(self):
        self.screen.fill((0, 0, 0))
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected else (150, 150, 150)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (Settings.screen_width // 2 - text.get_width() // 2, 150 + i * 50))

        pygame.display.flip()

    def handle_keys(self):
        """Menü-Steuerung"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 3  # Beenden auswählen
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected  # 🏆 Menü-Option zurückgeben
        return None
