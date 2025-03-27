import pygame

from game.setting.settings import Settings

# 🔫 Schussbegrenzung
MAX_BULLETS = 3  # 🏹 Maximal 3 Schüsse gleichzeitig
SHOOT_COOLDOWN = 500  # ⏳ 500ms Cooldown zwischen den Schüssen
last_shot_time = 0  # 🕒 Zeitstempel des letzten Schusses


def handle_snake_input(events, snake, battle_mode=False, bullets=None):
    if bullets is None:
        bullets = []  # ✅ Falls None, wird eine leere Liste erstellt

    current_time = pygame.time.get_ticks()
    """Verarbeitet die Steuerung der Schlange und ermöglicht Schießen im Battle Mode."""
    global last_shot_time
    new_bullets = []

    keys = pygame.key.get_pressed()

    for event in events:
        if event.type == pygame.QUIT:
            return False, new_bullets  # 🛑 Falls Fenster geschlossen → Spiel beenden

        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                snake.turn(Settings.up)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                snake.turn(Settings.down)
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                snake.turn(Settings.left)
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                snake.turn(Settings.right)
                print(
                    f"DEBUG: BattleMode={battle_mode}, Bullets={len(bullets) if bullets else 'None'}, Cooldown={current_time - last_shot_time}")
            elif battle_mode and event.key == pygame.K_SPACE:

                # ✅ Prüfen, ob noch Schüsse übrig sind & Cooldown vorbei ist
                print(f"DEBUG: Letzter Schuss: {last_shot_time}, Zeit: {current_time}, Schüsse: {len(bullets)}")
                if bullets is not None and len(bullets) < MAX_BULLETS and (
                        current_time - last_shot_time) > SHOOT_COOLDOWN:
                    new_bullets.append(snake.shoot())  # 🆕 Füge neuen Schuss hinzu
                    last_shot_time = current_time  # ⏳ Cooldown aktualisieren

            elif event.key == pygame.K_ESCAPE:
                return False, new_bullets  # 🛑 Falls ESC → Spiel beenden

    return True, new_bullets  # ✅ Normal weiterspielen + ggf. neue Schüsse zurückgeben
