import pygame
from game.setting.settings import Settings


def handle_snake_input(events, snake, battle_mode=False):
    """Verarbeitet die Steuerung der Schlange mit den Pfeiltasten oder WASD."""
    new_bullets = []  # 🔫 Liste für neue Schüsse (falls Battle-Modus aktiv)

    for event in events:
        if event.type == pygame.QUIT:
            return False, new_bullets  # 🛑 Spiel beenden → gibt jetzt zwei Werte zurück!

        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                snake.turn(Settings.up)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                snake.turn(Settings.down)
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                snake.turn(Settings.left)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                snake.turn(Settings.right)

            # 🔫 Nur im Battle Mode: Schießen mit Leertaste
            elif battle_mode and event.key == pygame.K_SPACE:
                new_bullets.append(snake.shoot())  # 🆕 Füge neuen Schuss hinzu

            elif event.key == pygame.K_ESCAPE:
                return False, new_bullets  # 🛑 Falls ESC → Spiel beenden

    return True, new_bullets  # ✅ Normal weiterspielen + ggf. neue Schüsse zurückgeben
