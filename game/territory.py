class Territory:
    def __init__(self, name, id_, adjacent_territories_names: list[str]) -> None:
        self.name = name
        self.id_ = id_
        self.adjacent_territories_names = adjacent_territories_names
        self.troops = 0
        self.occupying_player_name = None

    def set_troops(self, num_troops):
        self.troops = num_troops
        return self.troops

    def add_troops(self, num_troops):
        self.troops += num_troops
        return self.troops

    def remove_troops(self, num_troops):
        self.troops -= num_troops
        return self.troops

    def assign_to_player(self, name):
        self.occupying_player_name = name
