from loguru import logger

from game.dice_rolls import roll_dices


def wait_for_cmd_action():
    input("Press Enter to continue...")


def attack_once(player, attacker, target, attack_dice_nb, true_random):
    """
    Compute the lost troops on a dice roll

    Args:
        player (_type_): _description_
        attacker (_type_): _description_
        target (_type_): _description_
        attack_dice_nb (_type_): _description_
        true_random (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.debug(
        f"{player.name} Attacking from {attacker.name} to {target.name} with {attack_dice_nb} dices."
    )
    attacker_loss, defender_loss = roll_dices(
        player, attacker, target, attack_dice_nb, true_random, player.np_random
    )
    logger.debug(f"Attacker lost {attacker_loss}, Defender lost {defender_loss}")
    return attacker_loss, defender_loss
