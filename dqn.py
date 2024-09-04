from collections import deque
import random

import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow.keras.layers as tfl

from game.game import Game
from game.player import Player_Random, Player_RL

import gymnasium as gym
from gymnasium.spaces.utils import flatten_space

from loguru import logger


# Memory for experience replay
class ReplayMemory:
    def __init__(self, maxlen):
        self.memory = deque([], maxlen=maxlen)

    def append(self, transition):
        self.memory.append(transition)

    def sample(self, sample_size):
        return random.sample(self.memory, sample_size)

    def __len__(self):
        return len(self.memory)


class DQN:
    # Hyperparameters
    learning_rate = 1e-4
    mini_batch_size = 128  # How often do we optimize the network
    gamma = 0.9
    target_update_freq = 64  # How often do we copy
    replay_memory_size = 50_000  # Size of the replay memory

    epsilon_start = 1
    epsilon_end = 0.1
    epsilon_decay = 0.99

    def __init__(self, env: gym.Env) -> None:
        self.env = env

        flattened_obs = env.unwrapped.flatten_observation_space()

        self.num_states = flattened_obs.shape[0]
        self.num_actions = env.action_space.n

        self.memory = ReplayMemory(self.replay_memory_size)

        self.optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.loss_function = tf.keras.losses.MeanSquaredError()

        self.policy_dqn = self.create_q_model(self.num_states, self.num_actions)
        self.target_dqn = self.create_q_model(self.num_states, self.num_actions)
        self.target_dqn.set_weights(self.policy_dqn.get_weights())

        self.epsilon = self.epsilon_start

    def create_q_model(self, input_dim, output_dim):
        model = tf.keras.Sequential()
        model.add(tfl.Dense(input_shape=[input_dim], units=64, activation="relu"))
        model.add(tfl.Dense(64, activation="relu")),
        model.add(tfl.Dense(64, activation="relu")),
        model.add(tfl.Dense(output_dim, activation="linear"))
        model.compile(optimizer=self.optimizer, loss=self.loss_function)
        return model

    def select_action(self, state, episode_nb):
        valid_actions = self.env.unwrapped.get_masked_action_space()
        logger.debug(f"Valid actions: {valid_actions}")
        if episode_nb < 200:
            action = np.random.choice(valid_actions)
        elif np.random.random() < self.epsilon:
            action = np.random.choice(valid_actions)
        else:
            q_values = self.target_dqn.predict(state.reshape(1, -1), verbose=0)
            logger.debug(f"Q_values: {q_values}")
            mask = np.zeros(self.num_actions, dtype=int)
            mask[valid_actions] = 1
            logger.debug(f"Mask: {mask}")

            valid_q_values = np.where(mask == 1, q_values, -np.inf)
            logger.debug(f"Valid_q_values: {valid_q_values}")
            action = np.argmax(valid_q_values[0])

        return action

    def train_network(self, episode_nb):
        if len(self.memory) > self.mini_batch_size and episode_nb > 200:

            mini_batch = self.memory.sample(self.mini_batch_size)
            self.optimize(mini_batch)

            # Decay epsilon
            new_e = max(self.epsilon * self.epsilon_decay, self.epsilon_end)
            self.epsilon = new_e
            self.epsilon_history.append(self.epsilon)

            self.updateCounter += 1

            # Copy policy network to target network after a certain number of steps
            if self.updateCounter > self.target_update_freq:
                self.target_dqn.set_weights(self.policy_dqn.get_weights())
                self.updateCounter = 0

    def train(self, episodes=500):
        # List to keep track of epsilon decay
        self.epsilon_history = []
        self.updateCounter = 0

        steps_per_episode = []

        logger.debug(f"Initialization done, with {episodes} episodes")

        for i in range(episodes):

            logger.info(f"Simulating episode {i}, epsilon={self.epsilon}")
            state = self.env.reset()[0]

            # Because on super small maps 1v1 sometimes random player can win turn 1
            while self.env.unwrapped.game.is_game_over():
                logger.debug(f"P1 won turn 1")
                state = self.env.reset()[0]
            state = self.env.unwrapped.flatten_obs(state)

            terminated = False  # True when agent reach the target
            truncated = False  # True when agent takes too long

            steps_to_complete = 0

            while not terminated and not truncated:

                action = self.select_action(state, i)

                new_state, reward, terminated, truncated, _ = env.step(action)
                new_state = self.env.unwrapped.flatten_obs(new_state)

                self.memory.append((state, action, new_state, reward, terminated))

                state = new_state

                steps_to_complete += 1

            logger.debug(f"Steps to complete the episode: {steps_to_complete}")

            steps_per_episode.append(steps_to_complete)

            self.train_network(episode_nb=i)

        logger.debug(f"Episodes overn")
        # Close environment
        env.close()

        # Save policy
        self.target_dqn.save("warehouse_dqn.keras")

        # Create new graph
        plt.figure(1)

        plt.subplot(121)  # plot on a 1 row x 2 col grid, at cell 1
        plt.plot(steps_per_episode)

        # Plot epsilon decay (Y-axis) vs episodes (X-axis)
        plt.subplot(122)  # plot on a 1 row x 2 col grid, at cell 2
        plt.plot(self.epsilon_history)

        # Save plots
        plt.savefig("warehouse_dqn.png")

    def optimize(self, mini_batch):

        states, actions, new_states, rewards, terminals = zip(*mini_batch)

        states = tf.convert_to_tensor(np.vstack(states), dtype=tf.float32)
        new_states = tf.convert_to_tensor(np.vstack(new_states), dtype=tf.float32)

        # TODO: should be policy network?
        future_qs = tf.reduce_max(
            self.target_dqn.predict(new_states, verbose=0), axis=1
        )
        target_qs = rewards + self.gamma * future_qs * (
            1 - np.array(terminals, dtype=np.float32)
        )

        masks = tf.one_hot(actions, self.num_actions)

        with tf.GradientTape() as tape:
            q_values = self.policy_dqn(states)
            # print(f"Shape of q_values: {q_values.shape}")
            # print(f"Q values during optimization: {q_values}")
            q_action = tf.reduce_sum(q_values * masks, axis=1)
            loss = self.loss_function(target_qs, q_action)
            # print(loss)

        grads = tape.gradient(loss, self.policy_dqn.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.policy_dqn.trainable_variables))

    # Run the FrozeLake environment with the learned policy
    def test(self, episodes):
        # Create FrozenLake instance
        env = gym.make(
            "warehouse-robot-v0",
            render_mode="human",
        )

        num_states = env.observation_space.shape[0]
        num_actions = env.action_space.n

        # Load learned policy
        self.policy_dqn = tf.keras.models.load_model("warehouse_dqn.keras")

        for i in range(episodes):
            state = env.reset()[0]  # Initialize to state 0
            terminated = False  # True when agent falls in hole or reached goal
            truncated = False  # True when agent takes more than 200 actions

            # Agent navigates map until it falls into a hole (terminated), reaches goal (terminated), or has taken 200 actions (truncated).
            while not terminated and not truncated:
                # Select best action
                tensor = tf.convert_to_tensor(
                    [self.state_to_dqn_input(state, num_states)], dtype=tf.float32
                )

                action = tf.argmax(
                    self.policy_dqn(tensor)[0]
                ).numpy()  # TODO change here how we transform our state

                # Execute action
                state, reward, terminated, truncated, _ = env.step(action)

        env.close()


if __name__ == "__main__":
    p1 = Player_Random("p1")
    p2 = Player_RL("p2")
    game = Game("test_map_v0", [p1, p2])

    env = gym.make("game/RiskEnv-V0", game=game, agent_player=p2, render_mode=None)
    RL_bot = DQN(env)
    RL_bot.train(1000)
