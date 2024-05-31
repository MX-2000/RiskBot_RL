import os
import json
import random

from game.player import Player
from game.map import Map
from game.territory import Territory
from game.continent import Continent


class Game:
    def __init__(
        self,
        map_name: str,
        players: list[Player],
        fixed: bool = True,
        true_random: bool = True,
    ) -> None:

        self.player_nb = len(players)
        self.players = players
        self.map_name = map_name
        self.deck = None
        self.fixed = fixed
        self.true_random = true_random

        self.game_map = self.load_map(map_name)

    def render(self):
        """
        Render game state on screen
        """
        pass

    def load_map(self, map_name):
        """
        loads the map data based on the name
        Create according classes and objects
        """
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "maps", f"{map_name}.json"
        )
        if not os.path.exists(path):
            raise ValueError(f"The map does not exist at {path}")
        with open(path, "r") as map_file:
            map_metadata = json.loads(map_file.read())

        if len(self.players) > map_metadata["max_players"]:
            raise ValueError(
                f"Maximum number of players for this map is {map_metadata['max_players']}"
            )

        continents = []
        territories = []

        for name, t_data in map_metadata["territories"].items():
            territory = Territory(name, t_data["adjacent_territories_ids"])
            territories.append(territory)

        for name, c_data in map_metadata["continents"].items():
            continent = Continent(
                name, c_data["territories"], troops_reward=c_data["troops_reward"]
            )
            continents.append(continent)

        game_map = Map(map_name, territories, continents)

        return game_map

    def create(self, players, map, rules):
        """
        Initialize game variables
        """
        pass

    def play(self):
        """
        Start game loop
        """
        self.init_players()
        pass

    def init_players(self):
        """
        Based on the map & the player number:
            - shuffle the order
            - attribute a starting troop number to each player
            - randomly assigns territories to each player with 1 troop
            - randomly assigns the remaining troops to each territory
        """
        random.shuffle(self.players)

        starting_troops = 40 - (len(self.players) - 2) * 5
        print(starting_troops)
