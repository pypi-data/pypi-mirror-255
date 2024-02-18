import pygame.transform
import math
from pygame.math import Vector2 as Vec2
from enum import IntFlag
from collections import namedtuple
from asteroidsenv.env.utils import sign, rotate_point, WHITE, ORANGE, BLUE, clamp
from asteroidsenv.env.resourcemanager import rotate_image

Hitbox = namedtuple('Hitbox', ['tr', 'tl', 'b', 'center'])


class Action(IntFlag):
    """
    Enum for all possible actions the agent can take
    """
    NONE = 0,
    FORWARD = 1,
    BACKWARD = 2,
    LEFT = 3,
    RIGHT = 4,
    SHOOT = 5


MAX_RAY_LENGTH = 500.0


class Shot:
    def __init__(self, position, direction, velocity, radius, bounds):
        self.position = position
        self.direction = direction
        self.velocity = velocity
        self.radius = radius
        self.bounds = bounds
        self.alive = True

    def update(self):
        self.position += self.direction * self.velocity

        if self.position.x < -2 * self.radius or \
                self.position.x > self.bounds.x or \
                self.position.y < -2 * self.radius or \
                self.position.y > self.bounds.y:
            self.alive = False

    def render(self, surface):
        pygame.draw.circle(surface, WHITE, self.position, self.radius)

    def render_debug(self, surface):
        pygame.draw.circle(surface, ORANGE, self.position + Vec2(self.radius), self.radius, 1)


