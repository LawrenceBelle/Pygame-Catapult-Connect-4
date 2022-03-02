import pygame
import pymunk
import time
import os
import numpy as np
from numpy import int8
import random
import math
from menu import *
# from trajectory import PathPredictor
from cpu import CPU

class Catapult_4:
    def __init__(self, width, height):
        # pygame set up
        pygame.init()
        self.clock = pygame.time.Clock()
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = width, height
        self.WINDOW = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Catapult Connect 4")

        # set up fonts
        self.aim_font = pygame.font.SysFont("verdana", 20)
        self.win_font_name = 'hpsimplified'
        self.win_font_size = self.WINDOW_HEIGHT//8   
        self.turn_font_size = self.win_font_size//3    

        # set pymunk space variables
        self.space = None
        self.VERT_GRAVITY_VAL = int(self.WINDOW_HEIGHT/1.5)
        self.DAMPING_VAL = 0.75
        # Distance a disc must travel under between steps to be considered still
        self.disc_dist_tol = 0.003
        self.sol_wait_time = 3

        # I implemented frame rate indepedence but removed it since it messed with the physics
        # The collisions don't work correctly when the discs are allowed to move too much per frame
        self.prev_time = None
        self.current_time = None
        self.dt = None
        self.FPS = 120
        self.STEP_SIZE = 1/50

        # game colours
        self.BLUE = (40, 90, 210)
        self.RED = (255, 0, 0)
        self.YELLOW = (230, 230, 0)
        self.ORANGE = (227, 150, 27)
        self.TEAL = (23, 252, 203)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.DARK_GREY = (50, 50, 50)
        self.GREY = (65, 65, 65)
        self.BG_COLOUR = self.GREY

        # states for the turn and also values that fill the board matrix that represents the current state of the game
        self.turn = 0        
        self.RED_TURN = 0
        self.YELLOW_TURN = 1

        self.RED_PIECE = 1
        self.YELLOW_PIECE = 2
        self.cpu_piece = None
        self.cpu_colour = None

        # disc spawn positions
        self.RED_SPAWN = (5*self.WINDOW_WIDTH//6, self.WINDOW_HEIGHT//2)
        self.YELLOW_SPAWN = (1*self.WINDOW_WIDTH//6, self.WINDOW_HEIGHT//2)

        self.running = True
        self.playing = False 
        self.ready_to_aim = True
        self.resetting = False
        # currently unutilised but functional
        self.aiming = False

        self.player_turn = True
        self.computer_turn = False
        self.vs_cpu = False

        # constants for how far the disc can be launched
        self.disc_launch_factor = min(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)//75
        self.aim_line_max_dis = int(min(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)/3.75)   

        self.aim_line_group = pygame.sprite.Group()
        self.disc_group = pygame.sprite.Group()
        self.button_group = pygame.sprite.Group()
        
        self.buttons = []
        self.button_size = min(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)//10
        self.add_button((self.WINDOW_WIDTH-(self.button_size*2 + 10), self.WINDOW_HEIGHT//15), "Restart_Button.png", "Hover_Restart_Button.png",  self.button_size,  self.button_size, "restart")
        self.add_button((self.WINDOW_WIDTH-self.button_size, self.WINDOW_HEIGHT//15), "Back_Button.png", "Hover_Back_Button.png",  self.button_size,  self.button_size, "back")

        # Game modes hold the rows, columns and connect amount variables
        self.game_modes = {
            'standard' : (6, 7, 4),
            'precision' : (5, 1, 8),
            'practise' : (6, 7, 8) 
        }
        self.game_mode = self.game_modes['standard']

        self.cpu_difficulty = 'medium'

        self.disc = None
        self.board = None       

        self.main_menu = MainMenu(self)
        self.game_mode_menu = GameModeMenu(self)
        self.custom_menu = CustomMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.vs_menu = VersusMenu(self)
        self.current_menu = self.main_menu

    # Aim indicator line when launching discs
    class Aim_Line(pygame.sprite.Sprite):
        def __init__(self, origin, colour, font, window, max_dis):
            super().__init__()
            self.colour = colour
            self.origin = origin
            self.endpoint = origin
            self.line_width = 2
            self.power = None
            self.angle = None

            self.aim_font = font
            self.WINDOW = window
            # maximun line length
            self.max_dis = max_dis

        def update(self):
            # Creates line between first clicked position and current position
            self.endpoint = pygame.mouse.get_pos()
            x_dif = self.endpoint[0]-self.origin[0]
            y_dif = self.endpoint[1]-self.origin[1]
            distance = math.sqrt(x_dif**2 + y_dif**2)
            angle = math.atan2(y_dif , x_dif)

            if distance < self.max_dis:
                pygame.draw.line(self.WINDOW, self.colour, self.origin, self.endpoint, self.line_width)

                power_ind = round(distance / (self.max_dis/100), 1)
                label = self.aim_font.render(f"{power_ind}", 1, self.colour)
                self.WINDOW.blit(label, (self.endpoint[0] + 10, self.endpoint[1] + 10))

            else: # if cursor is further than the max line distance, it gets the angle and draws the line at the set max length
                new_x_dif = math.floor(self.max_dis * math.cos(angle))
                new_y_dif = math.floor(self.max_dis * math.sin(angle))
                self.endpoint = (self.origin[0] + new_x_dif, self.origin[1] + new_y_dif)

                power_ind = 100
        
                pygame.draw.line(self.WINDOW, self.colour, self.origin, self.endpoint, self.line_width)
                label = self.aim_font.render(f"{power_ind}", 1, self.colour)
                self.WINDOW.blit(label, (self.endpoint[0] + 10, self.endpoint[1] + 10))

            self.power = power_ind
            self.angle = angle


    class Disc(pygame.sprite.Sprite):
        def __init__(self, pos, radius, image, turn, space, launch_factor):
            super().__init__()

            # creates disc as pymunk shape and adds to space
            mass = 10
            self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius), body_type=pymunk.Body.DYNAMIC)
            self.body.position = pos # center of the body
            self.shape = pymunk.Circle(self.body, radius)
            self.shape.elasticity = 0.65
            self.shape.friction = 1
            self.space = space
            self.space.add(self.body, self.shape)

            self.image = pygame.transform.scale(pygame.image.load(os.path.join('resources', image)), (2*radius, 2*radius))
            self.rect = self.image.get_rect()
            self.rect.center = pos

            # constant that controls the power of a launch
            self.launch_factor = launch_factor
            self.turn = turn
            # Value that will be added to the board matrix once the disc has settled
            self.piece_value = self.turn + 1
            self.radius = radius

            self.set_in_board = False
            self.path_prediction = None

        def update(self):
            self.rect.center = self.body.position

        def launch(self, angle, power):
            x_component = math.cos(angle) * power * self.launch_factor
            y_component = math.sin(angle) * power * self.launch_factor
            self.body.velocity = (self.body.velocity[0] - x_component, self.body.velocity[1] - y_component)
            # self.path_prediction = PathPredictor(self.space.gravity[1], self.space.damping, self.body.position, self.body.velocity, 0.05)
            # self.path_prediction.get_checkpoints()

        # Run after the disc has stopped moving inside the board
        def set_to_board(self, board, j):
            self.set_in_board = True
            for i in range(board.rows-1, -1, -1):
                if board.filled_spaces[i, j] == 0:
                    board.filled_spaces[i, j] = self.piece_value
                    break


    class Board:
        def __init__(self, space, colour, window, window_width, window_height, rows, cols, connect_amount):
            self.colour = colour
            self.WINDOW = window
            self.WINDOW_HEIGHT = window_height
            self.WINDOW_WIDTH = window_width
    
            # Win cases
            self.H_SOLUTION = 0
            self.V_SOLUTION = 1
            self.PD_SOLUTION = 2
            self.SD_SOLUTION = 3

            # Values in .filled_spaces
            self.EMPTY = 0
            self.RED_PIECE = 1
            self.YELLOW_PIECE = 2

            # Board configuration
            self.rows = rows
            self.cols = cols
            self.CONNECT_AMOUNT = connect_amount  

            # Board sizing
            self.SLOT_SIZE = int(min(self.WINDOW_HEIGHT, self.WINDOW_WIDTH)/11.5)
            self.SLOT_BORDER = self.SLOT_SIZE//10
            self.FRAME_HEIGHT = self.SLOT_SIZE * self.rows 
            self.FRAME_WIDTH = self.cols * (self.SLOT_BORDER + self.SLOT_SIZE) + self.SLOT_BORDER
            #
            self.DISC_RADIUS = (self.SLOT_SIZE-(self.SLOT_SIZE//12))//2 
            self.SOL_LINE_THICKNESS = self.DISC_RADIUS//4

            self.filled_spaces = np.zeros((self.rows, self.cols), dtype=int8)
            # The origin is the vertical centre of the board (not including the base), and on the left hand side
            self.origin = (self.WINDOW_WIDTH//2 - ((self.SLOT_SIZE + self.SLOT_BORDER)*self.cols + self.SLOT_BORDER)//2, self.WINDOW_HEIGHT - self.FRAME_HEIGHT//2 - self.WINDOW_HEIGHT//15) 
            self.base_height = min(self.WINDOW_HEIGHT, self.WINDOW_WIDTH)//20

            self.elasticity = 0.75
            # frame is a list of shapes that make up the board
            self.frame = self.make_frame(space)        
            self.cover_image = pygame.transform.scale(pygame.image.load(os.path.join('resources', 'Board_Front.png')), (self.SLOT_SIZE, self.DISC_RADIUS*2))
            # reference points for drawing the cover
            self.bottom_left_point = (self.frame[0].bb[2], self.frame[0].bb[3] - self.cover_image.get_height())
            self.top_left_point = (self.frame[0].bb[2], self.frame[0].bb[1])

            # points in each column in which a disc would land
            self.query_points = [(self.origin[0] + ((i + 1/2) * (self.SLOT_SIZE + self.SLOT_BORDER)), self.origin[1] + self.FRAME_HEIGHT//2 - self.DISC_RADIUS) for i in range(self.cols)]
            

        def make_frame(self, space):
            frame = []

            for i in range(self.cols + 1):
                # Makes vertical pieces of the board
                body = pymunk.Body(body_type = pymunk.Body.STATIC)
                body.position = (self.origin[0] + (i * (self.SLOT_SIZE + self.SLOT_BORDER)), self.origin[1])
                shape = pymunk.Poly.create_box(body, size=(self.SLOT_BORDER, self.FRAME_HEIGHT))
                shape.elasticity = self.elasticity
                space.add(body, shape)
                frame.append(shape)

            # Builds bottom of the board
            body = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
            # fits base to the board without rounding errors and then adds some extra width
            buffer = self.SLOT_SIZE//5
            base_vertices = [(frame[0].bb[0]-buffer, frame[0].bb[3]), (frame[0].bb[0]-buffer, frame[0].bb[3]+self.base_height), (frame[-1].bb[2]+buffer, frame[0].bb[3]), (frame[-1].bb[2]+buffer, frame[0].bb[3]+self.base_height)]
            shape = pymunk.Poly(body, base_vertices)
            shape.elasticity = self.elasticity
            shape.friction = 1
            space.add(body, shape)
            frame.append(shape)        

            return frame

        def draw_frame(self):
            for poly in self.frame:
                pos_x = int(poly.bb[0])
                pos_y = int(poly.bb[1])
                width = int(poly.bb[2] - poly.bb[0])
                height = int(poly.bb[3] - poly.bb[1])
                pygame.draw.rect(self.WINDOW, self.colour, pygame.Rect(pos_x, pos_y, width, height))     

        def update_query_points(self, i):
            # if current query_point isn't in the top row
            if self.query_points[i][1] - self.DISC_RADIUS*2 > self.origin[1] - self.FRAME_HEIGHT//2:
                self.query_points[i] = (self.query_points[i][0], self.query_points[i][1] - self.DISC_RADIUS*2)     
            else:
                self.query_points[i] = (0,0)

        def detect_win(self, piece_value):
            # Check horizontal lines
            for j in range(self.cols - (self.CONNECT_AMOUNT-1)):
                for i in range(self.rows):
                    if np.all(self.filled_spaces[i, j : j+self.CONNECT_AMOUNT] == piece_value):
                        return (self.rows - (i+1), j), self.H_SOLUTION

            # Check vertical lines
            for j in range(self.cols):
                for i in range(self.rows - (self.CONNECT_AMOUNT-1)):
                    if np.all(self.filled_spaces[i : i+self.CONNECT_AMOUNT, j].flatten() == piece_value):
                        return (self.rows - (i+1), j), self.V_SOLUTION   

            # Check diagonal lines
            for j in range(self.cols - (self.CONNECT_AMOUNT-1)):
                for i in range(self.rows - (self.CONNECT_AMOUNT-1)):
                    if np.all(self.filled_spaces[i : i+self.CONNECT_AMOUNT, j : j+self.CONNECT_AMOUNT].diagonal() == piece_value):
                        return (self.rows - (i+1), j), self.PD_SOLUTION   
                    if np.all(np.rot90(self.filled_spaces[i : i+self.CONNECT_AMOUNT, j : j+self.CONNECT_AMOUNT]).diagonal() == piece_value):
                        return (self.rows - (i+1), j), self.SD_SOLUTION        

            return None, None   

        def detect_tie(self):
            if not np.any(self.filled_spaces == self.EMPTY):
                return True
            return False

        def draw_query_points(self, colour):
            for point in self.query_points:
                pygame.draw.circle(self.WINDOW, colour, (point[0], point[1]), 10)

        def draw_cover(self):
            for i in range(self.rows):
                for j in range(self.cols):
                    self.WINDOW.blit(self.cover_image, (self.bottom_left_point[0] + (j*(self.SLOT_SIZE+self.SLOT_BORDER)), self.bottom_left_point[1] - (i*self.cover_image.get_height())))
            vertical_midpoint = (self.top_left_point[1] + (self.bottom_left_point[1] - (self.cover_image.get_height() * (self.rows-1)))) // 2
            pygame.draw.rect(self.WINDOW, self.colour, pygame.Rect(self.origin[0], vertical_midpoint, self.FRAME_WIDTH - self.SLOT_BORDER, vertical_midpoint - self.top_left_point[1])) 


    class Button(pygame.sprite.Sprite):
        def __init__(self, pos, image, hover_image, width, height, function):
            super().__init__()
            self.function = function

            self.image = pygame.image.load(os.path.join('resources', image))
            self.image  = pygame.transform.scale(self.image, (width, height))

            self.hover_image = pygame.image.load(os.path.join('resources', hover_image))
            self.hover_image  = pygame.transform.scale(self.hover_image, (width, height))

            self.rect = self.image.get_rect()
            self.rect.center = pos
            self.hovering = False
            # Starting on true stops the button being pressed immediately
            self.clicked = True

        def check_clicked(self):
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0] and not self.clicked:
                    self.clicked = True
                    return True

            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False
            return False

        def update(self):
            # Swaps images if cursor is over the button
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if not self.hovering:
                    self.hovering = True
                    self.image, self.hover_image = self.hover_image, self.image

            elif self.hovering:
                self.hovering = False
                self.image, self.hover_image = self.hover_image, self.image


    def check_exited(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.current_menu.run_display = False
                return True
        return False


    # Pauses the game but still allows the use of buttons
    def wait(self, wait_time):
        start_time = time.time()
        time_passed = 0
        while time_passed < wait_time:
            if self.check_buttons():
                break
            if self.check_exited():
                break
            self.button_group.update()
            self.button_group.draw(self.WINDOW) 
            pygame.display.update()
            time_passed = time.time() - start_time


    def spawn_disc(self):
        self.turn += 1
        self.turn = self.turn % 2
        if self.turn == self.RED_TURN:
            self.disc = self.Disc(self.RED_SPAWN, self.board.DISC_RADIUS, 'Red_Disc.png', self.turn, self.space, self.disc_launch_factor)
        elif self.turn == self.YELLOW_TURN:
            self.disc = self.Disc(self.YELLOW_SPAWN, self.board.DISC_RADIUS, 'Yellow_Disc.png', self.turn, self.space, self.disc_launch_factor)
        self.disc_group.add(self.disc)
        self.ready_to_aim = True


    # Adds button objects to the game
    def add_button(self, pos, image, hover_image, width, height, function):
        button = self.Button(pos, image, hover_image, width, height, function)
        self.button_group.add(button)
        self.buttons.append(button)


    def check_buttons(self):
        for button in self.buttons:
            if button.check_clicked():
                if button.function == 'restart':
                    self.reset()
                elif button.function == 'back':
                    self.playing = False
                return True
        return False


    def reset(self):
        # Move final frame piece to the left so the pieces all fall out of the frame before resetting
        if self.playing:
            self.resetting = True
            start_time = time.time()
            time_passed = 0
            while self.resetting:
                self.clock.tick(self.FPS)
                if self.check_exited():
                    break

                if self.board.frame[-1].bb[2] > self.board.frame[0].bb[2]:
                    # moves bottom of the board to allow the pieces to fall out
                    self.board.frame[-1].body.position = (self.board.frame[-1].body.position[0] - 10, self.board.frame[-1].body.position[1])

                self.button_group.update()
                self.disc_group.update()
                self.space.step(self.STEP_SIZE)
                self.draw_window()
                pygame.display.update()
                # Waits for bottom piece to be removed before counting down
                if self.board.frame[-1].bb[2] <= self.board.frame[0].bb[2]:
                    time_passed = time.time() - start_time
                if time_passed > 1: 
                    self.resetting = False

        # Refreshes attributes
        self.space = pymunk.Space()
        self.space.gravity = (0, self.VERT_GRAVITY_VAL)  
        self.space.damping = self.DAMPING_VAL

        self.prev_time = None
        self.current_time = None
        self.dt = None

        self.turn = 0
        self.ready_to_aim = True
        self.aiming = False

        self.player_turn = True
        self.computer_turn = False

        self.disc_group = pygame.sprite.Group()

        self.board = self.Board(self.space, self.BLUE, self.WINDOW, self.WINDOW_WIDTH, self.WINDOW_HEIGHT, self.game_mode[0], self.game_mode[1], self.game_mode[2])

        if self.vs_cpu:
            if self.game_mode == self.game_modes['precision']:
                # Always lets player move first in precision since it is unwinnable vs an extreme cpu
                p = 0
            else:
                p = random.randrange(2)
            self.cpu_piece = [self.RED_PIECE, self.YELLOW_PIECE][p]
            self.cpu_colour = [self.RED, self.YELLOW][p]
            self.cpu = CPU(self, self.cpu_piece, [self.RED_SPAWN, self.YELLOW_SPAWN][p], self.cpu_difficulty)
            if self.cpu_piece == self.YELLOW_PIECE:
                self.switch_turns()

        if self.playing:
            self.game_loop()


    def create_aim_indicator(self, mouse_pos, disc_pos):
        dist_from_disc = math.dist(mouse_pos, disc_pos)
        if dist_from_disc < self.disc.radius:
            aim_line = self.Aim_Line(mouse_pos, self.BLACK, self.aim_font, self.WINDOW, self.aim_line_max_dis)
            self.aim_line_group.add(aim_line)
            self.aiming = True
            return aim_line        


    def release_aim_indicator(self, aim_line):
        self.aim_line_group.remove(aim_line)
        if aim_line.power > 0:
            self.disc.launch(aim_line.angle, aim_line.power)
            del aim_line
            self.ready_to_aim = False
        self.aiming = False
        return None


    def remove_disc(self):
        self.disc_group.remove(self.disc)
        self.space.remove(self.disc.shape, self.disc.body)        


    def draw_solution_line(self, winning_cell, line_direction, colour):
        # Same as query point locations
        winning_point = (self.board.origin[0] + int(((winning_cell[1] + 1/2) * (self.board.SLOT_SIZE + self.board.SLOT_BORDER))), self.board.origin[1] + self.board.FRAME_HEIGHT//2 - ((2 * winning_cell[0] + 1) * self.board.DISC_RADIUS))
        # Draws line through the winning section
        if line_direction == self.board.H_SOLUTION:
            pygame.draw.line(self.WINDOW, colour, winning_point, (winning_point[0] + ((self.board.CONNECT_AMOUNT-1) * (self.board.SLOT_SIZE + self.board.SLOT_BORDER)), winning_point[1]), self.board.SOL_LINE_THICKNESS)
        elif line_direction == self.board.V_SOLUTION:
            pygame.draw.line(self.WINDOW, colour, winning_point, (winning_point[0], winning_point[1] + (2 * (self.board.CONNECT_AMOUNT-1) * self.board.DISC_RADIUS)), self.board.SOL_LINE_THICKNESS)
        elif line_direction == self.board.PD_SOLUTION:
            pygame.draw.line(self.WINDOW, colour, winning_point, (winning_point[0] + ((self.board.CONNECT_AMOUNT-1) * (self.board.SLOT_SIZE + self.board.SLOT_BORDER)), winning_point[1] + (2 * (self.board.CONNECT_AMOUNT-1) * self.board.DISC_RADIUS)), self.board.SOL_LINE_THICKNESS)
        elif line_direction == self.board.SD_SOLUTION:
            pygame.draw.line(self.WINDOW, colour, (winning_point[0], winning_point[1] + (2 * (self.board.CONNECT_AMOUNT-1) * self.board.DISC_RADIUS)), (winning_point[0] + ((self.board.CONNECT_AMOUNT-1) * (self.board.SLOT_SIZE + self.board.SLOT_BORDER)), winning_point[1]), self.board.SOL_LINE_THICKNESS)
        pygame.display.update()


    def draw_text(self, font_name, pos, size, colour, text):
        font = pygame.font.SysFont(font_name, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.center = pos
        self.WINDOW.blit(text_surface, text_rect)


    # Returns if the game has been won in the 'precision' gamemode
    def detect_precision_win(self):
        if np.count_nonzero(self.board.filled_spaces == self.disc.piece_value) > self.board.rows//2:
            return True
        return False


    def print_result(self, tie = False):
        result = 'No one Wins!'
        sub_result = "(Isn't that fun?)"
        result_pos = (self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//8)
        if not tie:
            if self.disc.turn == self.RED_TURN:
                result = 'Red Wins!'
                self.draw_text(self.win_font_name, result_pos, self.win_font_size, self.RED, result)
            if self.disc.turn == self.YELLOW_TURN:
                result = 'Yellow Wins!'
                self.draw_text(self.win_font_name, result_pos, self.win_font_size, self.YELLOW, result)
        else: 
            self.draw_text(self.win_font_name, result_pos, self.win_font_size, self.BLACK, result)
            self.draw_text(self.win_font_name, (result_pos[0], result_pos[1] + self.win_font_size), self.win_font_size//2, self.BLACK, sub_result)
        pygame.display.update()


    # Shows whose turn it currently is
    def show_turn(self):
        font = pygame.font.SysFont(self.win_font_name, self.turn_font_size)
        text_surface = font.render("Computer's turn:", True, self.cpu_colour)
        self.WINDOW.blit(text_surface, (self.WINDOW_WIDTH//50, self.WINDOW_HEIGHT//50))


    def draw_window(self):
        self.WINDOW.fill(self.BG_COLOUR)
        self.disc_group.draw(self.WINDOW)
        self.board.draw_frame()
        #self.board.draw_query_points(self.BLACK)
        self.aim_line_group.update() 
        self.button_group.draw(self.WINDOW)   
        self.board.draw_cover()           
        # if self.disc.path_prediction:
        #     self.disc.path_prediction.draw_path(self.WINDOW, self.BLACK)
        if self.computer_turn:
            self.show_turn()
        #pygame.display.update()        


    def end_game(self, tie = False):
        self.print_result(tie)
        self.wait(self.sol_wait_time)
        self.reset()     


    # Allows for time independence but is unused as it allows the discs to move through board walls
    def update_delta_time(self):
        self.current_time = time.time()
        self.dt = self.current_time - self.prev_time
        self.prev_time = self.current_time     
        self.STEP_SIZE = self.dt * 2.3


    def switch_turns(self):
        if self.player_turn:
            self.player_turn = False
            self.computer_turn = True

        elif self.computer_turn:
            self.player_turn = True
            self.computer_turn = False


    def game_loop(self):
        if self.playing:

            # initialises game
            self.spawn_disc()
            aim_line = None
            temp_disc_pos = (0, 0)
            self.prev_time = time.time()

        while self.playing:
            self.clock.tick(self.FPS)

            # self.update_delta_time()

            self.draw_window()
            pygame.display.update()
          
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running, self.playing = False, False
                    self.current_menu.run_display = False

                # Player aim and launch disc
                if event.type == pygame.MOUSEBUTTONDOWN and self.player_turn:
                    if self.ready_to_aim:
                        aim_line = self.create_aim_indicator(event.pos, self.disc.rect.center)

                if event.type == pygame.MOUSEBUTTONUP and aim_line and self.player_turn:
                    aim_line = self.release_aim_indicator(aim_line)

                # Cheat for testing
                # if event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_s:
                #         self.disc.body.position = pygame.mouse.get_pos()

            # CPU aim and launch disc
            if self.computer_turn and self.ready_to_aim:
                self.cpu.aim_disc(self.Aim_Line(self.cpu.piece_spawn, self.BLACK, self.aim_font, self.WINDOW, self.aim_line_max_dis))
                self.release_aim_indicator(self.cpu.aim_line)

            # Suspends space if a disc has just spawned
            if not self.ready_to_aim:
                self.space.step(self.STEP_SIZE)

            self.disc_group.update()
            # Checks if disc has fallen off screen
            if self.disc.rect.top > self.WINDOW_HEIGHT:
                self.remove_disc()
                self.spawn_disc()
                if self.vs_cpu:
                    self.switch_turns()

            # Checks if a disc is no longer moving
            if math.dist(temp_disc_pos, self.disc.body.position) < self.disc_dist_tol and not self.ready_to_aim:
                for i, point in enumerate(self.board.query_points):
                    if self.disc.shape.point_query(point)[2] < 0:
                        self.disc.set_to_board(self.board, i)
                        self.board.update_query_points(i)
                        break

                # Removes discs settled outside the board
                if not self.disc.set_in_board:
                    self.remove_disc()

                # Checking for the end of the game
                if self.disc.set_in_board and self.game_mode == self.game_modes['precision']:
                    if self.detect_precision_win():
                        self.end_game()

                winning_cell, line_direction = self.board.detect_win(self.disc.piece_value)
                if winning_cell:
                    self.draw_solution_line(winning_cell, line_direction, self.ORANGE)
                    self.end_game()

                if self.board.detect_tie():
                    self.end_game(True)

                self.spawn_disc()

                # make player turn if computer turn and vice versa if vs cpu
                if self.vs_cpu:
                    self.switch_turns()

            self.button_group.update()
            self.check_buttons()            

            temp_disc_pos = self.disc.body.position      


if __name__ == '__main__':
    game = Catapult_4()
    game.game_loop()
