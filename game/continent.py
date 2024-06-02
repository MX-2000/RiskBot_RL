from game.player import Player


class Continent:
    def __init__(self, name, territories_name: list[str], troops_reward: int) -> None:
        self.name = name
        self.territories = territories_name
        self.troops_rewards = troops_reward

    def is_controlled_by(self, player: Player):
        # return all(c.occupying_player_name == player.name for c in self.territories)
        return False  # TODO
