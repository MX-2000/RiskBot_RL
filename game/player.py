from game.territory import Territory


class Player:
    def __init__(self, name, is_bot) -> None:
        self.name = name
        self.is_bot = is_bot
        self.tot_troops = 0
        self.controlled_territories = []
        self.cards = None

    def assign_territory(self, territory: Territory):
        """
        Puts the territory under player's control
        """
        self.controlled_territories.append(territory)
        territory.assign_to_player(self.name)
