import pygame
import sys
import random

# Farben für das Snake-Spiel
class GameColors:
    BODY_COLOR = (46, 58, 89)  # Dunkles Blau für den Körper
    HEAD_COLOR = (46, 58, 89)  # Helles Grün für den Kopf
    APPLE_COLOR = (231, 76, 60)  # Rot für den Apfel
    FAKE_APPLE_COLOR = (155, 89, 182)  # Lila für den Fake-Apfel
    MIN_APPLE_COLOR = (39, 174, 96)  # Grün für den Halb-Apfel

class Snake:
    def __init__(self):
        self.__length = 1
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__color = GameColors.BODY_COLOR
        self.__score = 0

    def turn(self, new_direction):
        if (new_direction[0] * -1, new_direction[1] * -1) != self.__direction:
            self.__direction = new_direction

    def move(self):
        head_pos = self.get_head_position()
        x, y = self.__direction
        new = (((head_pos[0] + (x * Settings.grid_size)) % Settings.screen_width),
               (head_pos[1] + (y * Settings.grid_size)) % Settings.screen_height)
        if len(self.__positions) > 2 and new in self.__positions[2:]:
            self.reset()
        else:
            self.__positions.insert(0, new)
            if len(self.__positions) > self.__length:
                self.__positions.pop()

    def get_positions(self):
        return self.__positions

    def get_head_position(self):
        return self.__positions[0]

    def reset(self):
        self.reset_length()
        self.__positions = [((Settings.screen_width / 2), (Settings.screen_height / 2))]
        self.__direction = random.choice(Settings.directions)
        self.__score = 0

    def increase_length(self, value):
        self.__length += value

    def decrease_length(self, value):
        if self.__length > 1:
            self.__length -= value
            self.__positions.pop()

    def reset_length(self):
        self.__length = 1

    def increase_score(self, value):
        self.__score += value

    def decrease_score(self):
        self.__score /= 2

    def get_score(self):
        return self.__score

    def reset_score(self):
        self.__score = 0

    def draw(self, surface):
        for index, pos in enumerate(self.__positions):
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            if index == 0:
                pygame.draw.rect(surface, GameColors.HEAD_COLOR, r)
            else:
                pygame.draw.rect(surface, self.__color, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)

class Food:
    def __init__(self, count=3, color=(0, 0, 0), snake=None):
        self.__positions = []
        self.__count = count
        self.__color = color
        self.snake = snake
        self.randomize_positions()

    def get_positions(self):
        return self.__positions

    def randomize_positions(self):
        self.__positions = []
        while len(self.__positions) < self.__count:
            x_pos = random.randint(0, int(Settings.grid_width) - 1) * Settings.grid_size
            y_pos = random.randint(0, int(Settings.grid_height) - 1) * Settings.grid_size
            new_position = (x_pos, y_pos)
            if new_position not in self.__positions and new_position not in self.snake.get_positions():
                self.__positions.append(new_position)

    def draw(self, surface):
        for pos in self.__positions:
            r = pygame.Rect((pos[0], pos[1]), (Settings.grid_size, Settings.grid_size))
            pygame.draw.rect(surface, self.__color, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)

class Apple(Food):
    def __init__(self, count=2, snake=None):
        super().__init__(count, GameColors.APPLE_COLOR, snake=snake)

    def action(self, snake):
        snake.increase_length(1)
        snake.increase_score(3)

class FakeApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, GameColors.FAKE_APPLE_COLOR, snake=snake)

    def action(self, snake):
        snake.increase_score(1)
        snake.increase_length(3)

class MinApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, GameColors.MIN_APPLE_COLOR, snake=snake)

    def action(self, snake):
        snake.decrease_score()

