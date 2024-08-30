import numpy as np

from game.game import Game
from game.player import Player_Random, Player_RL

import gymnasium as gym
from gymnasium.utils.env_checker import check_env

p1 = Player_Random("p1")
p2 = Player_RL("p2")
game = Game("test_map_v0", [p1, p2])

env = gym.make("game/RiskEnv-V0", game=game, agent_player=p2, render_mode="human")

print("Check environment begin")
check_env(env.unwrapped)
print("Check environment end")

# observation, info = env.reset()
# terminated = False
# while not terminated:

#     # Choosing a valid territory to attack
#     possible_actions = env.unwrapped.get_masked_action_space()
#     print(possible_actions)
#     action = np.random.choice(possible_actions)

#     # action = env.action_space.sample()

#     observation, reward, terminated, truncated, info = env.step(action)

# print(reward)
# env.close()
