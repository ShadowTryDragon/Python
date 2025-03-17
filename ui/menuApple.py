import pygame
import random

class MenuApple:
    def __init__(self, path):
        """Spawnt zufällige Äpfel entlang des Schlangenpfads."""
        self.path = path  # Der Pfad, auf dem Äpfel erscheinen
        self.position = random.choice(self.path)  # Zufällige Position auf dem Pfad
        self.color = (255, 0, 0)  # 🍎 Apfel ist rot

    def relocate(self):
        """Setzt den Apfel an eine neue zufällige Position auf dem Pfad."""
        self.position = random.choice(self.path)  # Neuer zufälliger Punkt
        print(f"[DEBUG] Apfel neu gespawnt bei {self.position}")

    def draw(self, screen):
        """Zeichnet den Apfel auf dem Bildschirm."""
        pygame.draw.circle(screen, self.color, self.position, 8)  # 🍏 Kleiner Apfel
