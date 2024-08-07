import time
import os
import json
import random

from loguru import logger

from game.player import Player
from game.map import Map
from game.territory import Territory
from game.continent import Continent
from game.utils import wait_for_cmd_action
from game.dice_rolls import roll_dices, roll_dices_sanity_checks

PAUSE_BTW_ACTIONS = 2


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
        self._set_players_id()
        self.map_name = map_name
        self.deck = None
        self.fixed = fixed
        self.true_random = true_random
        self.turn_number = 1
        self.game_phase = None
        self.active_player = None

        # Usefull to construct observation space
        self.attacking_territory = None

        self.game_map = self.load_map(map_name)

    def reset(self):
        """
        Called by the environment
        """
        self.turn_number = 1
        self.game_phase = None
        self.active_player = None
        self.attacking_territory = None
        self.load_map(self.map_name)
        for p in self.players:
            p.reset()

    def _set_players_id(self):
        for i, p in enumerate(self.players):
            p.id_ = i

    def render(self):
        """
        Render game state on screen
        """
        print(self.map_repr)
        print(f"\nTurn: {self.turn_number}\nPhase:{self.game_phase}\n")
        for continent in self.game_map.continents:
            for t in continent.territories:
                # t = self.game_map.get_territory_from_name(t_name)
                print(f"{t.name} - O: {t.occupying_player_name} - Troops: {t.troops}")
        print("--------------------------")
        for player in self.players:
            print(
                f"{player.name} - Territories: {len(player.controlled_territories)} - Troops: {player.get_total_troops()}"
            )
        print("\n**************************************\n\n")
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

        # for ids
        i = 0

        for name, t_data in map_metadata["territories"].items():
            territory = Territory(name, i, t_data["adjacent_territories_ids"])
            territories.append(territory)
            i += 1

        i = 0

        game_map = Map(map_name, territories, continents)

        for name, c_data in map_metadata["continents"].items():
            c_territories = [
                game_map.get_territory_from_name(t) for t in c_data["territories"]
            ]

            continent = Continent(
                name, i, c_territories, troops_reward=c_data["troops_reward"]
            )
            continents.append(continent)
            i += 1

        game_map.update_continents(continents)

        self.map_repr = map_metadata["repr"]
        return game_map

    def draft_phase(self, player: Player):
        """
        Go through the drafting phase for a player
            1. Cards sets
            2. Deploy troops on territories
        """
        self.game_phase = "DRAFT"

        # TODO CARD system

        troops_to_deploy = self.get_deployment_troops(player)

        while troops_to_deploy > 0:
            # Doing random for now. Need to plug in player methods.
            deploying = player.draft_choose_troops_to_deploy(troops_to_deploy)
            territory = player.draft_choose_territory_to_deploy()
            territory.add_troops(deploying)
            troops_to_deploy -= deploying
            print(f"{player.name} deployed {deploying} troops in {territory.name}")
            time.sleep(PAUSE_BTW_ACTIONS)

    def get_deployment_troops(self, player: Player, card_troops=0):
        """
        Computes the number of troops available for deployment at the start of a player's turn. Sum of:
            1. min(Controlles territories // 3,3)
            2. cards sets
            3. Continents
        """

        territory_count = max(3, len(player.controlled_territories) // 3)
        continent_count = 0
        for continent in self.game_map.continents:
            if continent.is_controlled_by(player):
                continent_count += continent.troops_rewards
        result = card_troops + territory_count + continent_count
        logger.debug(
            f"{player.name} got {result} troops to deploy. {card_troops} from cards. {territory_count} from territories. {continent_count} from continents."
        )
        return result

    def attack_phase(self, player: Player):
        """
        For bot so far: choose randomly 1 territory to attack another
        The sanity checks are out of the random choice, for later implementation
        """
        self.game_phase = "ATTACK"

        # TODO
        if not self.has_valid_attack(player):
            print(f"You do not have any valid attack")
            return

        time_remaining = 100  # TODO: implement time function at some point
        while time_remaining > 0 and len(self.get_remaining_players()) > 1:
            if not self.has_valid_attack(player):
                break
            if not player.attack_wants_attack():
                break

            attacker = player.attack_choose_attack_territory()
            self.attacking_territory = attacker
            target_name = player.attack_choose_target_territory(attacker)
            target = self.game_map.get_territory_from_name(target_name)
            attack_dice_nb, blitz = player.attack_choose_attack_dices(attacker.troops)

            # Sanity checks
            is_valid = roll_dices_sanity_checks(
                player, attacker, target, attack_dice_nb
            )
            logger.debug(
                f"{player.name} trying to attack from {attacker.name} to {target.name} with {attack_dice_nb} troops. Blitz? {blitz}"
            )
            time.sleep(PAUSE_BTW_ACTIONS)
            if not is_valid:
                break

            defender_remaining = target.troops

            def attack_once(player, attacker, target, attack_dice_nb, true_random):
                logger.debug(
                    f"{player.name} Attacking from {attacker.name} to {target.name} with {attack_dice_nb} dices."
                )
                attacker_loss, defender_loss = roll_dices(
                    player, attacker, target, attack_dice_nb, true_random
                )
                logger.debug(
                    f"Attacker lost {attacker_loss}, Defender lost {defender_loss}"
                )
                return attacker_loss, defender_loss

            if blitz:
                while defender_remaining > 0 and attack_dice_nb > 0:
                    if not roll_dices_sanity_checks(
                        player, attacker, target, attack_dice_nb
                    ):
                        attack_dice_nb -= 1
                        continue
                    attacker_loss, defender_loss = attack_once(
                        player, attacker, target, attack_dice_nb, self.true_random
                    )
                    attack_remaining = attacker.remove_troops(attacker_loss)
                    defender_remaining = target.remove_troops(defender_loss)
                    logger.debug(
                        f"Remaining: A: {attack_remaining}, D: {defender_remaining}"
                    )
                    time.sleep(PAUSE_BTW_ACTIONS)

            else:
                attacker_loss, defender_loss = attack_once(
                    player, attacker, target, attack_dice_nb, self.true_random
                )
                attack_remaining = attacker.remove_troops(attacker_loss)
                defender_remaining = target.remove_troops(defender_loss)
                logger.debug(
                    f"Remaining: A: {attack_remaining}, D: {defender_remaining}"
                )
                time.sleep(PAUSE_BTW_ACTIONS)

            if defender_remaining == 0:
                logger.debug(
                    f"Territory got conquered, transferring troops and ownership"
                )
                # Update ownership
                target_player = self.get_player_by_name(target.occupying_player_name)
                target_player.remove_territory(target)
                player.assign_territory(target)

                # Move attaker troops
                # We move a minimum of (remaining_troops -1, attack_dice_nb)
                min_to_move = min(attack_dice_nb, attack_remaining - 1)
                max_to_move = attack_remaining - 1

                # For now we move the maximum we can
                mooving = max_to_move
                attacker.remove_troops(mooving)
                target.add_troops(mooving)

                # If we killed the target
                if len(target_player.controlled_territories) == 0:
                    target_player.is_dead = True

                    # TODO transfer cards

    def get_player_by_name(self, player_name):
        result = [p for p in self.players if p.name == player_name]
        assert (
            len(result) == 1
        ), f"Can't get {player_name}. Players: {[p.name for p in self.players]}"
        return result[0]

    def has_valid_attack(self, player: Player):
        """
        True if there is at least 1 territory with 2 troops or more adjacent to another player's territory
        """
        # Territories with more than 1 troop:
        potential_attack_t = [t for t in player.controlled_territories if t.troops > 1]
        if len(potential_attack_t) == 0:
            return False

        # If any has an adjacent territory that isn't controlled by player, then we have a valid attack possible
        for t in potential_attack_t:
            adjacent_territories_names = t.adjacent_territories_ids
            if any(
                [
                    adj_terr_name
                    not in [p_t.name for p_t in player.controlled_territories]
                    for adj_terr_name in adjacent_territories_names
                ]
            ):
                return True
        return False

    def reinforce_phase(self, player):
        self.game_phase = "FORTIFY"

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
                self.active_player = player

                if player.is_dead:
                    continue

                wait_for_cmd_action()
                self.draft_phase(player)
                self.render()
                wait_for_cmd_action()
                self.attack_phase(player)

                self.attacking_territory = None

                self.render()
                # self.reinforce_phase(player)
                # time.sleep(PAUSE_BTW_ACTIONS)
                # self.card_phase(player)
                # time.sleep(PAUSE_BTW_ACTIONS)
                # self.render()
                # time.sleep(PAUSE_BTW_ACTIONS)

            remaining_players = [
                player for player in self.players if not player.is_dead
            ]
            self.turn_number += 1

        print(f"Player: {remaining_players[0].name} Won!!")

    def get_remaining_players(self):
        return [player for player in self.players if not player.is_dead]

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
