import random
import math
import pygame
import sys
import time
import numpy as np
from numpy import int8
from trajectory import PathPredictor

class CPU:
    # will initialise randomly with either yellow or red pieces
    def __init__(self, game, piece_value, piece_spawn, difficulty='medium'):
        self.difficulty = difficulty

        # depth for minimax
        # medium and easy will also miss on purpose
        self.difficulty_depths = {
            'easy' : 1,
            'medium' : 2,
            'extreme' : 4
        }
        self.depth = self.difficulty_depths[self.difficulty]

        self.game = game
        self.board = self.game.board
        # Number of discs needed in a row to win
        self.connect_amount = self.board.CONNECT_AMOUNT
        self.rows = self.board.rows
        self.cols = self.board.cols

        # values in the board's matrix to represent the game's current state
        self.EMPTY = 0
        self.CPU_PIECE = piece_value
        self.PLAYER_PIECE = 1 if self.CPU_PIECE == 2 else 2

        # tuple containing x and y position
        self.piece_spawn = piece_spawn

        self.point_multiplier = 5
        self.point_board = self.score_point_board()

        # Points that the computer aims for in order to get the disc in 
        self.target_points = [(x[0], x[1] - (2*self.board.DISC_RADIUS*self.board.rows)) for x in self.board.query_points]

        # distance from actual point can be from the projection but still accurate enough
        self.configuring_tol = 2

        # variables needed in configuring the computer player
        self.n = None
        self.config_increment = None

        # Will be a dictionary with the columns as keys and the angle and power to reach them as values
        self.moves = {}
        # mean difference between x value of self.moves values
        self.mean_x_dif = None

        self.configure(game.VERT_GRAVITY_VAL, game.DAMPING_VAL, game.disc_launch_factor, game.aim_line_max_dis, self.board.SLOT_SIZE)

    def wait(self, wait_time):
        start_time = time.time()
        time_passed = 0
        while time_passed < wait_time:
            self.check_exited()
            time_passed = time.time() - start_time

    # Checks if you closed the game window
    def check_exited(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    # Find which powers and angles sink the discs in each column
    def configure(self, gravity, damping, launch_factor, max_line_dist, slot_width):

        # Find vertical power
        x_vel = 0
        y_vel = 0

        self.n = 0
        self.update_increment(max_line_dist)

        endpoint_y = self.piece_spawn[1]
        projection = PathPredictor(gravity, damping, self.piece_spawn, (x_vel, y_vel), 0.05)
        projection.get_checkpoints()
        # is the last prediction too high?
        last_overshot = False
        
        # until the cpu has aimed close enough to the target
        # Find vertical power
        while abs(projection.checkpoints[-1][1] - self.target_points[0][1]) > self.configuring_tol:

            self.check_exited()

            if projection.checkpoints[-1][1] < self.target_points[0][1]:
                if not last_overshot:
                    self.update_increment(max_line_dist)
                endpoint_y -= self.config_increment
                last_overshot = True
            else:
                if last_overshot:
                    self.update_increment(max_line_dist)
                endpoint_y += self.config_increment
                last_overshot = False

            y_power = round((self.piece_spawn[1] - endpoint_y) / (max_line_dist/100), 3)
            y_vel = y_power * launch_factor
            velocity = (x_vel, y_vel)                   
  
            projection = PathPredictor(gravity, damping, self.piece_spawn, velocity, 0.05)
            projection.get_checkpoints()

        # Find horizontal powers
        for x in range(self.cols):
            self.n = 0
            self.update_increment(max_line_dist)

            endpoint_x = self.piece_spawn[0]
            projection = PathPredictor(gravity, damping, self.piece_spawn, (x_vel, y_vel), 0.05)
            projection.get_checkpoints()
            # is the last prediction to the left of the target?
            last_to_left = False

            while math.dist(projection.checkpoints[-1], self.target_points[x]) > self.configuring_tol:

                self.check_exited()

                if projection.checkpoints[-1][0] < self.target_points[x][0]:
                    if not last_to_left:
                        self.update_increment(max_line_dist)
                    endpoint_x -= self.config_increment
                    last_to_left = True
                else:
                    if last_to_left:
                        self.update_increment(max_line_dist)
                    endpoint_x += self.config_increment
                    last_to_left = False

                x_power = round((self.piece_spawn[0] - endpoint_x) / (max_line_dist/100), 3)
                x_vel = x_power * launch_factor
                velocity = (x_vel, y_vel)                    

                projection = PathPredictor(gravity, damping, self.piece_spawn, velocity, 0.05)
                projection.get_checkpoints()
            else:
                self.moves[x] = (endpoint_x, endpoint_y)

        if self.cols > 1:
            self.mean_x_dif = sum([abs(self.moves[x][0] - self.moves[x+1][0]) for x in range(len(self.moves)-1)]) / len(self.moves)
        else:
            # If there is only one column, this variable is filled, in order to let the cpu still miss
            self.mean_x_dif = slot_width//8


    # Lessens the increment if overshooting in the configuration
    def update_increment(self, max_line_dist):
        self.n += 10
        self.config_increment = max_line_dist/(2*self.n)

    # Score everything as if the cpu piece has been dropped for the minmax algoirthm

    # Scores individual column and row pairings for the minmax algoirthm
    def score_point_board(self):
        # Score each position on the board based on how many potential solutions they could fill
        point_board = np.zeros((self.board.rows, self.board.cols), dtype=int8)

        for j in range(self.cols - (self.connect_amount-1)):
            for i in range(self.rows):
                for x in range(self.connect_amount):
                    point_board[i, j + x] += self.point_multiplier//2

        # Check vertical lines
        for j in range(self.cols):
            for i in range(self.rows - (self.connect_amount-1)):
                for x in range(self.connect_amount):
                    point_board[i + x, j] += self.point_multiplier//2

        # Check diagonal lines
        for j in range(self.cols - (self.connect_amount-1)):
            for i in range(self.rows - (self.connect_amount-1)):
                for x in range(self.connect_amount):
                    point_board[i + x, j + x] += self.point_multiplier//2
                for x in range(self.connect_amount):
                    point_board[i + (self.connect_amount-1) - x, j + x] += self.point_multiplier//2

        return point_board

    # Scores entire board from the perspective of a certain player for the minmax algoirthm
    def score_position(self, board_matrix, piece):
        score = 0

        # Add score depending on where inside the board the pieces are
        for j in range(self.cols):
            for i in range(self.rows):
                if board_matrix[i, j] == piece:
                    score += self.point_board[i, j]

        # Check horizontal lines
        for j in range(self.cols - (self.connect_amount-1)):
            for i in range(self.rows):
                segment = board_matrix[i, j : j+self.connect_amount]
                score += self.score_segment(segment, piece)

        # Check vertical lines
        for j in range(self.cols):
            for i in range(self.rows - (self.connect_amount-1)):
                segment = board_matrix[i : i+self.connect_amount, j].flatten()
                score += self.score_segment(segment, piece)

        # Check diagonal lines
        for j in range(self.cols - (self.connect_amount-1)):
            for i in range(self.rows - (self.connect_amount-1)):
                segment = board_matrix[i : i+self.connect_amount, j : j+self.connect_amount].diagonal()
                score += self.score_segment(segment, piece) 
                segment = np.rot90(board_matrix[i : i+self.connect_amount, j : j+self.connect_amount]).diagonal()
                score += self.score_segment(segment, piece)

        return score

    # scores a segement of length 4 for the minmax algoirthm
    def score_segment(self, segment, piece):
        segment = [i for i in segment]
        opponent_piece = self.PLAYER_PIECE if piece == self.CPU_PIECE else self.CPU_PIECE
        score = 0 

        for n in range(2, self.connect_amount+1):
            if segment.count(piece) == n and segment.count(self.EMPTY) == self.connect_amount - n:
                score += (n**3) * self.point_multiplier
            #if segment.count(opponent_piece) == n and segment.count(self.EMPTY) == self.connect_amount - n:
            #    score -= ((n-1)**3) * (self.point_multiplier)

        if segment.count(opponent_piece) == self.connect_amount-1 and segment.count(self.EMPTY) == 1:
            score -= ((self.connect_amount-1)**3) * (self.point_multiplier)

        return score

    # Picks all columns not full
    def get_valid_cols(self, board_matrix):
        columns = []
        for col in range(self.cols):
            if board_matrix[0][col] == self.EMPTY:
                columns.append(col)
        return columns

    # Picks first available column of a row
    def get_valid_row(self, board_matrix, col):
        for row in range(self.rows-1, -1, -1):
            if board_matrix[row, col] == 0:
                return row


    def detect_win(self, board_matrix, piece_value):
        # Check horizontal lines
        for j in range(self.cols - (self.connect_amount-1)):
            for i in range(self.rows):
                if np.all(board_matrix[i, j : j+self.connect_amount] == piece_value):
                    return True

        # Check vertical lines
        for j in range(self.cols):
            for i in range(self.rows - (self.connect_amount-1)):
                if np.all(board_matrix[i : i+self.connect_amount, j].flatten() == piece_value):
                    return True 

        # Check diagonal lines
        for j in range(self.cols - (self.connect_amount-1)):
            for i in range(self.rows - (self.connect_amount-1)):
                if np.all(board_matrix[i : i+self.connect_amount, j : j+self.connect_amount].diagonal() == piece_value):
                    return True 
                if np.all(np.rot90(board_matrix[i : i+self.connect_amount, j : j+self.connect_amount]).diagonal() == piece_value):
                    return True       

        return False

    # Checks if the minmax algorithm has reached the end of a game for a certain node
    def is_temrinal_node(self, board_matrix):
        return self.detect_win(board_matrix, self.PLAYER_PIECE) or self.detect_win(board_matrix, self.CPU_PIECE) or not np.any(board_matrix == self.EMPTY)

    def minimax(self, board_matrix, depth, alpha, beta, maximising_player):
        self.check_exited()
        valid_cols = self.get_valid_cols(board_matrix)
        is_terminal = self.is_temrinal_node(board_matrix)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.detect_win(board_matrix, self.CPU_PIECE):
                    return (None, 1000000)
                if self.detect_win(board_matrix, self.PLAYER_PIECE):
                    return (None, -1000000)
                else: # Game ended in a tie
                    return (None, 0)
            else:
                return (None, self.score_position(board_matrix, self.CPU_PIECE))

        if maximising_player:
            value = -math.inf
            column = random.choice(valid_cols)
            for col in valid_cols:
                row = self.get_valid_row(board_matrix, col)
                temp_matrix = board_matrix.copy()
                temp_matrix[row, col] = self.CPU_PIECE
                new_score = self.minimax(temp_matrix, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else: # Minimising player
            value = math.inf
            column = random.choice(valid_cols)
            for col in valid_cols:
                row = self.get_valid_row(board_matrix, col)
                temp_matrix = board_matrix.copy()
                temp_matrix[row, col] = self.PLAYER_PIECE
                new_score = self.minimax(temp_matrix, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value            


    def get_next_move(self):
        pick_randomly = random.random()

        if self.difficulty == 'extreme' or pick_randomly < 0.75:
            col, _ = self.minimax(self.board.filled_spaces, self.depth, -math.inf, math.inf, True)
        else:
            col = random.randrange(self.cols)

        if self.difficulty == 'easy':
            return (self.moves[col][0] + random.normalvariate(0, self.mean_x_dif), self.moves[col][1])
        elif self.difficulty == 'medium':
            return (self.moves[col][0] + random.normalvariate(0, self.mean_x_dif/3), self.moves[col][1])
        elif self.difficulty == 'extreme':
            return self.moves[col]

    # Creates an aiming indicator for the cpu to be launched right after
    def aim_disc(self, aim_line):
        self.aim_line = aim_line

        move = self.get_next_move()
        target_endpoint = (round(move[0]), round(move[1]))

        x_dif = target_endpoint[0] - aim_line.endpoint[0]
        y_dif = target_endpoint[1] - aim_line.endpoint[1]
        distance = math.sqrt(x_dif**2 + y_dif**2)

        aim_line.power =  round(distance / (aim_line.max_dis/100), 1)
        aim_line.angle = math.atan2(y_dif , x_dif)       

        x_increment = x_dif/150
        y_increment = y_dif/150
        
        while aim_line.endpoint != target_endpoint:
            self.check_exited()
            aim_line.endpoint = (aim_line.endpoint[0] + x_increment, aim_line.endpoint[1] + y_increment)
            if aim_line.endpoint[1] + y_increment > target_endpoint[1]:
                aim_line.endpoint = target_endpoint
                self.wait(0.3)
            if self.game.check_buttons():
                break
            self.game.draw_window()
            pygame.draw.line(aim_line.WINDOW, aim_line.colour, aim_line.origin, aim_line.endpoint, aim_line.line_width)
            pygame.display.update()