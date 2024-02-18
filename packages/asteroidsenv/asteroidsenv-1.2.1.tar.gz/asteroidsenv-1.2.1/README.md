# Atari Asteroids
An implementation of the Atari Classic Asteroids as a `gymnasium` environment.
## Installation
1. Clone the repository
2. Use pip to install as python package (`pip install <Path of setup.py>`)
3. Copy the Resource folder into the working directory
## Dependencies
The environment needs the following packages to run
1. `gymnasium`
2. `numpy`
3. `pygame`
## Environment Arguments
The environment can be customized using the following kwargs:
1. render_mode: possible values are ["human", "agent", "rgb_array", "debug"], these are all explained in the Rendering Modes section
2. obs_type: either "pixels" or "features", specifies the observation type given to the agent
3. num_rays: a positive integer, specifying the number of rays the agent will use to see in "features" mode.
## Feature Space
The agent get the following values as features:
1. "agent_pos": Center position of the hitbox of the agent
2. "forward_normal": Normalized vector in the direction the agent is facing
3. "direction": Normalized vector in the direction the agent is traveling
4. "velocity": Scalar velocity of the agent
5. "angular_velocity": Scalar angular velocity of the agent
6. "hit_distance": Distance to the asteroid hit
7. "ray_direction<num>": Normalized direction vector of the Asteroid the ray intersected (not implemented yet)
The Shape of the vector depends on the number of rays the agent uses to see, but can be calculated via (8 + 5 * <num_rays>)
## Pixel Space
A 64 by 64 pixel image, the Observation Space has the Shape (64, 64, 3).
## Reward Function
The agent gets a positiv reward of 1.0 if he destroys an asteroid.
The agent gets a negativ reward of -10.0 if he gets hit by an asteroid.
## Rendering Modes
The Environment supports 4 different rendering mode:
### 1. "human"
The normal rendering mode, rendering the environment like a human would see the game.
![human](https://github.com/TU-Dortmund-ADRL-WiSe-2023-24/laurenzlevi/assets/72398071/5456acf3-0914-40e4-bafe-cd1c6f8a7e15)
### 2. "debug"
Same as human, but with the following debug info visualized:
1. the hitbox of the player as orange box
2. the hitbox of the asteroids as orange circle
3. the rays used by the agent to "see" as blue lines
4. the intersection points of the rays with the asteroids as red dots
5. the players velocity, angular velocity and position as text in the topleft corner
![human](https://github.com/TU-Dortmund-ADRL-WiSe-2023-24/laurenzlevi/assets/72398071/ebbae211-b97b-481b-868b-4622586c3cbe)
### 3. "agent"
Visualizes the environment in a way the agent would "see" by rendering...
1. ...the rays (in blue) it uses to "see"
2. ...the forward facing direction of the agent (in red), this is the same as one of the eight rays
3. ...the moving velocity and direction of the player (as green ray)
4. ...the turning velocity and direction of the player (as orange ray)
5. ...the intersection points of the rays with asteroids (in red)
6. ...the direction vector of the asteroids (in red)
7. ...the velocity, angular velocity and position of the player (as text)
![agent](https://github.com/TU-Dortmund-ADRL-WiSe-2023-24/laurenzlevi/assets/72398071/3cd3d5ca-4e6f-4ed9-9098-099262c280b9)
### 4. "rgb_array"
