import math


class Segment:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.x_vel = 0
        self.y_vel = 0
        self.speed = 0
        self.angle = 0

    def update(self):
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

        self.x += self.x_vel
        self.y += self.y_vel