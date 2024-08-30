# Install 

* Clone this repo
* Run pip install -r requirements.txt

Run python main_game_v0.py -h for help on how to start a game

# Start a game
## With Random players
```
python .\main_game_v0.py -m test_map_v0 -p p1:bot -p p2:bot
```

This will start a game with automated player acting randomly

# Testing the custom environment

Currently this runs the gymnasium custom environment with 1 random player and 1 RL player, which doesn't yet uses any RL algorithm. The game plays without pausing, while logging events.

