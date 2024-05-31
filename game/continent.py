class Continent:
    def __init__(self, name, territories_name: list[str], troops_reward: int) -> None:
        self.name = name
        self.territories = territories_name
        self.troops_rewards = troops_reward
