class Territory:
    def __init__(self, name, adjacent_territories) -> None:
        self.name = name
        self.adjacent_territories = adjacent_territories
        self.troops = 0
        self.occupying_player_id = None

    def update_troops(self, new_troops):
        pass

    def update_controlling_player(self, id):
        pass
