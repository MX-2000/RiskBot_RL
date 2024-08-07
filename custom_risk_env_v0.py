import numpy as np

import gymnasium as gym
from gymnasium import spaces

from game.game import Game


class RiskEnv_Choice_is_attack_territory(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 0}

    def __init__(self, game: Game, render_mode=None) -> None:
        self.game = game

        self.observation_space = spaces.Dict()

        # We can only chose which territory to attack
        self.action_space = spaces.Discrete(len(self.game.game_map.territories))
