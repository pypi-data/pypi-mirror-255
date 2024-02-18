import copy
import logging

import pygame
from pygame.math import Vector2 as Vec2

from asteroidsenv.env.spaceship import Spaceship, MAX_RAY_LENGTH
from asteroidsenv.env.resourcemanager import ResourceManager, rotate_image
from asteroidsenv.env.spacerock import Spacerock
from asteroidsenv.env.utils import circle_circle_collision, line_circle_collision, is_line_intersecting_circle, sign
import gymnasium as gym
import numpy as np
from collections import namedtuple

from asteroidsenv import resource_dir

RayHit = namedtuple('RayHit', ['point', 'object', 'distance'])


class AsteroidsEnv(gym.Env):
    metadata = {
        "render_modes": [
            "human",
            "agent",
            "rgb_array",
            "debug"
        ],
        "obs_types": [
            "pixels",
            "features"
        ],
        "render_fps": 60.0
    }

    def __init__(self, render_mode=None, obs_type=None, num_rays=None, normalize_images=False):
        if render_mode is not None and render_mode in self.metadata["render_modes"]:
            if render_mode == "debug":
                self.render_mode = "human"
                self.render_debug = True
            else:
                self.render_mode = render_mode
                self.render_debug = False
        else:
            # set "human" to be the default render mode
            self.render_mode = "human"
            self.render_debug = False

        self.width, self.height = 840.0, 840.0

        if num_rays is None:
            self.num_rays = 16
        elif type(num_rays) is int:
            assert num_rays > 0
            self.num_rays = num_rays
        else:
            logging.warning("num_rays must be integer but was {}".format(type(num_rays)))
            self.num_rays = 8

        # surface used for rendering
        pygame.display.init()

        if self.render_mode == "human" or self.render_mode == "agent":
            self.surface = pygame.display.set_mode(size=[self.width, self.height])
            self.resource_manager = ResourceManager(resource_dir + '/Resources/Images/', True)

            # setup display for human rendering
            pygame.display.set_caption("Asteroids")

            pygame.font.init()
            self.font = pygame.font.SysFont('arial', 24)
            self.clock = pygame.time.Clock()
        else:
            self.surface = pygame.Surface(size=[self.width, self.height])
            self.resource_manager = ResourceManager(resource_dir + '/Resources/Images/', False)

        # initializes all game components
        self.spaceship = Spaceship(self.resource_manager.load_sprite("Agent.png", True), self.num_rays, Vec2(self.width, self.height))
        self.spacerocks = []
        self.spacerock_image_32 = self.resource_manager.load_sprite("Spacerock.png", True)
        self.spacerock_image_16 = self.resource_manager.load_sprite("Spacerock32.png", True)
        self.spacerock_image_8 = self.resource_manager.load_sprite("Spacerock16.png", True)
        self.spacerock_radius = 32.0
        self.min_spacerock_radius = 16.0
        self.spawn_counter = 0
        self.spawn_delay = 60
        self.ray_hits = []
        self.normalize_images = normalize_images

        for i in range(self.num_rays):
            self.ray_hits.append(RayHit(Vec2(0.0, 0.0), None, MAX_RAY_LENGTH))

        # specify action and feature space for gymnasium
        self.action_space = gym.spaces.Discrete(6)

        if obs_type is None or obs_type not in self.metadata["obs_types"]:
            logging.warning("No obs type or illegal obs type specified, defaulting to features")

            self.obs_type = "features"
        else:
            self.obs_type = obs_type

        if self.obs_type == "pixels":
            if self.normalize_images:
                self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(64, 64, 3), dtype=np.float32)
            else:
                self.observation_space = gym.spaces.Box(0.0, 255.0, shape=(64, 64, 3), dtype=np.uint8)
        elif self.obs_type == "features":
            low = [
                0.0,  # x agent position
                0.0,  # y agent position
                -1.0,  # x forward normal
                -1.0,  # y forward normal
                -1.0,  # x direction
                -1.0,  # y direction
                -1.0,  # forward velocity
                -1.0,  # angular velocity
            ]
            for i in range(self.num_rays):
                low.extend([
                        0.0,  # distance to ray hit
                        -1.0,  # x position of the ray hit
                        -1.0,  # y position of the ray hit
                        -1.0,  # x direction of asteroid
                        -1.0  # y direction of asteroid
                    ]
                )

            high = [
                1.0,  # x agent position
                1.0,  # y agent position
                1.0,  # x forward normal
                1.0,  # y forward normal
                1.0,  # x direction
                1.0,  # y direction
                1.0,  # forward velocity
                1.0,  # angular velocity
            ]
            for i in range(self.num_rays):
                high.extend([
                        1.0,  # distance to ray hit
                        2.0,  # x position of the ray hit
                        2.0,  # y position of the ray hit
                        1.0,  # x direction of asteroid
                        1.0  # y direction of asteroid
                    ]
                )

            self.observation_space = gym.spaces.Box(
                low=np.array(low),
                high=np.array(high),
                dtype=np.float_
            )
        self.reward = 0.0

        self.key_active_images = [self.resource_manager.load_sprite("KeyActive.png")]

        self.key_active_images.extend(
            [
                rotate_image(self.key_active_images[0], 90.0, Vec2(0.0, 0.0), True)[0],
                rotate_image(self.key_active_images[0], 180.0, Vec2(0.0, 0.0), True)[0],
                rotate_image(self.key_active_images[0], 270.0, Vec2(0.0, 0.0), True)[0]
            ]
        )

        self.key_inactive_images = [self.resource_manager.load_sprite("KeyInactive.png")]

        self.key_inactive_images.extend(
            [
                rotate_image(self.key_inactive_images[0], 90.0, Vec2(0.0, 0.0), True)[0],
                rotate_image(self.key_inactive_images[0], 180.0, Vec2(0.0, 0.0), True)[0],
                rotate_image(self.key_inactive_images[0], 270.0, Vec2(0.0, 0.0), True)[0]
            ]
        )

        self.key_shoot_active_image = self.resource_manager.load_sprite("KeyShoot.png")
        self.key_shoot_inactive_image = self.resource_manager.load_sprite("KeyShootInactive.png")

        self.action = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.spaceship.reset()
        self.spacerocks.clear()
        self.spawn_counter = 0

        return self._get_obs(), self._get_info()

    def step(self, action):
        self.action = action
        self.reward = 0.0

        if self.spawn_counter == self.spawn_delay:
            self.spawn_counter = 0
            self._spawn_spacerock()
        else:
            self.spawn_counter += 1.0

        for rock in self.spacerocks:
            rock.update()

        self.spaceship.update(action)

        self._process_collision()

        # delete all rocks that are out of bounds
        self._delete_out_of_screen()

        if self.render_mode == 'human' or self.render_mode == 'agent' or self.obs_type == 'pixels':
            self.render()

        # return tuple of observation, reward, terminated, truncated, info
        return self._get_obs(), self.reward, not self.spaceship.alive, False, self._get_info()

    def _process_collision(self):
        # check for shot spacerock collision and player spacerock collision
        for spacerock in self.spacerocks:
            for shot in self.spaceship.shots:
                if (shot.alive and
                        spacerock.alive and
                        circle_circle_collision(spacerock.center(), spacerock.radius, shot.position, shot.radius)):
                    shot.alive = False
                    spacerock.alive = False

                    if spacerock.radius/2.0 >= self.min_spacerock_radius:
                        # TODO do some fancy angle calculations
                        # TODO maybe make smaller asteroids faster
                        self.spacerocks.append(Spacerock(spacerock.position.copy(), spacerock.radius/2.0, spacerock.direction.rotate(45.0), spacerock.velocity, spacerock.bounds))
                        self.spacerocks.append(Spacerock(spacerock.position.copy(), spacerock.radius/2.0, spacerock.direction.rotate(-45.0), spacerock.velocity, spacerock.bounds))

                    self.reward += 1.0

            # check if any of the hitbox lines are colliding with the asteroid
            if is_line_intersecting_circle(self.spaceship.hitbox.tr, self.spaceship.hitbox.tl, spacerock.center(),
                                           spacerock.radius) or \
                    is_line_intersecting_circle(self.spaceship.hitbox.tl, self.spaceship.hitbox.b, spacerock.center(),
                                                spacerock.radius) or \
                    is_line_intersecting_circle(self.spaceship.hitbox.b, self.spaceship.hitbox.tr, spacerock.center(),
                                                spacerock.radius):
                self.spaceship.alive = False
                self.reward -= 1.0

        self.ray_hits.clear()

        # check for intersection between ray and asteroid
        for ray_point in self.spaceship.ray_points:
            nearest = ray_point
            distance = MAX_RAY_LENGTH
            rock = None

            for spacerock in self.spacerocks:
                hit, point = line_circle_collision(self.spaceship.hitbox.center, ray_point, spacerock.center(),
                                                   spacerock.radius)

                # check if intersection is closer to hitbox center
                if hit and self.spaceship.hitbox.center.distance_to(point) < distance:
                    nearest = point
                    distance = self.spaceship.hitbox.center.distance_to(point)
                    rock = spacerock

            self.ray_hits.append(RayHit(nearest, rock, distance))

    """
    Creates a new instance of Spacerock and appends it to self.spacerocks
    Asteroids can spawn on any side of the screen with equal probability 
    They spawn just outside the visible area
    Their direction is randomized in a window of -45 to 45 degrees toward the center of the screen
    """

    def _spawn_spacerock(self):
        if self.np_random.random() < 0.5:
            if self.np_random.random() < 0.5:
                # spawn asteroid on top

                position = Vec2(self.np_random.random() * self.width, -2.0 * self.spacerock_radius)
                velocity = Vec2(0.0, 1.0).rotate(self.np_random.uniform(-45.0, 45.0))
            else:
                # spawn asteroid on bottom

                position = Vec2(self.np_random.random() * self.width, self.height)
                velocity = Vec2(0.0, -1.0).rotate(self.np_random.uniform(-45.0, 45.0))
        else:
            if self.np_random.random() < 0.5:
                # spawn asteroid on left

                position = Vec2(-2.0 * self.spacerock_radius, self.np_random.random() * self.height)
                velocity = Vec2(1.0, 0.0).rotate(self.np_random.uniform(-45.0, 45.0))
            else:
                # spawn asteroid on right

                position = Vec2(self.width, self.np_random.random() * self.height)
                velocity = Vec2(-1.0, 0.0).rotate(self.np_random.uniform(-45.0, 45.0))

        self.spacerocks.append(Spacerock(position, self.spacerock_radius, velocity, 2.0, Vec2(self.width, self.height)))

    def _delete_out_of_screen(self):
        self.spacerocks = list(filter(lambda x: x.alive, self.spacerocks))

    def _get_obs(self):
        if self.obs_type == "pixels":
            transformed = pygame.transform.scale(self.surface, [64, 64])

            if self.normalize_images:
                return (pygame.surfarray.pixels3d(transformed)/255.0).astype(dtype=np.float32)
            else:
                return pygame.surfarray.pixels3d(transformed).astype(dtype=np.uint8)

        elif self.obs_type == "features":
            features = [
                self.spaceship.hitbox.center.x/self.width,
                self.spaceship.hitbox.center.y/self.height,
                self.spaceship.forward_normal.x,
                self.spaceship.forward_normal.y,
                self.spaceship.direction.x,
                self.spaceship.direction.y,
                self.spaceship.velocity/self.spaceship.max_velocity,
                self.spaceship.angular_velocity/self.spaceship.max_angular_velocity
            ]

            assert len(self.ray_hits) == self.num_rays
            for hit in self.ray_hits:
                if hit.object is not None:
                    features.extend([
                            hit.distance/MAX_RAY_LENGTH,  # distance to ray hit
                            hit.point.x/self.width,  # x position of hit point
                            hit.point.y/self.height,  # y position of hit point
                            hit.object.direction.x,  # x direction of asteroid
                            hit.object.direction.y  # y direction of asteroid
                        ]
                    )
                else:
                    # if no asteroid was hit the endpoint of the ray is passed
                    features.extend([
                            1.0,  # distance to ray hit
                            hit.point.x/self.width,  # x position of hit point
                            hit.point.y/self.height,  # y position of hit point
                            0.0,  # x direction of asteroid
                            0.0  # y direction of asteroid
                        ]
                    )

            return np.array(features)

    def _get_info(self):
        return {}

    def render(self):
        self._render_frame()

        if self.render_mode == "rgb_array":
            array = copy.deepcopy(pygame.surfarray.pixels3d(self.surface))
            return array

    """
    Renders the frame to self.surface
    If self.render_mode is "human" or "agent" it displays the frame on the screen and ticks the clock
    """
    def _render_frame(self):
        self.surface.fill(pygame.color.Color(0, 0, 0, 255))

        if self.render_mode == "human" or self.render_mode == "rgb_array":
            self._render_human()

            if self.render_mode == "human":
                self._render_action()

            if self.render_debug:
                self._render_debug()
        elif self.render_mode == "agent":
            self._render_agent()

        # update screen and lock the framerate
        if self.render_mode == "human" or self.render_mode == "agent":
            pygame.display.flip()
            pygame.event.pump()
            self.clock.tick(self.metadata["render_fps"])

    def _render_human(self):
        self.spaceship.render(self.surface)

        for rock in self.spacerocks:
            if rock.radius == 32.0:
                rock.render(self.surface, self.spacerock_image_32)
            elif rock.radius == 16.0:
                rock.render(self.surface, self.spacerock_image_16)
            else:
                # backup if no texture in the right size is available
                pygame.draw.circle(self.surface, [255, 255, 255, 255], rock.center(), rock.radius, 4)

    def _render_agent(self):
        self.spaceship.render_rays(self.surface)
        self.spaceship.render_info(self.surface, self.font)

        for hit in self.ray_hits:
            pygame.draw.circle(self.surface, [255, 0, 0], hit.point, 4.0)

        pygame.draw.circle(self.surface, [0, 0, 255], self.spaceship.hitbox.center, 4.0)

        pygame.draw.line(self.surface, [0, 255, 0], self.spaceship.hitbox.center,
                         self.spaceship.hitbox.center +
                         self.spaceship.forward_normal * self.spaceship.velocity * self.metadata["render_fps"])
        pygame.draw.line(self.surface, [255, 0, 0], self.spaceship.hitbox.center,
                         self.spaceship.hitbox.center + self.spaceship.direction * MAX_RAY_LENGTH)
        pygame.draw.line(self.surface, [255, 128, 0], self.spaceship.hitbox.center,
                         self.spaceship.hitbox.center +
                         self.spaceship.direction.rotate(90.0) *
                         self.spaceship.angular_velocity * self.metadata["render_fps"])

        for hit in self.ray_hits:
            if hit[1] is not None:
                pygame.draw.line(self.surface, [255, 0, 0], hit.point,
                                 hit.point + hit.object.direction * hit.object.velocity * self.metadata["render_fps"])

    def _render_debug(self):
        self.spaceship.render_info(self.surface, self.font)
        self.spaceship.render_debug(self.surface)
        self.spaceship.render_rays(self.surface)

        for rock in self.spacerocks:
            rock.render_debug(self.surface)

        for hit in self.ray_hits:
            pygame.draw.circle(self.surface, [255, 0, 0], hit.point, 4.0)

    def _render_action(self):
        if self.action == 0:
            self.surface.blit(self.key_inactive_images[0], Vec2(self.width - 80.0, self.height - 80.0))
            self.surface.blit(self.key_inactive_images[2], Vec2(self.width - 80.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[1], Vec2(self.width - 120.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[3], Vec2(self.width - 40.0, self.height - 40.0))
            self.surface.blit(self.key_shoot_inactive_image, Vec2(self.width - 120.0, self.height - 80.0))
        elif self.action == 1:
            self.surface.blit(self.key_active_images[0], Vec2(self.width - 80.0, self.height - 80.0))
            self.surface.blit(self.key_inactive_images[2], Vec2(self.width - 80.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[1], Vec2(self.width - 120.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[3], Vec2(self.width - 40.0, self.height - 40.0))
            self.surface.blit(self.key_shoot_inactive_image, Vec2(self.width - 120.0, self.height - 80.0))
        elif self.action == 2:
            self.surface.blit(self.key_inactive_images[0], Vec2(self.width - 80.0, self.height - 80.0))
            self.surface.blit(self.key_active_images[2], Vec2(self.width - 80.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[1], Vec2(self.width - 120.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[3], Vec2(self.width - 40.0, self.height - 40.0))
            self.surface.blit(self.key_shoot_inactive_image, Vec2(self.width - 120.0, self.height - 80.0))
        elif self.action == 3:
            self.surface.blit(self.key_inactive_images[0], Vec2(self.width - 80.0, self.height - 80.0))
            self.surface.blit(self.key_inactive_images[2], Vec2(self.width - 80.0, self.height - 40.0))
            self.surface.blit(self.key_active_images[1], Vec2(self.width - 120.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[3], Vec2(self.width - 40.0, self.height - 40.0))
            self.surface.blit(self.key_shoot_inactive_image, Vec2(self.width - 120.0, self.height - 80.0))
        elif self.action == 4:
            self.surface.blit(self.key_inactive_images[0], Vec2(self.width - 80.0, self.height - 80.0))
            self.surface.blit(self.key_inactive_images[2], Vec2(self.width - 80.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[1], Vec2(self.width - 120.0, self.height - 40.0))
            self.surface.blit(self.key_active_images[3], Vec2(self.width - 40.0, self.height - 40.0))
            self.surface.blit(self.key_shoot_inactive_image, Vec2(self.width - 120.0, self.height - 80.0))
        elif self.action == 5:
            self.surface.blit(self.key_inactive_images[0], Vec2(self.width - 80.0, self.height - 80.0))
            self.surface.blit(self.key_inactive_images[2], Vec2(self.width - 80.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[1], Vec2(self.width - 120.0, self.height - 40.0))
            self.surface.blit(self.key_inactive_images[3], Vec2(self.width - 40.0, self.height - 40.0))
            self.surface.blit(self.key_shoot_active_image, Vec2(self.width - 120.0, self.height - 80.0))

    def close(self):
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
