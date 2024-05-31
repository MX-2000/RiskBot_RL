class Territory:
    def __init__(self, name, adjacent_territories_ids: list[str]) -> None:
        self.name = name
        self.adjacent_territories_ids = adjacent_territories_ids
        self.troops = 0
        self.occupying_player_name = None

    def update_troops(self, new_troops):
        pass

    def assign_to_player(self, name):
        self.occupying_player_name = name
