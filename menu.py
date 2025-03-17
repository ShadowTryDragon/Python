import os

import pygame
from pygame.math import lerp
from game.setting.settings import Settings
from game.ui.menuSnake import MenuSnake



class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 40, bold=True)
        self.title_font = pygame.font.SysFont("monospace", 60, bold=True)
        self.options = ["Start Game", "Classic Mode", "Chaos Mode", "Bestenliste", "Beenden"]
        self.selected = 0
        self.bg_color = [30, 30, 30]  # 🌑 Dunkler Hintergrund als Liste (RGB)
        self.color_direction = [1, 1, 1]  # Für die Farbänderung
        self.snake_path = [
            (Settings.screen_width // 2 - 250, 160),
            (Settings.screen_width // 2 + 250, 160),
            (Settings.screen_width // 2 + 250, 550),
            (Settings.screen_width // 2 - 250, 550),
            (Settings.screen_width // 2 - 250, 160)
        ]
        from main import play_music
        play_music("game/audio/menu_music.mp3")

        # ✅ MenuSnake bekommt jetzt den Pfad als Parameter
        self.menu_snake = MenuSnake(self.snake_path)



        # 📌 🎨 Icons laden

        # 🔍 Debugging: Prüfe, ob der Pfad existiert
        icon_path = os.path.join(os.getcwd(), "game/icons/")
        print(f"DEBUG: Icon-Pfad = {icon_path}")
        print(f"DEBUG: Existiert der Pfad? {os.path.exists(icon_path)}")
        self.icons = {}
        icon_size = (50, 50)  # Standardgröße für alle Icons

        for option, filename in {
            "Start Game": "start_game.png",
            "Classic Mode": "classic_mode.png",
            "Chaos Mode": "chaos_mode.png",
            "Bestenliste": "highscores.png",
            "Beenden": "exit.png"
        }.items():
            icon_full_path = os.path.join(icon_path, filename)

            if os.path.exists(icon_full_path):
                try:
                    icon_image = pygame.image.load(icon_full_path).convert_alpha()
                    self.icons[option] = pygame.transform.scale(icon_image, icon_size)  # 📌 Skaliere auf 50x50 px
                    print(f"DEBUG: ✅ Icon {filename} erfolgreich geladen!")
                except pygame.error as e:
                    print(f"DEBUG: ❌ Fehler beim Laden von {filename}: {e}")


    def lerp(a, b, t):
        """Hilfsfunktion für lineare Interpolation zwischen zwei Farben."""
        return a + (b - a) * t

    def animate_background(self):
        """Sanfter Übergang der Hintergrundfarbe"""
        t = (pygame.time.get_ticks() % 5000) / 5000  # 5 Sekunden Übergangszeit

        # Übergang zwischen zwei Farbtönen (dunkel & heller)
        target_color = [50, 50, 50]  # Etwas heller als Startwert
        for i in range(3):
            self.bg_color[i] = int(lerp(30, target_color[i], t))  # Sanfter Farbwechsel

    def draw(self):
        """Zeichnet das Menü mit Icons & animierter Schlange."""
        self.animate_background()
        self.screen.fill(tuple(self.bg_color))  # Hintergrund zuerst zeichnen!

        # 🎮 Titel zeichnen
        title_text = self.title_font.render("🐍 Snake Game 🐍", True, (0, 255, 0))
        self.screen.blit(title_text, (Settings.screen_width // 2 - title_text.get_width() // 2, 50))

        # 🐍 Menü-Schlange bewegen & zeichnen
        self.menu_snake.move()
        self.menu_snake.draw(self.screen)  # ✅ Jetzt wird sie gezeichnet!

        # 📌 Icons zuerst zeichnen
        for i, option in enumerate(self.options):
            icon_x = Settings.screen_width // 2 - 150
            icon_y = 200 + i * 60

            if option in self.icons:
                icon = pygame.transform.scale(self.icons[option], (40, 40))
                self.screen.blit(icon, (icon_x - 60, icon_y))  # 🎯 Icons werden gezeichnet

        # 📌 Dann Text über die Icons
        for i, option in enumerate(self.options):
            color = (0, 255, 0) if i == self.selected else (200, 200, 200)
            text = self.font.render(option, True, color)
            text_x = Settings.screen_width // 2 - 150 + 10
            text_y = 200 + i * 60
            self.screen.blit(text, (text_x, text_y))  # 📝 Text über Icons

        pygame.display.flip()  # ✅ Bildschirm aktualisieren, damit die Schlange sichtbar ist!

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 4  # Beenden
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected  # ✅ Gibt die gewählte Option zurück

        return None





