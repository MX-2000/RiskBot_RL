import numpy as np

import gymnasium as gym
from gymnasium import spaces

from game.game import Game
from game.player import Player, Player_Random


class RiskEnv_Choice_is_attack_territory(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 0}

    def __init__(self, game: Game, render_mode=None) -> None:
        self.game = game

        num_territories = len(game.game_map.territories)
        max_troops = 10e4
        num_players = game.player_nb

        self.observation_space = spaces.Dict(
            {
                "territory_ids": spaces.MultiDiscrete(
                    [num_territories for _ in range(num_territories)]
                ),  # [1,....n] which can take values from 0 to n
                "num_troops": spaces.MultiDiscrete(
                    [max_troops for _ in range(num_territories)]
                ),  # Vector (n,) for number of troops
                "player_ids": spaces.MultiDiscrete(
                    [num_players for _ in range(num_territories)]
                ),  # Vector (n,) for the assigned player id
                "connections": spaces.MultiBinary(
                    num_territories * num_territories
                ),  # Flattened adjacency matrix
            }
        )

        # We can only chose which territory to attack
        self.action_space = spaces.Discrete(len(self.game.game_map.territories))


if __name__ == "__main__":
    p1 = Player_Random("p1")
    p2 = Player_Random("p2")
    game = Game("test_map_v0", [p1, p2])
    env = RiskEnv_Choice_is_attack_territory(game, render_mode=None)