class Spaceship:
    def __init__(self, image, num_rays, bounds):
        self.bounds = bounds
        self.dimensions = Vec2(image.get_size())
        self.position = bounds / 2.0 - self.dimensions / 2.0
        self.direction = Vec2(0, 1.0)
        self.forward_normal = Vec2(0, 1.0)
        self.velocity = 0.0
        self.acceleration = 1.5
        self.max_velocity = 7.5
        self.drag = 0.1
        self.angular_velocity = 0.0
        self.max_angular_velocity = 4.0
        self.angular_acceleration = 0.25
        self.angular_drag = 0.1
        self.image = image
        self.ray_points = []
        self.update_image = True
        self.rotated_image = self.image
        self.rect = self.image.get_rect()
        self.hitbox = Hitbox(Vec2(0, 0), Vec2(0, 0), Vec2(0, 0), Vec2(0, 0))
        self.shots = []
        self.can_shoot = True
        self.shot_timer = 0
        self.shot_delay = 20
        self.num_rays = num_rays
        self._calculate_rays()
        self._calculate_hitbox()
        self.alive = True

    def reset(self):
        self.position = self.bounds / 2.0 - self.dimensions / 2.0
        self.velocity = 0.0
        self.angular_velocity = 0.0
        self.direction = Vec2(0, 1.0)
        self.forward_normal = Vec2(0, 1.0)
        self.update_image = True
        self.shot_timer = 0
        self.can_shoot = True
        self.alive = True

        self.shots.clear()

        self._calculate_hitbox()
        self._calculate_rays()

    def update(self, action: Action):
        # update movement first
        self._update_movement(action)

        # update the hitbox and rays
        self._calculate_hitbox()
        self._check_bounds()
        self._calculate_rays()

        # update shooting last so shots are created at the right position
        # otherwise they would lack a frame behind
        self._update_shots(action)

    def _update_movement(self, action):
        # process forward and backward movement
        if action == Action.FORWARD:
            # apply positive acceleration
            self.velocity += self.acceleration

            if self.velocity > 0.0:
                # update moving direction if we move forward
                self.forward_normal = self.direction
        elif action == Action.BACKWARD:
            # apply negative acceleration
            self.velocity -= self.acceleration

            if self.velocity < 0.0:
                # update moving direction if we move backwards
                self.forward_normal = self.direction
        else:
            # calculate drag
            drag = self.drag * -sign(self.velocity)

            # if drag is larger than the current velocity hard set velocity to 0
            if abs(drag) < abs(self.velocity):
                self.velocity += drag
            else:
                self.velocity = 0.0

        # clamp velocity in range [-max_velocity, max_velocity]
        self.velocity = clamp(-self.max_velocity, self.max_velocity, self.velocity)

        # process rotation
        if action == Action.LEFT:
            # update rendering direction
            self.angular_velocity -= self.angular_acceleration
        elif action == Action.RIGHT:
            # update rendering direction
            self.angular_velocity += self.angular_acceleration
        else:
            # process angular_drag the same way that normal drag is processed
            angular_drag = self.angular_drag * -sign(self.angular_velocity)

            if abs(angular_drag) < abs(self.angular_velocity):
                self.angular_velocity += angular_drag
            else:
                self.angular_velocity = 0.0

        self.angular_velocity = clamp(-self.max_angular_velocity, self.max_angular_velocity, self.angular_velocity)

        if self.angular_velocity != 0:
            # image needs to be updated next frame
            self.update_image = True

        # update rendering direction
        self.direction = self.direction.rotate(self.angular_velocity)

        # update position in direction of the forward_normal
        # this is not the rendering direction, because after turning
        # the spaceship should continue in the same direction as before turning
        # until a new forward or backward thrust is applied
        self.position += self.forward_normal * self.velocity

    def _update_shots(self, action):
        for shot in self.shots:
            shot.update()

        if not self.can_shoot:
            self.shot_timer -= 1

            if self.shot_timer == 0:
                self.can_shoot = True

        if action == Action.SHOOT:
            self._shoot()

        # delete all shots that are out of bounds
        self.shots = list(filter(lambda x: x.alive, self.shots))

    def _shoot(self):
        if not self.can_shoot:
            return

        # create new shots exactly centered at the front of the hitbox
        position = self.hitbox.b

        # shots will be flying in the direction the spaceship is facing
        self.shots.append(Shot(position, self.direction, 10.0, 4.0, self.bounds))

        self.can_shoot = False
        self.shot_timer = self.shot_delay

    def _check_bounds(self):
        # Outside left bounds edge
        if self.hitbox.center.x < 0.0:
            # translate the hitbox center to the other side of the playable area
            self.position.x = self.bounds.x - self.dimensions.x / 2.0

            # rebuild the hitbox
            self._calculate_hitbox()
        # Outside right edge
        elif self.hitbox.center.x > self.bounds.x:
            self.position.x = -self.dimensions.x / 2.0
            self._calculate_hitbox()

        # Outside top bounds edge
        if self.hitbox.center.y < 0.0:
            self.position.y = self.bounds.y - self.dimensions.y / 2.0
            self._calculate_hitbox()
        # Outside bottom edge
        elif self.hitbox.center.y > self.bounds.y:
            self.position.y = -self.dimensions.y / 2.0
            self._calculate_hitbox()

    def render(self, surface):
        if self.update_image:
            # update the image if the spaceship was rotated
            self.rotated_image, self.rect = rotate_image(self.image,
                                                         self.direction.angle_to(Vec2(0, 1)),
                                                         self.position,
                                                         True)
            self.update_image = False
        else:
            # or just update the rect for rendering
            self.rect = self.rotated_image.get_rect(center=self.image.get_rect(topleft=self.position).center)

        surface.blit(self.rotated_image, self.rect)

        for shot in self.shots:
            shot.render(surface)

    def render_debug(self, surface):
        pygame.draw.line(surface, ORANGE, self.hitbox.tl, self.hitbox.tr)
        pygame.draw.line(surface, ORANGE, self.hitbox.tr, self.hitbox.b)
        pygame.draw.line(surface, ORANGE, self.hitbox.b, self.hitbox.tl)
        pygame.draw.circle(surface, ORANGE, self.hitbox.center, 4.0)

    def render_rays(self, surface):
        for point in self.ray_points:
            pygame.draw.line(surface, BLUE,
                             self.hitbox.center,
                             point)

    def render_info(self, canvas, font):
        image_pos = font.render("Position: ({0:.2f}, {0:.2f})".format(self.position.x, self.position.y), True, WHITE)
        image_vel = font.render("Velocity: {0:.2f}".format(self.velocity), True, WHITE)
        image_ang_vel = font.render("Angular: {0:.2f}".format(self.angular_velocity), True, WHITE)

        canvas.blit(image_pos, Vec2(8, 8))
        canvas.blit(image_vel, Vec2(8, 32))
        canvas.blit(image_ang_vel, Vec2(8, 56))

    def _calculate_hitbox(self):
        # convert angle to radians
        angle = 2 * math.pi - math.radians(self.direction.angle_to(Vec2(0, 1)))

        # create a box with (0,0) as the center
        bl = Vec2(-self.dimensions.x / 2.0, self.dimensions.y / 2.0)
        br = Vec2(self.dimensions.x / 2.0, self.dimensions.y / 2.0)
        tl = Vec2(-self.dimensions.x / 2.0, -self.dimensions.y / 2.0)
        tr = Vec2(self.dimensions.x / 2.0, -self.dimensions.y / 2.0)

        # rotate the box around the origin
        bl = rotate_point(bl, angle)
        br = rotate_point(br, angle)
        tl = rotate_point(tl, angle)
        tr = rotate_point(tr, angle)

        # translate the box back to the right position
        bl += self.position + self.dimensions / 2.0
        br += self.position + self.dimensions / 2.0
        tl += self.position + self.dimensions / 2.0
        tr += self.position + self.dimensions / 2.0

        self.hitbox = Hitbox(tl, tr, bl + (br - bl)/2.0, self.position + self.dimensions / 2.0)

    def _calculate_rays(self):
        self.ray_points.clear()
        for i in range(0, self.num_rays):
            self.ray_points.append(
                self.hitbox.center + (self.direction.rotate(360 * i / self.num_rays).normalize()) * MAX_RAY_LENGTH
            )
