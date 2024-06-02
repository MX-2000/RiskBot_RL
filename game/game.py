import time
import os
import json
import random

from game.player import Player
from game.map import Map
from game.territory import Territory
from game.continent import Continent

PAUSE_BTW_ACTIONS = 5


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
        print(self.map_repr)
        for continent in self.game_map.continents:
            for t_name in continent.territories:
                t = self.game_map.get_territory_from_name(t_name)
                print(f"{t.name} - O: {t.occupying_player_name} - Troops: {t.troops}")
        print("--------------------------")
        for player in self.players:
            print(
                f"{player.name} - Territories: {len(player.controlled_territories)} - Troops: {player.get_total_troops()}"
            )
        return

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

        game_map = Map(map_name, territories, continents)

        for name, c_data in map_metadata["continents"].items():
            c_territories = [
                game_map.get_territory_from_name(t) for t in c_data["territories"]
            ]

            continent = Continent(
                name, c_data["territories"], troops_reward=c_data["troops_reward"]
            )
            continents.append(continent)

        game_map.update_continents(continents)

        self.map_repr = map_metadata["repr"]
        return game_map

    def draft_phase(self, player: Player):
        """
        Go through the drafting phase for a player
            1. Cards sets
            2. Deploy troops on territories
        """

        # TODO CARD system

        troops_to_deploy = self.get_deployment_troops(player)

        while troops_to_deploy > 0:

            if player.is_bot:
                # Doing random for now
                deploying = random.randint(1, troops_to_deploy)
                territory = random.choice(player.controlled_territories)
                territory.add_troops(deploying)
                troops_to_deploy -= deploying
                print(f"{player.name} deployed {deploying} troops in {territory.name}")
                time.sleep(PAUSE_BTW_ACTIONS)
            else:
                # TODO prompt
                pass

    def get_deployment_troops(self, player: Player, set=0):
        """
        Computes the number of troops available for deployment at the start of a player's turn. Sum of:
            1. min(Controlles territories // 3,3)
            2. cards sets
            3. Continents
        """
        result = set
        result += min(3, len(player.controlled_territories) // 3)
        # TODO continents holds
        return result

    def attack_phase(self, player):
        """"""
        pass

    def reinforce_phase(self, player):
        pass

    def card_phase(self, player):
        pass

    def play(self):
        """
        Start game loop
        """
        self.init_players()
        self.render()

        remaining_players = self.players

        while len(remaining_players) > 1:

            for player in remaining_players:

                if player.is_dead:
                    continue

                self.draft_phase(player)
                self.render()
                time.sleep(PAUSE_BTW_ACTIONS)
                # self.attack_phase(player)
                # time.sleep(PAUSE_BTW_ACTIONS)
                # self.reinforce_phase(player)
                # time.sleep(PAUSE_BTW_ACTIONS)
                # self.card_phase(player)
                # time.sleep(PAUSE_BTW_ACTIONS)
                # self.render()
                # time.sleep(PAUSE_BTW_ACTIONS)

            remaining_players = [
                player for player in self.players if not player.is_dead
            ]

        print(f"Player: {remaining_players[0].name} Won!!")

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

        # Each player gets their territories
        unassigned_territories = self.game_map.territories
        i = 0
        while len(unassigned_territories) > 1:
            unassigned_territories = self.game_map.get_unassigned_territories()
            t = random.choice(unassigned_territories)
            self.players[i].assign_territory(t)

            # Assign 1 troop
            t.set_troops(1)

            # We loop over the players until it's over
            i += 1
            if i == len(self.players):
                i = 0

        # Assign remaining troops randomly
        for player in self.players:
            p_remaining_troops = starting_troops - len(
                player.controlled_territories
            )  # We already put 1 troop on each
            while p_remaining_troops > 0:
                t = random.choice(player.controlled_territories)
                t.add_troops(1)
                p_remaining_troops -= 1
