from gymnasium.envs.registration import register
import os

resource_dir = os.path.dirname(os.path.realpath(__file__)) + '/'

register(
     id="Asteroids-features-v0",
     entry_point="asteroidsenv.env:AsteroidsEnv",
     max_episode_steps=1800,
     kwargs={
          "obs_type": "features"
     }
)

register(
     id="Asteroids-pixels-v0",
     entry_point="asteroidsenv.env:AsteroidsEnv",
     max_episode_steps=1800,
     kwargs={
          "obs_type": "pixels"
     }
)

register(
     id="Asteroids-normalized-v0",
     entry_point="asteroidsenv.env:AsteroidsEnv",
     max_episode_steps=1800,
     kwargs={
          "obs_type": "pixels",
          "normalize_images": True
     }
)
