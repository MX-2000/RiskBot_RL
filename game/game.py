class Game:
    def __init__(self, player_nb, map_name) -> None:
        self.player_nb = player_nb
        self.map_name = map_name
        self.deck = None
        self.map = None
        self.rules = None
        self.players = None

    def render(self):
        """
        Render game state on screen
        """
        pass

    def load(self):
        """
        loads the map data based on the name
        """
        pass

    def create(self, players, map, rules):
        """
        Initialize game variables
        """
        pass

    def play(self):
        """
        Start game loop
        """
        pass
