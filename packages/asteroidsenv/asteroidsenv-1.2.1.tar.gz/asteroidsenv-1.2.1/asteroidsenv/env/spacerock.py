import pygame
from pygame.math import Vector2 as Vec2

from asteroidsenv.env.utils import ORANGE


class Spacerock:
    def __init__(self, position, radius, direction, velocity, bounds):
        # top left position of the rect
        self.position = position
        self.radius = radius
        self.direction = direction
        self.velocity = velocity
        self.bounds = bounds
        self.alive = True

    def update(self):
        # update position
        self.position += self.direction * self.velocity

        # set alive to false if spacerock is fully out of bounds
        if self.position.x < -2 * self.radius or\
                self.position.x > self.bounds.x or\
                self.position.y < -2 * self.radius or\
                self.position.y > self.bounds.y:
            self.alive = False

    def render(self, surface, image):
        surface.blit(image, self.position)

    def render_debug(self, surface):
        pygame.draw.circle(surface, ORANGE, self.position + Vec2(self.radius), self.radius, 1)

    def center(self):
        return self.position + Vec2(self.radius)
