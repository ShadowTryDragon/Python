import pygame
import random

from game import Settings


class MenuApple:
    def __init__(self, path):
        """Spawnt zufällige Äpfel entlang des Schlangenpfads."""
        self.path = path  # Der Pfad, auf dem Äpfel erscheinen
        self.position = random.choice(self.path)  # Zufällige Position auf dem Pfad
        self.image = pygame.image.load("game/icons/sprites/apple.png").convert_alpha()
        apple_size = int(Settings.grid_size * 2)  # 150% der Grid-Size
        self.image = pygame.transform.scale(self.image, (apple_size, apple_size))

    def relocate(self):
        """Setzt den Apfel an eine neue zufällige Position auf dem Pfad."""
        self.position = random.choice(self.path)  # Neuer zufälliger Punkt
        print(f"[DEBUG] Apfel neu gespawnt bei {self.position}")

    def draw(self, screen):
        """Zeichnet den Apfel mit seinem Sprite auf dem Bildschirm."""
        apple_width, apple_height = self.image.get_size()
        offset_x = (Settings.grid_size - apple_width) // 2  # Zentrieren
        offset_y = (Settings.grid_size - apple_height) // 2

        screen.blit(self.image, (self.position[0] + offset_x, self.position[1] + offset_y))
