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

    def get_total_troops(self):
        result = 0
        for t in self.controlled_territories:
            result += t.troops
        return result
