from game.game import Game
from game.player import Player_Random, Player_RL

import gymnasium as gym
from gymnasium.utils import RecordConstructorArgs
from gymnasium.utils.env_checker import check_env


class SafeActionWrapper(gym.Wrapper, RecordConstructorArgs):
    def __init__(self, env):
        super(SafeActionWrapper, self).__init__(env)

    def step(self, action):
        # Here, you can implement a mechanism to modify invalid actions
        # For example, you could pick a valid action if the given one is invalid
        if not self.is_valid_action(action):
            action = self.get_valid_action(action)
        return self.env.step(action)

    def is_valid_action(self, action):
        # Implement your logic to check if an action is valid
        return action in self.env.get_masked_action_space()

    def get_valid_action(self, action):
        # Implement your logic to return a valid action if the given one is invalid
        return self.env.get_masked_action_space()[0]


p1 = Player_Random("p1")
p2 = Player_RL("p2")
game = Game("test_map_v0", [p1, p2])

env = gym.make("game/RiskEnv-V0", game=game, agent_player=p2, render_mode="human")
# w_env = SafeActionWrapper(env)

# print("Check environment begin")
# check_env(w_env)
# print("Check environment end")
obs, info = env.reset()
obs_fl = env.unwrapped.flatten_obs(obs)
print(obs_fl)
