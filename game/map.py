from game.territory import Territory
from game.continent import Continent


class Map:
    def __init__(
        self, name, territories: list[Territory], continents: list[Continent]
    ) -> None:
        self.name = name
        self.territories = territories
        self.continents = continents
