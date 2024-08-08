from gymnasium.envs.registration import register

register(
    id="game/RiskEnv-V0",
    entry_point="game.custom_risk_env_v0:RiskEnv_Choice_is_attack_territory",
    max_episode_steps=100,
)
