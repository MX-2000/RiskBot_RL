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
        return [t for t in self.territories if t.occupying_player_name is None]

    def get_territory_from_name(self, name):
        """
        Returns the territory object
        """
        result = [t for t in self.territories if t.name == name]
        assert len(result) == 1
        return result[0]

    def get_territory_from_id(self, id_):
        result = [t for t in self.territories if t.id_ == id_]
        assert len(result) == 1
        return result[0]

    def get_continent_from_id(self, id_):
        result = [c for c in self.continents if c.id_ == id_]
        assert len(result) == 1
        return result[0]

    def update_continents(self, continents: list[Continent]):
        """
        Used at load time for convenience, after init
        """
        self.continents = continents
