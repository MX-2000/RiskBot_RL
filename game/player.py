from game.territory import Territory


class Player:
    def __init__(self, name, is_bot) -> None:
        self.name = name
        self.is_bot = is_bot
        self.controlled_territories: list[Territory] = []
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

    def draft_choose_troops_to_deploy(self):
        pass

    def draft_choose_territory_to_deploy(self):
        pass

    def attack_choose_attack_territory(self):
        pass

    def attack_choose_target_territory(self):
        pass

    def attack_choose_attack_dices(self):
        pass

    def reinforce_choose_from(self):
        pass

    def reinforce_choose_to(self):
        pass

    def reinforce_choose_troops_nb(self):
        pass
