import numpy as np
from pygame.math import Vector2 as Vec2
from math import copysign, cos, sin


def sign(x):
    return copysign(1, x)


def clamp(min, max, val):
    """
    Returns max if val > max, min if val < min, otherwise returns val
    """
    if val > max:
        return max
    elif val < min:
        return min

    return val


def rotate_point(point, angle):
    """
    Rotates a point around the origin by the specified angle in degrees
    """
    return Vec2(point.x * cos(angle) - point.y * sin(angle),
                point.x * sin(angle) + point.y * cos(angle))


def circle_circle_collision(centerA: Vec2, radiusA, centerB: Vec2, radiusB):
    """
    Check for collision of two circles by calculating their distance
    Circles collide if the distance is less than the sum if both radius
    Returns true if the circles are colliding
    """
    return (centerA - centerB).length() < radiusA + radiusB


def is_line_intersecting_circle(start: Vec2, end: Vec2, center: Vec2, radius: float):
    """
    Check if the circle is colliding with the line segment
    Returns true if a collision is detected
    """
    hit, point = line_circle_collision(start, end, center, radius)

    return hit


# https://stackoverflow.com/a/1084899
def line_circle_collision(start: Vec2, end: Vec2, center: Vec2, radius: float):
    """
    Calculate if the line segment is intersecting the circle
    Return Tuple of Success and nearest collision point
    """
    d = end - start
    f = start - center

    a = d.dot(d)
    b = 2 * f.dot(d)
    c = f.dot(f) - radius * radius

    discriminant = b * b - 4 * a * c

    # no intersection
    if discriminant < 0:
        return False, Vec2(0.0, 0.0)

    discriminant = np.sqrt(discriminant)

    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)

    # t1 is the closest intersection point
    if 0 <= t1 <= 1:
        return True, start + t1 * d
    # t2 is the closest intersection point
    elif 0 <= t2 <= 1:
        return True, start + t2 * d

    # either completely inside the circle, ray is not long enough or ray is going the wrong direction
    return False, Vec2(0.0, 0.0)


WHITE = [255, 255, 255]
ORANGE = [255, 128, 0]
BLUE = [0, 0, 255]
