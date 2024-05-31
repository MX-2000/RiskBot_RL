class Player:
    def __init__(self, name, is_bot) -> None:
        self.id = None
        self.name = name
        self.is_bot = is_bot
        self.tot_troops = 0
        self.controlled_territories = None
        self.cards = None
