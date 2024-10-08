from loguru import logger

import numpy as np

from game.territory import Territory


class Player:
    def __init__(self, name) -> None:
        self.name = name
        self.id_ = None
        self.controlled_territories: list[Territory] = []
        self.cards = None
        self.is_dead = False

    def reset(self):
        self.controlled_territories = []
        self.cards = None
        self.is_dead = False

    def assign_territory(self, territory: Territory):
        """
        Puts the territory under player's control
        """
        self.controlled_territories.append(territory)
        territory.assign_to_player(self.name)

    def remove_territory(self, territory: Territory):
        og_terr_nb = len(self.controlled_territories)
        self.controlled_territories = [
            t for t in self.controlled_territories if t != territory
        ]
        assert (
            og_terr_nb == len(self.controlled_territories) + 1
        ), f"Seems like {territory.name} wasn't under {self.name} control."
        territory.occupying_player_name = None

    def get_total_troops(self):
        result = 0
        for t in self.controlled_territories:
            result += t.troops
        return result

    def attack_wants_attack(self):
        raise NotImplementedError

    def draft_choose_troops_to_deploy(self, troops_to_deploy):
        raise NotImplementedError

    def draft_choose_territory_to_deploy(self) -> Territory:
        raise NotImplementedError

    def attack_choose_attack_territory(self) -> Territory:
        raise NotImplementedError

    def attack_choose_target_territory(self, attack_territory: Territory) -> str:
        raise NotImplementedError

    def attack_choose_attack_dices(self, attacker_troops: int):
        """
        Returns tuple with number of troops to attack, and boolean (dice_number, blitz)
        blitz is true if wants to roll all troops at once (and puts the dice nb to max)
        """
        raise NotImplementedError

    def attack_choose_blitz(self) -> bool:
        raise NotImplementedError

    def attack_choose_transfert_nb(self) -> bool:
        raise NotImplementedError

    def fortify_choose_from(self):
        raise NotImplementedError

    def fortify_choose_to(self):
        raise NotImplementedError

    def fortify_choose_troops_nb(self):
        raise NotImplementedError


class Player_Random(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def attack_wants_attack(self):
        return np.random.choice([True, False])

    def draft_choose_troops_to_deploy(self, troops_to_deploy):
        if troops_to_deploy == 1:
            return 1
        return np.random.randint(1, troops_to_deploy)

    def draft_choose_territory_to_deploy(self) -> Territory:
        return np.random.choice(self.controlled_territories)

    def attack_choose_attack_territory(self):

        t_with_more_than_one_troop = [
            t for t in self.controlled_territories if t.troops > 1
        ]

        # Getting player controlled territories names
        player_t = [t.name for t in self.controlled_territories]
        # Filtering on territories having at least one adjacent territory that isn't owned by us
        t_with_valid_attack = list(
            filter(
                lambda x: any(
                    [t_n not in player_t for t_n in x.adjacent_territories_names]
                ),
                t_with_more_than_one_troop,
            )
        )
        if len(t_with_valid_attack) == 0:
            return

        return np.random.choice(t_with_valid_attack)

    def attack_choose_target_territory(self, attack_territory: Territory) -> str:
        """
        Return territory name
        """
        adjacent_territories = attack_territory.adjacent_territories_names
        # Target randomly an adjacent territory that isn't our own
        try:
            target = np.random.choice(
                [
                    t
                    for t in adjacent_territories
                    if t not in [p_t.name for p_t in self.controlled_territories]
                ]
            )
            return target
        except ValueError:
            # all adjacent territories are player's
            return []

    def attack_choose_attack_dices(self, attacker_troops):
        return min(np.random.randint(1, 4), attacker_troops - 1), np.random.choice(
            [True, False]
        )


class Player_Human(Player):
    def __init__(self, name) -> None:
        super().__init__(name)


class Player_RL(Player):
    def __init__(self, name) -> None:
        super().__init__(name)

    def attack_wants_attack(self):
        # Random player always attack as long as it can
        return True

    def draft_choose_troops_to_deploy(self, troops_to_deploy):
        if troops_to_deploy == 1:
            return 1
        return np.random.randint(1, troops_to_deploy)

    def draft_choose_territory_to_deploy(self) -> Territory:
        return np.random.choice(self.controlled_territories)

    def attack_choose_attack_territory(self):
        t_with_more_than_one_troop = [
            t for t in self.controlled_territories if t.troops > 1
        ]

        # Getting player controlled territories names
        player_t = [t.name for t in self.controlled_territories]
        # Filtering on territories having at least one adjacent territory that isn't owned by us
        t_with_valid_attack = list(
            filter(
                lambda x: any(
                    [t_n not in player_t for t_n in x.adjacent_territories_names]
                ),
                t_with_more_than_one_troop,
            )
        )
        if len(t_with_valid_attack) == 0:
            return

        return np.random.choice(t_with_valid_attack)

    def attack_choose_target_territory(self, attack_territory: Territory) -> str:
        """
        Return territory name
        """
        adjacent_territories = attack_territory.adjacent_territories_names
        # Target randomly an adjacent territory that isn't our own
        try:
            target = np.random.choice(
                [
                    t
                    for t in adjacent_territories
                    if t not in [p_t.name for p_t in self.controlled_territories]
                ]
            )
            return target
        except ValueError:
            # all adjacent territories are player's
            return []

    def attack_choose_attack_dices(self, attacker_troops):
        # RL player always blitz with maximum troops
        return min(3, attacker_troops - 1), True
