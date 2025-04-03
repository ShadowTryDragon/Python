import os
import random

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
        self.bg_color_shift = 0
        self.bg_color_direction = 1  # 🌈 Farbwechsel-Richtung

        self.select_sound = pygame.mixer.Sound("game/audio/select_sound.wav")
        self.confirm_sound = pygame.mixer.Sound("game/audio/confirm_sound.wav")



        self.snake_path = [
            (Settings.screen_width // 2 - 250, 160),
            (Settings.screen_width // 2 + 250, 160),
            (Settings.screen_width // 2 + 250, 550),
            (Settings.screen_width // 2 - 250, 550),
            (Settings.screen_width // 2 - 250, 160)
        ]
        self.menu_music_path = "game/audio/menu_music.mp3"  # 🎵 Menü-Musik Datei
        self.play_music(self.menu_music_path)  # 🔊 Menü-Musik beim Start

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

    def play_music(self, file_path):
        """Spielt Musik in einer Endlosschleife."""
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(-1)
        print(f"[DEBUG] 🎵 Musik gestartet: {file_path}")

    def return_to_menu(self):
        """Menü-Musik neu starten, wenn man ins Menü zurückkehrt."""
        print("[DEBUG] 🔄 Zurück im Menü!")  # Wird das angezeigt?
        self.stop_music()
        self.play_music(self.menu_music_path)

    def stop_music(self):
        """Stoppt die Musik."""
        pygame.mixer.music.stop()
        print("[DEBUG] ⏹️ Musik gestoppt!")

    def animate_background(self):
        """Sanfter Übergang der Hintergrundfarbe"""
        self.bg_color_shift += self.bg_color_direction
        if self.bg_color_shift > 50 or self.bg_color_shift < -50:
            self.bg_color_direction *= -1  # 🔄 Richtung umkehren

        red = max(0, min(255, 10 + self.bg_color_shift))
        green = max(0, min(255, 30 + self.bg_color_shift))
        blue = max(0, min(255, 10 + self.bg_color_shift))
        self.bg_color = (red, green, blue)  # 🎨 Sanfter Farbverlauf

    def draw(self):
        """Zeichnet das Menü mit Icons & animierter Schlange."""
        self.animate_background()
        self.screen.fill(tuple(self.bg_color))  # Hintergrund zuerst zeichnen!

        # 🎮 Titel zeichnen
        title_text = self.title_font.render("Snake Game", True, (0, 255, 0))

        # 🖼️ Snake-Icon laden & skalieren (größer)
        snake_icon = pygame.image.load("game/icons/snake.png")
        snake_icon = pygame.transform.scale(snake_icon, (70, 70))  # 🐍 Größere Schlange

        # 📍 Positionen berechnen
        title_x = Settings.screen_width // 2 - title_text.get_width() // 2
        title_y = 50

        icon_gap = 20  # 📏 Abstand zwischen Icon und Text
        icon_size = 70  # 🔍 Gleiche Größe für Berechnung

        icon_left_x = title_x - icon_size - icon_gap  # 🐍 Links vom Titel
        icon_right_x = title_x + title_text.get_width() + icon_gap  # 🐍 Rechts vom Titel
        icon_y = title_y - 10  # 📌 Perfekt auf einer Ebene mit dem Titel

        # 🖌️ Elemente auf den Bildschirm zeichnen
        self.screen.blit(snake_icon, (icon_left_x, icon_y))  # 🐍 Links
        self.screen.blit(title_text, (title_x, title_y))  # 📝 Titel
        self.screen.blit(snake_icon, (icon_right_x, icon_y))  # 🐍 Rechts

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

        # 📌 Dann Text über die Icons mit Hover-Effekt
        for i, option in enumerate(self.options):
                    if i == self.selected:
                        color = (0, 255, 0)  # 🌟 Helleres Grün beim Hover
                        scale = 1.2  # ✨ Text größer machen
                    else:
                        color = (200, 200, 200)  # ⚪ Grauer, wenn nicht ausgewählt
                        scale = 1.0  # 🔍 Normale Größe

                    # 🔠 Dynamische Schriftgröße für Hover-Effekt
                    font_scaled = pygame.font.SysFont("monospace", int(40 * scale), bold=True)
                    text = font_scaled.render(option, True, color)

                    # 📌 Zentriert ausrichten
                    text_x = Settings.screen_width // 2 - text.get_width() // 2
                    text_y = 200 + i * 60
                    self.screen.blit(text, (text_x, text_y))  # 📝 Text über Icons





        pygame.display.flip()  # ✅ Bildschirm aktualisieren, damit die Schlange sichtbar ist!

    def start_game_music(self, mode):
        """Startet die passende Musik mit sanftem Übergang."""
        pygame.mixer.music.fadeout(1000)  # 🔉 Musik sanft ausblenden (1 Sekunde)
        pygame.time.delay(1000)  # Warte kurz für sanften Wechsel

        if mode in [0, 1]:  # Start Game oder Classic Mode
            self.play_music("game/audio/game_music.mp3")
        elif mode == 2:  # Chaos Mode
            self.play_music("game/audio/chaos_music.mp3")

    def handle_events(self):
        """Verarbeitet Tasteneingaben und Maus-Interaktionen im Menü."""
        mouse_x, mouse_y = pygame.mouse.get_pos()  # 🖱️ Mausposition holen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 4  # Beenden

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_DOWN, pygame.K_s]:  # 🔽 Nach unten
                    self.selected = (self.selected + 1) % len(self.options)
                    self.select_sound.play()  # 🎵 Sound abspielen
                elif event.key in [pygame.K_UP, pygame.K_w]:  # 🔼 Nach oben
                    self.selected = (self.selected - 1) % len(self.options)
                    self.select_sound.play()  # 🎵 Sound abspielen
                elif event.key == pygame.K_RETURN:  # ✅ Auswahl bestätigen
                    if self.selected in [0, 1, 2]:  # Wenn Spielmodus gewählt
                        self.confirm_sound.play()  # 🎵 Bestätigungston
                        self.start_game_music(self.selected)
                    return self.selected


            elif event.type == pygame.MOUSEMOTION:
                # Überprüfen, ob die Maus über einem Menüpunkt ist
                for i, option in enumerate(self.options):
                    text_y = 200 + i * 60
                    if text_y <= mouse_y <= text_y + 40:  # 40px Textgröße
                        self.selected = i  # 🎯 Menüpunkt markieren

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 🖱️ Linksklick
                    for i, option in enumerate(self.options):
                        text_y = 200 + i * 60
                        if text_y <= mouse_y <= text_y + 40:
                            if i in [0, 1, 2]:  # Falls ein Spielmodus ausgewählt wird
                                self.start_game_music(i)
                            return i  # Auswahl zurückgeben

        return None






