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
                "continent_territories": spaces.MultiBinary(
                    num_continents * num_territories
                ),  # Vector(c,t) for territories inside each continent, c continents x t territories
                "player": spaces.Discrete(num_players),  # Scalar - who is the player
                "attacking_territory": spaces.Discrete(
                    num_territories
                ),  # Scalar - which territory are we attacking from
                "connexions": spaces.MultiBinary(
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
        num_troops = []
        player_ids_territory = []
        connexions = []
        for t in self.game.game_map.territories:
            territory_ids.append(t.id_)
            num_troops.append(t.troops)
            player_ids_territory.append(
                self.game.get_player_by_name(t.occupying_player_name).id_
            )
            t_connexions = [0] * len(self.game.game_map.territories)
            for t_name in t.adjacent_territories_ids:
                t_id = self.game.game_map.get_territory_from_name(t_name).id_
                t_connexions[t_id] = 1
            connexions.extend(t_connexions)

        continent_ids = []
        continent_territories = []  # Binaries of length num_territories
        for c in self.game.game_map.continents:
            continent_ids.append(c.id_)
            c_territories = [0] * len(game.game_map.territories)
            c_terr_ids = [t.id_ for t in c.territories]
            for idx in c_terr_ids:
                c_territories[idx] = 1
            continent_territories.extend(c_territories)

        player = self.game.active_player.id_

        attacking_territory = self.game.attacking_territory

        return {
            "territory_ids": territory_ids,
            "num_troops": num_troops,
            "player_ids_territory": player_ids_territory,
            "continent_ids": continent_ids,
            "continent_territories": continent_territories,
            "player": player,
            "attacking_territory": attacking_territory,
            "connexions": connexions,
        }


if __name__ == "__main__":
    p1 = Player_Random("p1")
    p2 = Player_Random("p2")
    game = Game("test_map_v0", [p1, p2])
    game.init_players()
    game.active_player = p1
    env = RiskEnv_Choice_is_attack_territory(game, render_mode=None)
    print(env._get_obs())
