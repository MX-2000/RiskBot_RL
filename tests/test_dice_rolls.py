import random

import pytest

from game.dice_rolls import *
from game.territory import Territory
from game.player import Player


def test_sanity_checks():
    attack_player = Player("p1", True)
    attack_terr = Territory("t1", ["t2"])
    attack_terr.set_troops(3)
    attack_terr.occupying_player_name = attack_player.name
    target = Territory("t2", ["t1"])
    target.set_troops(2)
    attack_dice = 2
    # Ok
    assert (
        roll_dices_sanity_checks(attack_player, attack_terr, target, attack_dice)
        == True
    )
    attack_dice = 3
    # Too many attack dices
    assert (
        roll_dices_sanity_checks(attack_player, attack_terr, target, attack_dice)
        == False
    )

    attack_dice = 2
    attack_terr.occupying_player_name = "p2"
    # Not owning attacking territory
    assert (
        roll_dices_sanity_checks(attack_player, attack_terr, target, attack_dice)
        == False
    )

    # Owning target
    attack_terr.occupying_player_name = "p1"
    target.occupying_player_name = "p1"
    assert (
        roll_dices_sanity_checks(attack_player, attack_terr, target, attack_dice)
        == False
    )

    # Target not connected
    target.occupying_player_name = "p2"
    attack_terr.adjacent_territories_ids = ["other"]
    assert (
        roll_dices_sanity_checks(attack_player, attack_terr, target, attack_dice)
        == False
    )


def test_rolling_dices():
    attack_player = Player("p1", True)
    attack_terr = Territory("t1", ["t2"])
    attack_terr.set_troops(5)
    attack_terr.occupying_player_name = attack_player.name
    target = Territory("t2", ["t1"])
    target.set_troops(2)
    attack_dice = 2

    random.seed(1)
    # Expected sequence for random.randint(1,6):
    # [2,5,1,3,1,4,4,4,6,4,2,1,4,1,4]

    # Attack 2,5
    # Def 1, 3
    attack_loss, def_loss = roll_dices(attack_player, attack_terr, target, attack_dice)
    assert attack_loss == 0
    assert def_loss == 2

    # Attack 1, 4, 4
    # Def 4,6
    attack_dice = 3
    attack_loss, def_loss = roll_dices(attack_player, attack_terr, target, attack_dice)
    assert attack_loss == 2
    assert def_loss == 0

    # Attack 4,2,1
    # Def 4
    target.set_troops(1)
    attack_loss, def_loss = roll_dices(attack_player, attack_terr, target, attack_dice)
    assert attack_loss == 1
    assert def_loss == 0

    random.seed(2)
    # Expected sequence:
    # [1,1,1,3,2,6,6,3,3,5,2]
    for i in range(7):
        # Consuming some to get where we want
        random.randint(1, 6)

    # Attack 3,3
    # Def 5,2
    target.set_troops(5)
    attack_dice = 2
    attack_loss, def_loss = roll_dices(attack_player, attack_terr, target, attack_dice)
    assert attack_loss == 1
    assert def_loss == 1
