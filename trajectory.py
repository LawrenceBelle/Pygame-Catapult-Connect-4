import pygame
import math


class PathPredictor:
    def __init__(self, gravity, damping, pos, initial_velocity, time_passed=0.05):
        self.g = gravity # the space.gravity value
        self.d = 1 - damping # the space.damping value
        self.pos_x, self.pos_y = pos
        self.u_x, self.u_y = initial_velocity
        self.t = time_passed        

        self.angle = None
        # directional damping values
        self.d_x = None
        self.d_y = None
        # directional acceleration values
        self.a_x = None
        self.a_y = None
        # works out everything assigned None
        self.solve_unkowns()

        # collects each position calculated
        self.checkpoints = [(self.pos_x, self.pos_y)]
        # number of checkpoints
        self.path_length = 55

    def get_checkpoints(self):
        get_displacement = lambda u, a, t=self.t : u*t + 0.5*a*(t**2)
        update_velocity = lambda u, a, t=self.t : u + a*t

        for _ in range(self.path_length):
            self.u_x, self.u_y = map(update_velocity, [self.u_x, self.u_y], [self.a_x, self.a_y])

            self.solve_unkowns()
            
            self.pos_x += get_displacement(self.u_x, self.a_x)
            self.pos_y += get_displacement(self.u_y, self.a_y)

            self.checkpoints.append((self.pos_x, self.pos_y))

    def solve_unkowns(self):
        # self.angle = math.atan2(self.u_y, self.u_x)

        # self.d_x = self.d * abs(math.cos(self.angle))
        # self.d_y = self.d * abs(math.sin(self.angle))

        # appears to be more accurate when taking damping from x and y velocity instead of the overall velocity
        self.a_x = -self.u_x * self.d
        self.a_y = self.g + self.d*(-self.u_y)

    def draw_path(self, window, colour):
        # draws a line between the checkpoints calculated
        for i in range(len(self.checkpoints)-1):
            pygame.draw.line(window, colour, self.checkpoints[i], self.checkpoints[i+1], 2)



if __name__ == '__main__':
    path_predictor = PathPredictor(500, 0.75, (1000, 400), (-400, -600), 0.1)
    path_predictor.get_checkpoints()
    print(path_predictor.checkpoints)