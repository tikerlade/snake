from enum import Enum

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
import random

BLUE = (106, 159, 181)
# BLUE = (106, 255, 181)
WHITE = (255, 255, 255)
FOOD_COLOR = (139, 0, 255)

CELL, COLS, ROWS = 20, 25, 25
HEIGHT = CELL * ROWS
WIDTH = CELL * COLS

BASE_SPEED = 3
BOOST_SPEED_PER_N_APPLES = 1


class GameState(Enum):
    QUIT = -1
    TITLE = 0
    GAME = 1
    GAMEOVER = 2


class Grid:
    def __init__(self, n_rows, n_cols, obstacles_option=None):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.maze = self.generate_maze()
        self.fill_borders()

    def generate_maze(self):
        return [
            [0 for _ in range(self.n_cols)]
            for __ in range(self.n_rows)
        ]

    def fill_borders(self):
        for col in range(self.n_cols):
            self.maze[0][col] = 1
            self.maze[self.n_rows-1][col] = 1

        for row in range(self.n_rows):
            self.maze[row][0] = 1
            self.maze[row][self.n_cols-1]

    def generate_obstacles(self, obstacles_option):
        pass


class Apple:
    def __init__(self, size=1):
        self.size = size

    def spawn_new(self, grid):
        while True:
            x = random.randint(1, COLS-3)
            y = random.randint(1, ROWS-3)


def place_food(maze, snake):
    while True:
        x, y = random.randint(1, COLS-3), random.randint(1, ROWS-3)
        if maze[y][x] == 0 and (x, y) not in snake:
            return (x, y)


def display_random_snake():
    pass


def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """
        self.mouse_over = False  # indicates if the mouse is over the element

        # create the default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # create the image that shows when mouse is over the element
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        # add both images and their rects to lists
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        self.action = action
        # calls the init method of the parent sprite class
        super().__init__()

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        """ Updates the element's appearance depending on the mouse position
            and returns the button's action if clicked.
        """
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)


def title_screen(screen):
    start_btn = UIElement(
        center_position=(WIDTH // 2, HEIGHT // 2 - 30),
        font_size=30,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="Start",
        action=GameState.GAME,
    )
    quit_btn = UIElement(
        center_position=(WIDTH // 2, HEIGHT // 2 + 30),
        font_size=30,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    buttons = [start_btn, quit_btn]

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return GameState.GAME
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return GameState.QUIT
        screen.fill(BLUE)

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()


def gameover_screen(screen):
    menu_btn = UIElement(
        center_position=(WIDTH // 2, HEIGHT // 2 - 30),
        font_size=30,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="menu",
        action=GameState.TITLE,
    )
    tryagain_btn = UIElement(
        center_position=(WIDTH // 2, HEIGHT // 2 + 30),
        font_size=30,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="try again",
        action=GameState.GAME,
    )

    buttons = [menu_btn, tryagain_btn]

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return GameState.GAME
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return GameState.QUIT
        screen.fill(BLUE)

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()


def game_screen(screen):
    font = pygame.freetype.SysFont("Courier", 18, bold=True)
    clock = pygame.time.Clock()
    # This fills the square
    maze = [[1 if x in (0, COLS-1) or y in (0, ROWS-1)
            else 0 for x in range(COLS)] for y in range(ROWS)]
    # We can add obstacles here ...

    snake = [(COLS // 2, ROWS // 2)]
    # direction = (1, 0)
    direction = (0, 0)
    food, score, running = place_food(maze, snake), 0, True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                d = {
                    pygame.K_UP: (0, -1),
                    pygame.K_w: (0, -1),
                    pygame.K_DOWN: (0, 1),
                    pygame.K_s: (0, 1),
                    pygame.K_LEFT: (-1, 0),
                    pygame.K_a: (-1, 0),
                    pygame.K_RIGHT: (1, 0),
                    pygame.K_d: (1, 0)
                }.get(event.key)

                if d and (d[0] + direction[0], d[1] + direction[1]) != (0, 0):
                    direction = d

        head = (
            snake[0][0] + direction[0],
            snake[0][1] + direction[1]
        )
        if maze[head[1]][head[0]] == 1 or (head in snake and direction != (0, 0)):
            running = False
            continue

        snake.insert(0, head)
        food_options = [(food[0] + x, food[1] + y)
                        for x, y in [(0, 0), (0, 1), (1, 0), (1, 1)]]
        if head in (food_options):
            score += 1
            food = place_food(maze, snake)
        else:
            snake.pop()

        screen.fill((15, 15, 25))
        for y in range(ROWS):
            for x in range(COLS):
                if maze[y][x]:
                    pygame.draw.rect(screen, BLUE,
                                     (x*CELL, y*CELL, CELL, CELL))

        for idx, s in enumerate(snake):
            color_for_snake = (0, 220, 80)
            if idx == 0:
                color_for_snake = (0, 120, 80)

            pygame.draw.rect(
                screen,
                color_for_snake,
                (s[0]*CELL, s[1]*CELL, CELL-1, CELL-1)
            )

        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            (food[0]*CELL, food[1]*CELL, CELL-1, CELL-1)
        )
        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            ((food[0]+1)*CELL, food[1]*CELL, CELL-1, CELL-1)
        )
        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            ((food[0])*CELL, (food[1]+1)*CELL, CELL-1, CELL-1)
        )
        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            ((food[0] + 1)*CELL, (food[1] + 1)*CELL, CELL-1, CELL-1)
        )
        text_surface, _ = font.render(f"Score: {score}", (255, 255, 255))
        screen.blit(text_surface, (8, 4))
        pygame.display.flip()

        clock.tick(BASE_SPEED + len(snake) // BOOST_SPEED_PER_N_APPLES)
    return GameState.GAMEOVER


def main():
    pygame.init()
    screen = pygame.display.set_mode((COLS * CELL, ROWS * CELL))

    pygame.display.set_caption("Maze Snake")
    game_state = GameState.TITLE

    while True:
        if game_state == GameState.TITLE:
            game_state = title_screen(screen)

        if game_state == GameState.GAMEOVER:
            game_state = gameover_screen(screen)

        if game_state == GameState.GAME:
            game_state = game_screen(screen)

        if game_state == GameState.QUIT:
            pygame.quit()
            return


if __name__ == '__main__':
    main()
