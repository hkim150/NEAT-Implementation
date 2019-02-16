import pygame as pg
from NEAT import *


class Game:
    window_width = 1000
    window_height = 500
    screen_width = 400
    screen_height = 400
    screen_x = (window_width - screen_width) // 2
    screen_y = (window_height - screen_height) // 2

    ice_height = 10
    wall_thickness = 6
    white_space_width = screen_width - 2*wall_thickness
    white_space_height = screen_height - wall_thickness - ice_height
    radius = 8
    hole_velocity = 1.5
    hole_width = 60
    hole_thickness = 30
    move_interval = 0
    hole_interval = 500

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
        'ice':(0,255,255)
    }

    num_inputs = 1
    num_actions = 2
    actions_str = ['Left', 'Right']
    left = 1
    right = 2

    def draw_background(self, window):
        window.fill(Game.colors['white'])
        pg.draw.rect(window, Game.colors['ice'], (Game.screen_x, Game.screen_y + Game.screen_height - Game.ice_height, Game.screen_width, Game.ice_height), 0)
        pg.draw.rect(window, Game.colors['black'], (Game.screen_x, Game.screen_y, Game.screen_width, Game.wall_thickness), 0)
        pg.draw.rect(window, Game.colors['black'], (Game.screen_x, Game.screen_y, Game.wall_thickness, Game.screen_height), 0)
        pg.draw.rect(window, Game.colors['black'], (Game.screen_x + Game.screen_width - Game.wall_thickness, Game.screen_y, Game.wall_thickness, Game.screen_height), 0)

    def check_out_of_bound(self, player_x):
        left_bound = -1 * Game.screen_width//2 + Game.wall_thickness + Game.radius
        if player_x < left_bound:
            return True, left_bound

        right_bound = Game.screen_width//2 - Game.wall_thickness - Game.radius
        if player_x > right_bound:
            return True, right_bound

        return False, player_x

    def check_game_end(self, player_x, holes):
        if len(holes) < 1:
            return False

        if holes[0][1] > Game.white_space_height - Game.hole_thickness/2 - Game.radius*2:
            if player_x - Game.radius < holes[0][0] - Game.hole_width/2 or player_x + Game.radius > holes[0][0] + Game.hole_width/2:
                return True

        return False

    def draw_info(self, surface, info):
        pg.font.init()
        font = pg.font.SysFont('comicsans', 30)
        sx = 100
        sy = Game.screen_y
        str_list = ["generation", "population", "num_species", "species", "organism", "nodes", "connections", "innovation #"]

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

        texts = ["player_x", "del_x", "del_y", "velocity", "actions"]

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

    def get_state(self, player_x, holes, velocity):
        h_x, h_y = 0.0, 0.0
        x = player_x / (Game.screen_width//2 - Game.wall_thickness - Game.radius)
        if len(holes) > 0:
            h_x, h_y = holes[0]
            del_x = (h_x - player_x) / (Game.white_space_width - Game.hole_width/2 - Game.radius)
            del_y = (Game.white_space_height - h_y - Game.radius) / (Game.white_space_height - Game.hole_thickness/2 - Game.radius)
        state = [x, del_x, del_y, velocity]

        return state

    def game_start(self, window, organism, info, user_mode=False):
        self.draw_background(window)
        fit_x, fit_y = self.draw_info(window, info)
        run = True
        game_end = False
        clock = pg.time.Clock()
        fitness = 0

        move_delay = 0

        player_x = 0
        holes = []
        hole_delay = 0
        holes.append([(random.random() - 0.5) * (Game.white_space_width - Game.hole_width), -1*Game.hole_thickness//2])

        max_velocity = 3.5
        velocity = (random.random() - 0.5) * max_velocity

        if user_mode:
            pg.key.set_repeat(100, 100)
            Game.move_interval = 10

        while run:
            clock.tick()
            fitness += clock.get_rawtime()/100

            move_delay += clock.get_rawtime()
            hole_delay += clock.get_rawtime()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                    pg.display.quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                            run = False
                            pg.display.quit()
                    if user_mode:
                        if event.key == pg.K_LEFT:
                            velocity -= 0.5
                        if event.key == pg.K_RIGHT:
                            velocity += 0.5

            if not user_mode:
                state = self.get_state(player_x, holes, velocity)
                actions = organism.choose_action([state[1]])

                if len(actions) > 0:
                    for action in actions:
                        if action == Game.left:
                            velocity = max(velocity - 0.5, -1*max_velocity)
                        if action == Game.right:
                            velocity = min(velocity + 0.5, max_velocity)

            for hole in holes:
                hole[1] += Game.hole_velocity

            if len(holes) > 0:
                if holes[0][1] - Game.hole_thickness/2 > Game.white_space_height:
                    del holes[0]
                    fitness += 15

            if move_delay > Game.move_interval:
                player_x += velocity
                game_end, player_x = self.check_out_of_bound(player_x)
                game_end = game_end or self.check_game_end(player_x, holes)
                move_delay = 0

            if hole_delay > Game.hole_interval:
                holes.append([(random.random() - 0.5) * (Game.white_space_width - Game.hole_width), -1* Game.hole_thickness//2])
                hole_delay = 0

            pg.draw.rect(window, Game.colors['white'], (Game.screen_x + Game.wall_thickness, Game.screen_y + Game.wall_thickness, Game.white_space_width, Game.white_space_height), 0)
            for hole in holes:
                pg.draw.rect(window, Game.colors['red'], (Game.screen_x + Game.wall_thickness, max(1, int(hole[1] - Game.hole_thickness/2)) + Game.screen_y + Game.wall_thickness, Game.white_space_width, min(Game.hole_thickness, Game.white_space_height - int(hole[1]) + Game.hole_thickness/2, int(Game.hole_thickness//2 + hole[1]))), 0)
                pg.draw.rect(window, Game.colors['white'], (Game.screen_x + Game.screen_width//2 + int(hole[0] - Game.hole_width/2), max(1, int(hole[1] - Game.hole_thickness/2)) + Game.screen_y + Game.wall_thickness, Game.hole_width, min(Game.hole_thickness, Game.white_space_height - int(hole[1] - Game.hole_thickness/2), int(Game.hole_thickness//2 + hole[1]))), 0)
            pg.draw.circle(window, Game.colors['blue'], (Game.screen_x + Game.screen_width//2 + int(player_x), Game.screen_y + Game.screen_height - Game.ice_height - Game.radius), Game.radius, 0)
            self.draw_fitness(window, fitness, fit_x, fit_y)
            if not user_mode:
                self.draw_input_output(window, state, actions)
            pg.display.update()

            if game_end:
                organism.fitness = fitness
                run = False