class ReverseApple(Food):
    def __init__(self, count=1, snake=None):
        super().__init__(count, (255, 165, 0), snake=snake)
        self.__reversed = False
        self.__start_time = None
        self.__active = False

    def action(self, snake):
        if self.__active and not self.__reversed:
            self.__reversed = True
            self.__start_time = pygame.time.get_ticks()
            self.reverse_controls(snake)

    def reverse_controls(self, snake):
        Settings.up, Settings.down = Settings.down, Settings.up
        Settings.left, Settings.right = Settings.right, Settings.left

    def reset_controls(self):
        Settings.up, Settings.down = (0, -1), (0, 1)
        Settings.left, Settings.right = (-1, 0), (1, 0)
        self.__reversed = False
        self.__active = False

    def update(self):
        if self.__reversed:
            elapsed_time = pygame.time.get_ticks() - self.__start_time
            if elapsed_time >= 5000:
                self.reset_controls()

    def activate(self):
        self.__active = True
        self.randomize_positions()

class Settings:
    screen_width = 480
    screen_height = 480

    grid_size = 20
    grid_width = screen_width / grid_size
    grid_height = screen_height / grid_size

    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)

    directions = [up, down, left, right]

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode((Settings.screen_width, Settings.screen_height), 0, 32)
        self.__surface = pygame.Surface(self.__screen.get_size()).convert()
        self.__snake = Snake()
        self.__apple = Apple(count=1, snake=self.__snake)
        self.__fakeapple = FakeApple(count=1, snake=self.__snake)
        self.__halfapple = MinApple(count=1, snake=self.__snake)
        self.__my_font = pygame.font.SysFont("monospace", 16)
        self.__paused = False
        self.__game_started = False
        self.__game_over = False  # Neues Flag für Game Over

    def __quit_game(self):
        pygame.quit()
        sys.exit()

    def __handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__quit_game()
            elif event.type == pygame.KEYDOWN:
                if self.__game_over:  # Wenn das Spiel zu Ende ist
                    if event.key == pygame.K_RETURN:  # Neustart
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:  # Beenden
                        self.__quit_game()
                elif event.key == pygame.K_UP:
                    self.__snake.turn(Settings.up)
                elif event.key == pygame.K_s:
                    self.__snake.turn(Settings.down)
                elif event.key == pygame.K_DOWN:
                    self.__snake.turn(Settings.down)
                elif event.key == pygame.K_LEFT:
                    self.__snake.turn(Settings.left)
                elif event.key == pygame.K_a:
                    self.__snake.turn(Settings.left)
                elif event.key == pygame.K_RIGHT:
                    self.__snake.turn(Settings.right)
                elif event.key == pygame.K_r:
                    self.__snake.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.__quit_game()
                elif event.key == pygame.K_p:
                    self.__paused = not self.__paused
                elif event.key == pygame.K_RETURN:
                    if not self.__game_started:
                        self.__game_started = True
                        self.__snake.reset()

    def __draw_grid(self, surface):
        for y in range(0, int(Settings.grid_height)):
            for x in range(0, int(Settings.grid_width)):
                r = pygame.Rect((x * Settings.grid_size, y * Settings.grid_size),
                                (Settings.grid_size, Settings.grid_size))
                color = (93, 216, 228) if (x + y) % 2 == 0 else (84, 194, 205)
                pygame.draw.rect(surface, color, r)

    def __draw_start_screen(self, surface):
        title = self.__my_font.render("Snake Game", True, (255, 255, 255))
        start_enter = self.__my_font.render("Press Enter to Start", True, (0, 255, 0))
        start_esc = self.__my_font.render("Press ESC to Quit", True, (255, 0, 0))

        surface.fill((0, 0, 0))
        surface.blit(title, (Settings.screen_width // 2 - title.get_width() // 2, Settings.screen_height // 3))
        surface.blit(start_enter, (Settings.screen_width // 2 - start_enter.get_width() // 2, Settings.screen_height // 2))
        surface.blit(start_esc, (Settings.screen_width // 2 - start_esc.get_width() // 2, Settings.screen_height // 2 + 30))
        pygame.display.update()

    def __draw_pause_screen(self, surface):
        pause_text = self.__my_font.render("PAUSED - Press P to Resume", True, (255, 0, 0))
        surface.blit(pause_text, (Settings.screen_width // 2 - pause_text.get_width() // 2, Settings.screen_height // 2))

    def __draw_game_over_screen(self, surface):
        # Hintergrund für den Game Over Screen
        surface.fill((0, 0, 0))  # Schwarzer Hintergrund

        # "Game Over" Text
        game_over_text = self.__my_font.render("Game Over", True, (255, 0, 0))
        surface.blit(game_over_text, (Settings.screen_width // 2 - game_over_text.get_width() // 2, Settings.screen_height // 3))

        # Punktestand anzeigen
        score_text = self.__my_font.render(f"Score: {self.__snake.get_score()}", True, (255, 255, 255))
        surface.blit(score_text, (Settings.screen_width // 2 - score_text.get_width() // 2, Settings.screen_height // 2))

        # Neustart und Beenden Optionen
        restart_text = self.__my_font.render("Press ENTER to Restart", True, (255, 255, 255))
        quit_text = self.__my_font.render("Press ESC or Q to Quit", True, (255, 255, 255))

        surface.blit(restart_text, (Settings.screen_width // 2 - restart_text.get_width() // 2, Settings.screen_height // 2 + 30))
        surface.blit(quit_text, (Settings.screen_width // 2 - quit_text.get_width() // 2, Settings.screen_height // 2 + 60))

    def __update_screen(self):
        if self.__game_over:
            self.__draw_game_over_screen(self.__surface)  # Zeige Game Over Screen
        elif not self.__game_started:
            self.__draw_start_screen(self.__surface)
        else:
            self.__screen.blit(self.__surface, (0, 0))
            score_text = self.__my_font.render(f"Score: {self.__snake.get_score()}", True, (0, 0, 0))
            self.__screen.blit(score_text, (5, 10))
            pygame.display.update()

    def __check_collisions(self):
        head_pos = self.__snake.get_head_position()

        if head_pos in self.__apple.get_positions():
            self.__apple.action(self.__snake)
            self.__apple.randomize_positions()
            self.__fakeapple.randomize_positions()
            self.__halfapple.randomize_positions()

        elif head_pos in self.__fakeapple.get_positions():
            self.__fakeapple.action(self.__snake)
            self.__apple.randomize_positions()
            self.__fakeapple.randomize_positions()
            self.__halfapple.randomize_positions()

        elif head_pos in self.__halfapple.get_positions():
            self.__halfapple.action(self.__snake)
            self.__halfapple.randomize_positions()
            self.__apple.randomize_positions()
            self.__fakeapple.randomize_positions()

        # Kollision mit dem eigenen Körper oder den Wänden -> Game Over
        if self.__snake.collides_with_boundaries() or self.__snake.collides_with_self():
            self.__game_over = True  # Spiel endet bei Kollision

    def __draw_objects(self):
        self.__snake.draw(self.__surface)
        self.__apple.draw(self.__surface)
        self.__fakeapple.draw(self.__surface)
        self.__halfapple.draw(self.__surface)

    def start_game(self):
        self.__game_started = True
        self.__game_over = False  # Game Over zurücksetzen
        self.__snake.reset()
        self.__apple.randomize_positions()
        self.__fakeapple.randomize_positions()
        self.__halfapple.randomize_positions()

    def main_loop(self):
        while True:
            self.__clock.tick(10)
            self.__handle_keys()

            if not self.__game_started:
                self.__draw_start_screen(self.__surface)
            else:
                self.__draw_grid(self.__surface)
                if not self.__paused and not self.__game_over:
                    self.__snake.move()
                    self.__check_collisions()
                    self.__draw_objects()
                elif self.__paused:
                    self.__draw_pause_screen(self.__surface)

            self.__update_screen()



game = SnakeGame()
game.main_loop()
