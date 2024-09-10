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

Run the dqn.py file to train using dqn. 
Use the generated .keras files to test the trained agent

