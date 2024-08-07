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
        num_continents = len(game.game_map.continents)
        max_troops = 10e4
        num_players = game.player_nb

        self.observation_space = spaces.Dict(
            {
                "territory_ids": spaces.MultiDiscrete(
                    [num_territories for _ in range(num_territories)]
                ),  # Vector (n,) for territory id
                "num_troops": spaces.MultiDiscrete(
                    [max_troops for _ in range(num_territories)]
                ),  # Vector (n,) for number of troops
                "player_ids_territory": spaces.MultiDiscrete(
                    [num_players for _ in range(num_territories)]
                ),  # Vector (n,) for the assigned player id
                "continent_ids": spaces.MultiDiscrete(
                    [num_continents for _ in range(num_continents)]
                ),  # Vector (j,) for j continents
                "player_ids_continent": spaces.MultiDiscrete(
                    [num_players for _ in range(num_continents)]
                ),  # Vector(p,) for p players controlling each continent
                "player": spaces.Discrete(num_players),  # Scalar - who is the player
                "attacking_territory": spaces.Discrete(
                    num_territories
                ),  # Scalar - which territory are we attacking from
                "connections": spaces.MultiBinary(
                    num_territories * num_territories
                ),  # Flattened adjacency matrix
            }
        )

        # We can only chose which territory to attack
        self.action_space = spaces.Discrete(len(self.game.game_map.territories))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def _get_obs(self):
        """
        Compute the observation state
        """

        territory_ids = []
        for t in self.game.game_map.territories:
            territory_ids.append(t.id_)
        num_troops = []


if __name__ == "__main__":
    p1 = Player_Random("p1")
    p2 = Player_Random("p2")
    game = Game("test_map_v0", [p1, p2])
    env = RiskEnv_Choice_is_attack_territory(game, render_mode=None)
