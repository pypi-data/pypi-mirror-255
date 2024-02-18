from gymnasium.envs.registration import register

register(
     id="Board9A-v0",
     entry_point="gnomes_at_night_gym.envs:GnomesAtNightEnv9A",
     max_episode_steps=300,
)

register(
     id="Board5A-v0",
     entry_point="gnomes_at_night_gym.envs:GnomesAtNightEnv5A",
     max_episode_steps=300,
)