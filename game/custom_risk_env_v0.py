import os
import sys

import numpy as np

import gymnasium as gym
from gymnasium import spaces
from gymnasium.spaces.utils import flatten_space

from loguru import logger

logger.remove()

logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), f"env.log"),
    level="DEBUG",
    mode="w",
)
logger.add(sys.stdout, level="INFO")

from game.game import Game
from game.player import Player, Player_Random

LOSE_GAME_REWARD = -1e10
WIN_GAME_REWARD = 1e10
TERRITORY_GAIN_REWARD = 1e9


class RiskEnv_Choice_is_attack_territory(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 1}

    def __init__(self, game: Game, agent_player: Player, render_mode=None) -> None:
        self.game = game
        self.agent_player = agent_player

        num_territories = len(game.game_map.territories)
        num_continents = len(game.game_map.continents)
        max_troops = 10e4
        num_players = game.player_nb

        self.observation_space = spaces.Dict(
            {
                "num_troops": spaces.MultiDiscrete(
                    [max_troops for _ in range(num_territories)]
                ),  # Vector (n,) for number of troops
                "player_ids_territory": spaces.MultiDiscrete(
                    [num_players for _ in range(num_territories)]
                ),  # Vector (n,) for the player controlling each territory
                "continent_territories": spaces.MultiBinary(
                    num_continents * num_territories
                ),  # Vector(c,t) for territories inside each continent, c continents x t territories
                "player": spaces.Discrete(num_players),  # Scalar - who is the player
                "attacking_territory": spaces.Discrete(
                    num_territories
                ),  # Scalar - which territory are we attacking from
                "connexions": spaces.MultiBinary(
                    num_territories * num_territories
                ),  # Flattened adjacency matrix
            }
        )

        # We can only chose which territory to attack
        self.action_space = spaces.Discrete(len(self.game.game_map.territories))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def flatten_observation_space(self):
        flattened_space_shape = self._calculate_flattened_space_shape()
        return gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(flattened_space_shape,), dtype=np.float32
        )

    def _calculate_flattened_space_shape(self):
        flattened_shape = 0
        for key, space in self.observation_space.spaces.items():
            if key == "num_troops":
                flattened_shape += len(self.game.game_map.territories)
            else:
                flattened_shape += flatten_space(space).shape[0]
        return flattened_shape

    def flatten_obs(self, obs):
        # Flatten each part of the observation manually

        # This should be a (terr_nb,player_nb) shape one hot encoded to which player controls which territory
        flat_player_id_terr = np.zeros(
            shape=(len(self.game.players) * len(self.game.game_map.territories),),
            dtype=np.int8,
        )
        for i in range(len(obs["player_ids_territory"])):
            territory_idx_start = i * len(self.game.players)
            flat_player_id_terr[
                territory_idx_start + obs["player_ids_territory"][i]
            ] = 1

        flat_cont_terr = obs["continent_territories"].flatten()

        player_one_hot = np.zeros(len(self.game.players), dtype=np.int16)
        player_one_hot[obs["player"]] = 1
        flat_player = player_one_hot

        att_t_one_hot = np.zeros(len(self.game.game_map.territories), dtype=np.int16)
        att_t_one_hot[obs["attacking_territory"]] = 1
        flat_att_terr = att_t_one_hot

        flat_conn = obs["connexions"].flatten()

        # That one we keep label encoded
        flat_num_troops = obs["num_troops"]

        flattened_obs = np.concatenate(
            [
                flat_player_id_terr,
                flat_cont_terr,
                flat_player,
                flat_att_terr,
                flat_conn,
                flat_num_troops,
            ]
        )
        return flattened_obs

    def _get_obs(self):
        """
        Compute the observation state
        """

        num_troops = []
        player_ids_territory = []
        connexions = []
        for t in self.game.game_map.territories:
            num_troops.append(t.troops)
            player_ids_territory.append(
                self.game.get_player_by_name(t.occupying_player_name).id_
            )
            t_connexions = [0] * len(self.game.game_map.territories)
            for t_name in t.adjacent_territories_names:
                t_id = self.game.game_map.get_territory_from_name(t_name).id_
                t_connexions[t_id] = 1
            connexions.extend(t_connexions)

        continent_territories = []  # Binaries of length num_territories
        for c in self.game.game_map.continents:
            c_territories = [0] * len(self.game.game_map.territories)
            c_terr_ids = [t.id_ for t in c.territories]
            for idx in c_terr_ids:
                c_territories[idx] = 1
            continent_territories.extend(c_territories)

        player = self.game.active_player.id_

        attacking_territory = self.game.attacking_territory.id_

        return {
            "num_troops": np.array(num_troops),
            "player_ids_territory": np.array(player_ids_territory),
            "continent_territories": np.array(continent_territories),
            "player": player,
            "attacking_territory": attacking_territory,
            "connexions": np.array(connexions),
        }

    def _get_info(self):
        return {}

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        np.random.seed(seed=seed)

        self.game.reset()

        logger.debug(f"Player turn: {self.game.active_player.name}")

        terminated = self.play_other_player_turn()
        if terminated:
            obs = self._get_obs()
            return obs, self._get_info()

        # It's back to the agent_player's turn again
        if self.game.game_phase == "DRAFT":
            troops_to_deploy = self.game.get_deployment_troops(self.game.active_player)

            while (
                troops_to_deploy > 0
            ):  # To be replaced whenever the player will actually choose
                # Doing random for now. Need to plug in player methods.
                deploying = self.game.active_player.draft_choose_troops_to_deploy(
                    troops_to_deploy
                )
                territory = self.game.active_player.draft_choose_territory_to_deploy()
                territory.add_troops(deploying)
                troops_to_deploy -= deploying
                logger.debug(
                    f"{self.game.active_player.name} deployed {deploying} troops in {territory.name}"
                )

            # We are now in ATTACK phase
            self.game.next_phase()
            # If the player can't attack or doesn't want to
            if (
                not self.game.active_player.attack_wants_attack()
                or not self.game.has_valid_attack(self.game.active_player)
            ):
                # We should run the entire game loop again up to agent_player's turn
                # This should never happen though, because the player will always deploy troops and for now we make it always want to attack
                raise f"Error in current design"

            # We choose the attacking territory
            attacker = self.game.active_player.attack_choose_attack_territory()
            self.game.attacking_territory = attacker
            logger.debug(
                f"{self.game.active_player.name} attacking from {attacker.name}"
            )

        else:
            raise f"Incorrect phase: {self.game.game_phase}"

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        logger.debug(self.game)
        return observation, info

    def get_masked_action_space(self):
        """
        Based on the state of the game, return the list of available actions

        Currently, only choosing the attack territory.
        Available actions is the list of territories that are adjacent to the attacking territory AND are not owned by the player
        """
        attacking_player = self.agent_player
        attacker = self.game.attacking_territory

        adjacent_territories_names = attacker.adjacent_territories_names
        adjacent_territories = [
            self.game.game_map.get_territory_from_name(t)
            for t in adjacent_territories_names
        ]
        valid_actions = [
            t.id_
            for t in adjacent_territories
            if t.occupying_player_name != attacking_player.name
        ]
        return valid_actions

    def play_other_player_turn(self):

        while self.game.active_player != self.agent_player:
            self.game.draft_phase(self.game.active_player)
            self.game.attack_phase(self.game.active_player)

            # Check if the game ended during another player's turn
            if self.game.is_game_over():
                terminated = True
                return terminated

            self.game.next_turn()
        return False

    def play_from_agent_player_draft(self):

        if self.game.game_phase == "DRAFT":
            troops_to_deploy = self.game.get_deployment_troops(self.game.active_player)

            while troops_to_deploy > 0:
                deploying = self.game.active_player.draft_choose_troops_to_deploy(
                    troops_to_deploy
                )
                territory = self.game.active_player.draft_choose_territory_to_deploy()
                territory.add_troops(deploying)
                troops_to_deploy -= deploying

            # We are now in ATTACK phase
            self.game.next_phase()
            # If the player can't attack or doesn't want to
            while (
                not self.game.active_player.attack_wants_attack()
                or not self.game.has_valid_attack(self.game.active_player)
            ):
                self.game.next_turn()
                terminated = self.play_other_player_turn()
                if terminated:
                    return terminated
                return self.play_from_agent_player_draft()

            # We choose the attacking territory
            attacker = self.game.active_player.attack_choose_attack_territory()
            self.game.attacking_territory = attacker
            return False

        else:
            raise f"Incorrect phase: {self.game.game_phase}"

    def step(self, action):
        """
        For now this is called right before choosing the target territory (action is target territory)
        So everything else needs to be processed after applying the action, including:
            - Running the rest of the player's turn
            - Running other non agent turns
            - Running the beginning of the agent turn (choosing attacker)
        """

        initial_player_terr_numbers = len(
            self.game.active_player.controlled_territories
        )

        masked_action_space = self.get_masked_action_space()

        if action not in masked_action_space:
            raise ValueError(f"Invalid action {action} selected.")

        done = False
        reward = 0

        # The agent turn. This will always be called after choosing attacker
        target_territory_id = action
        target_territory = self.game.game_map.get_territory_from_id(target_territory_id)

        attack_remaining, defender_remaining, dice_nb = self.game.perform_attack(
            self.agent_player, self.game.attacking_territory, target_territory
        )

        attack_info = {
            "attack_remaining": attack_remaining,
            "defender_remaining": defender_remaining,
            "target": target_territory,
            "attacker": self.game.attacking_territory,
            "player": self.agent_player,
            "attack_dice_nb": dice_nb,
        }
        self.game.after_attack(attack_info=attack_info)
        # TODO add reward if territory conquered ?

        if self.game.is_game_over():
            if self.game.remaining_players[0] == self.agent_player:
                reward = WIN_GAME_REWARD
            else:
                reward = LOSE_GAME_REWARD

            terminated = True
            obs = self._get_obs()
            return obs, reward, terminated, False, self._get_info()

        # If player keep attacking, we choose an attacker again and we return the state
        if self.game.active_player.attack_wants_attack() and self.game.has_valid_attack(
            self.game.active_player
        ):
            attacker = self.game.active_player.attack_choose_attack_territory()
            self.game.attacking_territory = attacker

            current_terr_nb = len(self.game.active_player.controlled_territories)
            reward = (
                current_terr_nb - initial_player_terr_numbers
            ) * TERRITORY_GAIN_REWARD
            return self._get_obs(), reward, False, False, self._get_info()

        # Else we check if game is over & we move on to the next phase
        if self.game.is_game_over():
            if self.game.remaining_players[0] == self.agent_player:
                reward = WIN_GAME_REWARD
            else:
                reward = LOSE_GAME_REWARD

            terminated = True
            obs = self._get_obs()
            return obs, reward, terminated, False, self._get_info()

        self.game.next_phase()
        # TODO What do in reinforce phase?

        self.game.next_turn()

        terminated = self.play_other_player_turn()

        if terminated:
            if self.game.remaining_players[0] == self.agent_player:
                reward = WIN_GAME_REWARD
            else:
                reward = LOSE_GAME_REWARD
            obs = self._get_obs()
            return obs, reward, terminated, False, self._get_info()

        terminated = self.play_from_agent_player_draft()
        if terminated:
            if self.game.remaining_players[0] == self.agent_player:
                reward = WIN_GAME_REWARD
            else:
                reward = LOSE_GAME_REWARD
            obs = self._get_obs()
            return obs, reward, terminated, False, self._get_info()

        current_terr_nb = len(self.game.active_player.controlled_territories)
        reward = (current_terr_nb - initial_player_terr_numbers) * TERRITORY_GAIN_REWARD

        # It should be now back up to the agent making a new choice
        return self._get_obs(), reward, False, False, self._get_info()

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        if self.render_mode == "human":
            self.game.render()

    def close(self):
        return


if __name__ == "__main__":
    p1 = Player_Random("p1")
    p2 = Player_Random("p2")
    game = Game("test_map_v0", [p1, p2])
    game.init_players()
    game.active_player = p1
    env = RiskEnv_Choice_is_attack_territory(game, render_mode=None)
    print(env._get_obs())
