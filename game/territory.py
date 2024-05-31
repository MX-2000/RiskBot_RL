class Territory:
    def __init__(self) -> None:
        self.name = ""
        self.troops = 0
        self.occupying_player_id = None
        self.adjacent_territories = None

    def update_troops(self, new_troops):
        pass

    def update_controlling_player(self, id):
        pass
