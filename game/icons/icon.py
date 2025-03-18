import pygame
from game.setting.settings import Settings

pygame.init()

def create_snake_body_sprite(color, filename):
    """Erstellt ein rundes Körper-Sprite für die Schlange und speichert es."""
    size = (Settings.grid_size, Settings.grid_size)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (size[0] // 2, size[1] // 2), size[0] // 2)  # 🟢 Runde Körperform
    pygame.image.save(surface, filename)

create_snake_body_sprite((0, 255, 0), "snake_body.png")  # 🟢 Spieler
create_snake_body_sprite((255, 255, 0), "bob_body.png")  # 🟡 Bob
print("✅ Sprites wurden gespeichert!")
pygame.quit()
