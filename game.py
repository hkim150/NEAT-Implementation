import pygame as pg
from NEAT import *


class Game:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 700
    NUM_ROWS = 20
    NUM_COLS = 10
    BLOCK_SIZE = 30
    GAME_WIDTH = NUM_COLS * BLOCK_SIZE
    GAME_HEIGHT = NUM_ROWS * BLOCK_SIZE

    GRID_START_X = (SCREEN_WIDTH - GAME_WIDTH) // 2
    GRID_START_Y = SCREEN_HEIGHT - GAME_HEIGHT

    S = [['.....',
          '..00.',
          '.00..',
          '.....',
          '.....'],
         ['.....',
          '..0..',
          '..00.',
          '...0.',
          '.....']]

    Z = [['.....',
          '.00..',
          '..00.',
          '.....',
          '.....'],
         ['.....',
          '..0..',
          '.00..',
          '.0...',
          '.....']]

    I = [['..0..',
          '..0..',
          '..0..',
          '..0..',
          '.....'],
         ['.....',
          '0000.',
          '.....',
          '.....',
          '.....']]

    O = [['.....',
          '.00..',
          '.00..',
          '.....',
          '.....']]

    J = [['.....',
          '.0...',
          '.000.',
          '.....',
          '.....'],
         ['.....',
          '..00.',
          '..0..',
          '..0..',
          '.....'],
         ['.....',
          '.....',
          '.000.',
          '...0.',
          '.....'],
         ['.....',
          '..0..',
          '..0..',
          '.00..',
          '.....']]

    L = [['.....',
          '...0.',
          '.000.',
          '.....',
          '.....'],
         ['.....',
          '..0..',
          '..0..',
          '..00.',
          '.....'],
         ['.....',
          '.....',
          '.000.',
          '.0...',
          '.....'],
         ['.....',
          '.00..',
          '..0..',
          '..0..',
          '.....']]

    T = [['.....',
          '..0..',
          '.000.',
          '.....',
          '.....'],
         ['.....',
          '..0..',
          '..00.',
          '..0..',
          '.....'],
         ['.....',
          '.....',
          '.000.',
          '..0..',
          '.....'],
         ['.....',
          '..0..',
          '.00..',
          '..0..',
          '.....']]

    shapes = (S, Z, I, O, J, L, T)
    shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]
    NUM_SHAPE = len(shapes)
    EMPTY = (0, 0, 0)
    NUM_INPUT = 14
    NUM_ACTIONS = 5
    UP, DOWN, LEFT, RIGHT, SPACE = 14, 15, 16, 17, 18

    def __init__(self):
        self.win = None

    def create_grid(self):
        return [[Game.EMPTY for _ in range(Game.NUM_COLS)] for _ in range(Game.NUM_ROWS)]

    def convert_shape_format(self, piece):
        positions = []
        rot = piece.rotation

        if rot < 0:
            rot += len(piece.shape)
        format = piece.shape[rot % len(piece.shape)]

        for row, row_val in enumerate(format):
            for col, col_val in enumerate(row_val):
                if col_val == '0':
                    positions.append((piece.row + row - 2, piece.col + col - 2))

        return positions

    def valid_space(self, piece, grid):
        positions = self.convert_shape_format(piece)

        for (row, col) in positions:
            if row >= Game.NUM_ROWS or col < 0 or col >= Game.NUM_COLS:
                return False
            if row > -1 and grid[row][col] != Game.EMPTY:
                return False

        return True

    def get_shape(self, gen_shape):
        if len(gen_shape) < 1:
            gen_shape.extend([n for n in range(Game.NUM_SHAPE)])
            random.shuffle(gen_shape)

        return Piece(0, 5, gen_shape.pop())

    def draw_text_middle(self, surface, text, size, color):
        pg.font.init()

        font = pg.font.SysFont("comicsans", size, bold=True)
        label = font.render(text, 1, color)

        surface.blit(label, (Game.GRID_START_X + Game.GAME_WIDTH / 2 - (label.get_width() / 2),
                             Game.GRID_START_Y + Game.GAME_HEIGHT / 2 - label.get_height() / 2))

    def draw_grid(self, surface, grid):
        sx = Game.GRID_START_X
        sy = Game.GRID_START_Y

        for row in range(Game.NUM_ROWS):
            pg.draw.line(surface, (128, 128, 128), (sx, sy + row * Game.BLOCK_SIZE),
                         (sx + Game.GAME_WIDTH, sy + row * Game.BLOCK_SIZE))

        for col in range(Game.NUM_COLS):
            pg.draw.line(surface, (128, 128, 128), (sx + col * Game.BLOCK_SIZE, sy),
                         (sx + col * Game.BLOCK_SIZE, sy + Game.GAME_HEIGHT))

    def clear_rows(self, grid):
        num_cleared_lines = 0
        remainder = []
        for row in range(Game.NUM_ROWS - 1, -1, -1):
            r = row + num_cleared_lines
            if Game.EMPTY not in grid[r]:
                num_cleared_lines += 1
                if r > 0:
                    remainder = grid[:r][:]
                    remainder.extend(grid[r + 1:][:])
                else:
                    remainder = grid[r + 1:][:]
                grid = [[Game.EMPTY for _ in range(Game.NUM_COLS)]]
                grid.extend(remainder)

        return grid, num_cleared_lines

    def check_all_clear(self, grid):
        for row in range(Game.NUM_ROWS - 1, -1, -1):
            for val in grid[row]:
                if val != Game.EMPTY:
                    return False

        return True

    def draw_next_shape(self, piece, surface):
        font = pg.font.SysFont('comicsans', 30)
        label = font.render('Next Shape', 1, (255, 255, 255))

        sx = Game.GRID_START_X + Game.GAME_WIDTH + 50
        sy = Game.GRID_START_Y + Game.GAME_HEIGHT / 2 - 100

        for i, row in enumerate(piece.shape[0]):
            for j, col in enumerate(row):
                if col == '0':
                    pg.draw.rect(surface, piece.color,
                                 (sx + j * Game.BLOCK_SIZE, sy + i * Game.BLOCK_SIZE, Game.BLOCK_SIZE, Game.BLOCK_SIZE), 0)

        surface.blit(label, (sx + 10, sy - 30))

    def draw_window(self, surface, grid, score=0):
        surface.fill((0, 0, 0))

        pg.font.init()
        font = pg.font.SysFont('comicsans', 60)
        label = font.render('Tetris', 1, (255, 255, 255))

        surface.blit(label, (Game.GRID_START_X + Game.GAME_WIDTH / 2 - (label.get_width() / 2), 30))

        # current score
        font = pg.font.SysFont('comicsans', 30)
        label = font.render('Score: ' + str(score), 1, (255, 255, 255))

        sx = Game.GRID_START_X + Game.GAME_WIDTH + 50
        sy = Game.GRID_START_Y + Game.GAME_HEIGHT / 2 - 100

        surface.blit(label, (sx + 20, sy + 160))

        sx = Game.GRID_START_X - 200
        sy = Game.GRID_START_Y + 200

        surface.blit(label, (sx + 20, sy + 160))

        for i in range(Game.NUM_ROWS):
            for j in range(Game.NUM_COLS):
                pg.draw.rect(surface, grid[i][j],
                             (Game.GRID_START_X + j * Game.BLOCK_SIZE, Game.GRID_START_Y + i * Game.BLOCK_SIZE, Game.BLOCK_SIZE, Game.BLOCK_SIZE), 0)

        pg.draw.rect(surface, (255, 0, 0), (Game.GRID_START_X, Game.GRID_START_Y, Game.GAME_WIDTH, Game.GAME_HEIGHT), 5)

        self.draw_grid(surface, grid)

    def game_start(self, organism, show):
        locked_grid = self.create_grid()
        gen_shape = []

        get_new_piece = False
        check_lost = False
        run = True
        current_piece = self.get_shape(gen_shape)
        next_piece = self.get_shape(gen_shape)
        clock = pg.time.Clock()
        play_time = 0
        fall_time = 0
        fall_delay = 40
        piece_used = 1
        score = 0

        while run:
            fall_time += clock.get_rawtime()
            play_time += clock.get_rawtime()
            clock.tick()

            if fall_time > fall_delay:
                fall_time = 0
                current_piece.row += 1
                if not self.valid_space(current_piece, locked_grid) and current_piece.row > 0:
                    current_piece.row -= 1
                    get_new_piece = True

            curr_state = self.get_state(locked_grid, current_piece)
            action = organism.choose_action(curr_state)

            '''
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                    pg.display.quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        current_piece.col -= 1
                        if not self.valid_space(current_piece, locked_grid):
                            current_piece.col += 1
                    if event.key == pg.K_RIGHT:
                        current_piece.col += 1
                        if not self.valid_space(current_piece, locked_grid):
                            current_piece.col -= 1
                    if event.key == pg.K_DOWN:
                        current_piece.row += 1
                        if not self.valid_space(current_piece, locked_grid):
                            current_piece.row -= 1
                    if event.key == pg.K_UP:
                        current_piece.rotation += 1
                        if not self.valid_space(current_piece, locked_grid):
                            current_piece.rotation -= 1
                    if event.key == pg.K_z:
                        current_piece.rotation -= 1
                        if not self.valid_space(current_piece, locked_grid):
                            current_piece.rotation += 1
                    if event.key == pg.K_SPACE:
                        while self.valid_space(current_piece, locked_grid):
                            current_piece.row += 1
                        current_piece.row -= 1
                        get_new_piece = True
                        

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                    pg.display.quit()

            '''

            if action == Game.LEFT:
                current_piece.col -= 1
                if not self.valid_space(current_piece, locked_grid):
                    current_piece.col += 1
            if action == Game.RIGHT:
                current_piece.col += 1
                if not self.valid_space(current_piece, locked_grid):
                    current_piece.col -= 1
            if action == Game.DOWN:
                current_piece.row += 1
                if not self.valid_space(current_piece, locked_grid):
                    current_piece.row -= 1
            if action == Game.UP:
                current_piece.rotation += 1
                if not self.valid_space(current_piece, locked_grid):
                    current_piece.rotation -= 1
            #if event.key == pg.K_z:
            #    current_piece.rotation -= 1
            #    if not self.valid_space(current_piece, locked_grid):
            #        current_piece.rotation += 1
            if action == Game.SPACE:
                while self.valid_space(current_piece, locked_grid):
                    current_piece.row += 1
                current_piece.row -= 1
                get_new_piece = True

            curr_piece_pos = self.convert_shape_format(current_piece)

            if get_new_piece:
                piece_used += 1
                for row, col in curr_piece_pos:
                    if row > -1:
                        locked_grid[row][col] = current_piece.color
                current_piece = next_piece
                next_piece = self.get_shape(gen_shape)
                locked_grid, num_cleared_rows = self.clear_rows(locked_grid)
                score += (0, 5, 10, 20, 40)[num_cleared_rows]
                if self.check_all_clear(locked_grid):
                    score += 80
                get_new_piece = False
                check_lost = True

            curr_grid = [row.copy() for row in locked_grid]

            for row, col in curr_piece_pos:
                if row > -1:
                    curr_grid[row][col] = current_piece.color

            if show:
                self.draw_window(self.win, curr_grid, score)
                self.draw_next_shape(next_piece, self.win)
                pg.display.update()

            if check_lost:
                if self.valid_space(current_piece, locked_grid):
                    check_lost = False
                else:
                    organism.fitness = score*1000 + play_time/10 + piece_used*100
                    run = False
                    '''
                    self.draw_text_middle(self.win, "YOU LOST!", 80, (255, 255, 255))
                    pg.display.update()
                    pg.time.delay(1500)
                    run = False
                    '''

    def main_menu(self):
        pg.display.set_caption('Tetris')

        run = True
        while run:
            self.win.fill(Game.EMPTY)
            self.draw_text_middle(self.win, 'Press Any Key To Play', 60, (255, 255, 255))
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                if event.type == pg.KEYDOWN:
                    self.game_start()

        pg.display.quit()

    def get_state(self, locked_grid, current_piece):
        state = []
        for col in range(Game.NUM_COLS):
            for row in range(Game.NUM_ROWS-1, -1, -1):
                if locked_grid[row][col] == Game.EMPTY or row == 0:
                    state.append(row/Game.NUM_ROWS)
                    break

        state.extend([current_piece.row/(Game.NUM_ROWS-1), current_piece.col/(Game.NUM_COLS-1), current_piece.shape_idx/6, current_piece.rotation/3])

        return state


class Piece:
    def __init__(self, row, col, shape_idx):
        self.row = row
        self.col = col
        self.shape_idx = shape_idx
        self.shape = Game.shapes[shape_idx]
        self.color = Game.shape_colors[shape_idx]
        self.rotation = 0

