import argparse
import os

from game.game import Game
from game.player import Player_Random, Player_Human, Player_RL


def parse_player(player_string):
    player_data = player_string.split(":")
    if len(player_data) == 1:
        return {"name": player_data[0], "is_bot": False}
    elif len(player_data) == 2 and player_data[1].lower() == "bot":
        return {"name": player_data[0], "is_bot": True}
    else:
        raise argparse.ArgumentTypeError(
            f"Player string must be in the format 'name' or 'name:bot'."
        )


def get_available_map_names():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game", "maps")
    print(path)
    try:
        files = os.listdir(path)
        json_files = [f[:-5] for f in files if f.endswith(".json")]
        return json_files
    except Exception as e:
        print(f"Err: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="A CLI Risk Game")

    parser.add_argument(
        "-gm",
        "--get_maps",
        action="store_true",
        help="Return available maps.",
    )

    parser.add_argument("-m", "--map", type=str, help="Specify the map name")

    parser.add_argument(
        "-p",
        "--player",
        type=parse_player,
        action="append",
        help="Player name in the format 'player' or 'player:bot' if a bot.",
    )

    args = parser.parse_args()

    if args.get_maps:
        print(get_available_map_names())
        return

    map_name = args.map
    players_args = args.player

    if len(players_args) < 2:
        print("Error: At least two players must be specified.")
        return

    players = []
    name_set = set()
    for i, player in enumerate(players_args):
        if player["is_bot"]:
            p = Player_Random(player["name"])
        else:
            p = Player_Human(player["name"])
        players.append(p)
        name_set.add(player["name"])

    if len(players) > 6 or len(name_set) != len(players):
        print(f"Maximum 6 players and 2 players can't have same name.")
        return

    game = Game(map_name, players=players)
    game.play()


if __name__ == "__main__":
    main()
