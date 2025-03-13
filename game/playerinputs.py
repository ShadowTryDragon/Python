import pygame


def handle_snake_input(events, snake):
    from game.settings import Settings
    """Verarbeitet die Steuerung der Schlange mit den Pfeiltasten oder WASD."""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                snake.turn(Settings.up)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                snake.turn(Settings.down)
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                snake.turn(Settings.left)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                snake.turn(Settings.right)
            elif event.key == pygame.K_ESCAPE:
                return False  # 🛑 Spiel stoppen
    return True  # 🎮 Spiel weiterführen
