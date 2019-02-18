import pygame as pg
from NEAT import *


class Game:
    window_width = 1000
    window_height = 600
    screen_width = 500
    screen_height = 500
    screen_x = (window_width - screen_width)/2
    screen_y = (window_height - screen_height)/2

    ground_thickness = 14
    wall_thickness = 6
    white_space_width = screen_width - wall_thickness*2
    white_space_height = screen_height - wall_thickness - ground_thickness
    white_space_start_x = screen_x + wall_thickness
    white_space_start_y = screen_y + wall_thickness
    white_space_end_x = screen_x + screen_width - wall_thickness
    white_space_end_y = screen_y + screen_height - ground_thickness

    bird_color = [(255, 0, 0), (255, 165, 0), (12, 124, 21), (15, 27, 155), (255, 255, 0), (0, 0, 255), (128, 0, 128), (160, 160, 160), (0, 255, 255), (255, 178, 247)]
    colors = {
        'black':(0, 0, 0),
        'red':(255, 0, 0),
        'orange':(255, 165, 0),
        'yellow':(255, 255, 0),
        'green':(0, 255, 0),
        'blue':(0, 0, 255),
        'purple':(128, 0, 128),
        'white':(255, 255, 255),
        'gray':(160,160,160),
        'ice':(0,255,255),
        'brown':(139,69,19)
    }

    num_inputs = 3
    num_actions = 1
    actions_str = ['Flap']
    flap = 3

    def draw_background(self, window):
        window.fill(Game.colors['white'])
        pg.draw.rect(window, Game.colors['brown'], (Game.screen_x, Game.white_space_end_y, Game.screen_width, Game.ground_thickness), 0)
        pg.draw.rect(window, Game.colors['black'], (Game.screen_x, Game.screen_y, Game.screen_width, Game.wall_thickness), 0)
        pg.draw.rect(window, Game.colors['black'], (Game.screen_x, Game.screen_y, Game.wall_thickness, Game.screen_height), 0)
        pg.draw.rect(window, Game.colors['black'], (Game.white_space_end_x, Game.screen_y, Game.wall_thickness, Game.screen_height), 0)

    def check_out_of_bound(self, bird):
        if bird.y - Bird.radius < Game.white_space_start_y:
            return True

        if bird.y + Bird.radius > Game.white_space_end_y:
            return True

        return False

    def check_game_end(self, bird, pipes):
        if self.check_out_of_bound(bird):
            return True

        if len(pipes) < 1:
            return False

        for pipe in pipes:
            if bird.x + Bird.radius > pipe.left_x and bird.x - Bird.radius < pipe.right_x:
                if bird.y + Bird.radius > pipe.hole_bottom_y or bird.y - Bird.radius < pipe.hole_top_y:
                    return True

        return False

    def draw_neat_info(self, surface, info):
        font = pg.font.SysFont('comicsans', 30)
        sx = Game.screen_x - 180
        sy = Game.screen_y
        str_list = ["generation", "population", "num_species"]#, "species", "organism", "nodes", "connections", "innovation #"]

        for i in range(len(str_list)):
            text = str_list[i] + ": " + str(info[i])
            label = font.render(text, 1, Game.colors['black'])
            surface.blit(label, (sx, sy))
            sy += 30
            if i == 0 or i == 2 or i == 4 or i == 7:
                sy += 20

        label = font.render("fitness: ", 1, Game.colors['black'])
        surface.blit(label, (sx, sy))

        return sx, sy

    def draw_num_survivors(self, surface, num_alive):
        font = pg.font.SysFont("comicsans", 30)
        sx = Game.white_space_end_x + Game.wall_thickness + 20
        sy = Game.screen_y

        pg.draw.rect(surface, Game.colors['white'], (sx, sy, 100, 40))
        label = font.render(str(num_alive) + " alive", 1, Game.colors['black'])
        surface.blit(label, (sx, sy))

    def draw_input_output(self, surface, state, actions):
        numbers = []
        for s in state:
            numbers.append("{:.2f}".format(s))

        if len(actions) < 1:
            numbers.append("Do Nothing")
        else:
            a_str = ""
            for i, action in enumerate(actions):
                comma = "" if i == 0 else ", "
                a_str += comma + Game.actions_str[action - Game.num_inputs]
            numbers.append(a_str)

        texts = ["bird_pos", "pipe_pos", "velocity", "action"]

        font = pg.font.SysFont('comicsans', 30)
        sx = Game.screen_x + Game.screen_width + 20
        sy = Game.screen_y

        pg.draw.rect(surface, Game.colors['white'], (sx, sy, 250, 150), 0)

        for i,v in enumerate(texts):
            label = font.render(v + ": " + numbers[i], 1, Game.colors['black'])
            surface.blit(label, (sx, sy))
            sy += 20

    def draw_fitness(self, surface, fit, sx, sy):
        font = pg.font.SysFont('comicsans', 30)
        pg.draw.rect(surface, Game.colors['white'], (sx+80, sy, 100, 20), 0)
        text = "{:.2f}".format(fit)
        label = font.render(text, 1, Game.colors['black'])
        surface.blit(label, (sx+80, sy))

    def draw_pipes(self, surface, pipes):
        if len(pipes) > 0:
            for pipe in pipes:
                draw_width = min(pipe.right_x - Game.white_space_start_x, Game.white_space_end_x - pipe.left_x, pipe.width)
                if draw_width > 0:
                    pg.draw.rect(surface, Game.colors['green'], (
                    max(Game.white_space_start_x, pipe.left_x), Game.white_space_start_y, draw_width,
                    Game.white_space_height), 0)
                    pg.draw.rect(surface, Game.colors['white'], (
                        max(Game.white_space_start_x, pipe.left_x), pipe.hole_top_y, draw_width,
                        Pipe.hole_height), 0)

    def draw_birds(self, surface, birds):
        if len(birds) > 0:
            for bird in birds.values():
                pg.draw.circle(surface, bird.color, (bird.x, int(bird.y)), Bird.radius, 0)

    def get_pipe(self, pipes):
        for pipe in pipes:
            if pipe.right_x > Bird.start_x:
                return pipe

    def get_state(self, bird, pipe):
        #bird_pos = (Game.white_space_end_y - bird.y) / Game.white_space_height
        #pipe_pos = (Game.white_space_end_y - pipe.hole_center_y) / Game.white_space_height
        del_y = (pipe.hole_center_y - bird.y) / Game.white_space_height
        bird_vel = -1*bird.vel_y / Bird.max_vel_y
        state = [del_y, bird_vel, 1.0]

        return state

    def game_start(self, window, organisms, info, user_mode=False):
        pg.font.init()
        self.draw_background(window)
        self.draw_num_survivors(window, len(organisms))
        fit_x, fit_y = self.draw_neat_info(window, info)
        run = True
        clock = pg.time.Clock()
        play_time = 0
        score = 0
        pipes = [Pipe()]
        #key_delay = 0

        birds = dict()
        for organism in organisms:
            newBird = Bird(random.randint(Game.white_space_start_y+20, Game.white_space_end_y-20), random.choice(Game.bird_color))
            birds[organism] = newBird

        # if user_mode:
        #     pg.key.set_repeat(100, 100)

        while run:
            clock.tick()
            play_time += clock.get_rawtime()
            # key_delay += clock.get_rawtime()

            if pipes[-1].right_x + Pipe.interval < Game.white_space_end_x:
                pipes.append(Pipe())

            for i in range(len(pipes)-1, -1, -1):
                pipes[i].left_x += Pipe.speed
                pipes[i].right_x += Pipe.speed
                pipes[i].center_x += Pipe.speed
                if pipes[i].right_x < Bird.start_x and not pipes[i].scored:
                    score += 10
                    pipes[i].scored = True
                if pipes[i].right_x <= Game.white_space_start_x:
                    pipes.remove(pipes[i])

            fitness = score + play_time / 1000

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                    pg.display.quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        run = False
                        pg.display.quit()
                #     if event.key == pg.K_SPACE:
                #         bird.vel_y = max(Bird.max_vel_y, bird.vel_y + Bird.lift_force)

        # if not user_mode:
            weaklings = []
            next_pipe = self.get_pipe(pipes)
            for organism, bird in birds.items():
                state = self.get_state(bird, next_pipe)
                actions = organism.choose_action(state)
                if len(actions) > 0:
                    for action in actions:
                        if action == Game.flap:
                            bird.vel_y = max(Bird.max_vel_y, bird.vel_y + Bird.lift_force)

                bird.y += bird.vel_y
                bird.vel_y = min(-1*Bird.max_vel_y, bird.vel_y + Bird.gravity)

                if self.check_game_end(bird, pipes):
                    organism.fitness = fitness
                    weaklings.append(organism)

            for weakling in weaklings:
                del birds[weakling]

            if len(birds) < 1:
                run = False

            pg.draw.rect(window, Game.colors['white'], (Game.white_space_start_x, Game.white_space_start_y, Game.white_space_width, Game.white_space_height), 0)
            self.draw_pipes(window, pipes)
            self.draw_birds(window, birds)
            self.draw_fitness(window, fitness, fit_x, fit_y)
            self.draw_num_survivors(window, len(birds))

            # if not user_mode:
            #     self.draw_input_output(window, state, actions)

            pg.display.update()


class Bird:
    start_x = Game.screen_x + Game.screen_width//4
    radius = 8
    lift_force = -1.5
    gravity = 0.015
    max_vel_y = -1.5

    def __init__(self, y, color):
        self.x = int(Bird.start_x)
        self.y = y
        self.color = color
        self.vel_y = 0


class Pipe:
    width = 50
    hole_height = 140
    speed = -0.5
    interval = 120
    
    def __init__(self, left_x=Game.white_space_end_x):
        self.left_x = left_x
        self.right_x = self.left_x + Pipe.width
        self.center_x = self.left_x + Pipe.width/2
        self.hole_center_y = random.randint(Game.white_space_start_y + Pipe.hole_height, Game.white_space_end_y - Pipe.hole_height)
        self.hole_top_y = int(self.hole_center_y - Pipe.hole_height/2)
        self.hole_bottom_y = int(self.hole_center_y + Pipe.hole_height/2)
        self.scored = False
