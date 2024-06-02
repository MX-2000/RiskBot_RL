import random

from game.player import Player
from game.territory import Territory


def roll_dices_sanity_checks(
    attack_player: Player,
    attacker_territory: Territory,
    target: Territory,
    attack_dice_nb: int,
):
    """
    Return true if the attack is valid, false otherwise
    1 sanity checks:
        . attacker is controlled by player
        . target is NOT controlled by player
        . target is connected to attacker
        . attacker has at least attack_dice_nb available & more than 1 troop
    """
    if attack_player.name != attacker_territory.occupying_player_name:
        return False
    if attack_player.name == target.occupying_player_name:
        return False
    if target.name not in attacker_territory.adjacent_territories_ids:
        return False
    if attacker_territory.troops < 2:
        return False

    return True


def roll_dices(
    attack_player: Player,
    attacker_territory: Territory,
    target: Territory,
    attack_dice_nb: int,
    true_random=True,
):
    """
    Returns tuple: [attacker_loss, defender_loss]
    """
    """
    2. Dice rolls: 
        . On assigne à chaque dès attack. un nombre aléatoire entre 1 et 6 (entre 1 et 3 dés)
        . On assigne à chaque dés def. un nombre aléatoire entre 1 et 6 (entre 1 et 2 dés)
        . Sort both dices
        . From inverse order, look at highest dice values
        . For each pair of dice, add loosing troop
        . Return loosing troops
    """
    if true_random:

        attack_loss = 0
        defender_loss = 0

        attack_dices = []
        defender_dices = []

        for i in range(attack_dice_nb):
            attack_dices.append(random.randint(1, 6))
        for i in range(min(target.troops, 2)):
            defender_dices.append(random.randint(1, 6))

        attack_dices = sorted(attack_dices, reverse=True)
        defender_dices = sorted(defender_dices, reverse=True)

        for j in range(min(len(attack_dices), len(defender_dices))):
            if attack_dices[j] > defender_dices[j]:
                defender_loss += 1
            else:
                attack_loss += 1

    return (attack_loss, defender_loss)
