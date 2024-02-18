import gymnasium as gym
import asteroidsenv
import pygame
import numpy as np


def simulate(env: gym.Env, steps: int):
    """
    Simulate the given environment using the policy learned by the q-network
    :param env: environment to be simulated
    :param device: device for torch to use
    :param steps: length of the simulation
    :param model: q-network with the learned policy
    :param capture: if true captures a video of the entire simulation
    """
    clock = pygame.time.Clock()
    surface = pygame.display.set_mode(size=[64, 64])

    fps = env.metadata["render_fps"]

    observation, info = env.reset()
    for i in range(steps):

        observation, reward, terminated, truncated, info = env.step(env.action_space.sample())

        if env.render_mode == "rgb_array":
            image = pygame.surfarray.make_surface(np.transpose(observation[0:3, :, :], axes=(1, 2, 0)) * 255.0)

            surface.blit(image, [0.0, 0.0])

            pygame.event.pump()

            pygame.display.flip()
            clock.tick(env.metadata['render_fps'])

        if terminated or truncated:
            observation, info = env.reset()

    pygame.quit()

env = gym.make('asteroidsenv:Asteroids-pixels-v0', render_mode='rgb_array')
simulate(env, 10_000)

obs, info = env.reset()
for _ in range(10_000):
    obs, reward, terminated, truncated, info = env.step(env.action_space.sample())

    if terminated or truncated:
        obs, info = env.reset()
