from game.game import Game
from game.player import Player_Random, Player_RL
import gymnasium as gym

p1 = Player_Random("p1")
p2 = Player_RL("p2")
game = Game("test_map_v0", [p1, p2])
# game.init_players()

env = gym.make("game/RiskEnv-V0", game=game, agent_player=p2, render_mode="human")
env.reset()
