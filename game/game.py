import os
import json
import sys

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
        self.map = None
        self.rules = None
        self.players = None

        metadata = self.load_map(map_name)
        print(metadata)

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

        continents = []
        territories = []

        for name, t_data in map_metadata["territories"].items():
            territory = Territory()
            territories.append(territory)

        for name, c_data in map_metadata["continents"].items():
            continent = Continent()
            continents.append(continent)

        game_map = Map()
        return map_metadata

    def create(self, players, map, rules):
        """
        Initialize game variables
        """
        pass

    def play(self):
        """
        Start game loop
        """
        pass
