from game.territory import Territory
from game.continent import Continent


class Map:
    def __init__(
        self, name, territories: list[Territory], continents: list[Continent]
    ) -> None:
        self.name = name
        self.territories = territories
        self.continents = continents

    def get_unassigned_territories(self):
        """
        return the list of unassigned territories.
        Used in game setup phase.
        """
        return [t for t in self.territories if t.occupying_player_id is None]
