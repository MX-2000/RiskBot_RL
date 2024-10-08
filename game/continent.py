from game.player import Player
from game.territory import Territory


class Continent:
    def __init__(
        self, name, id_, territories: list[Territory], troops_reward: int
    ) -> None:
        self.name = name
        self.id_ = id_
        self.territories = territories
        self.troops_rewards = troops_reward

    def is_controlled_by(self, player: Player):
        return all(t.occupying_player_name == player.name for t in self.territories)
