# Gnomes at Night Gym Environment

This repo contains the custom Gym environment for the game of Gnomes at Night. Designed to test reinforcement learning algorithms on a cooperative task in imperfect-information environments.


## Installation

To install the environment, use the following command:
```sh
git clone https://github.com/vivianchen98/gnomes-at-night-gym.git
cd gnomes-at-night-gym
python -m venv .env
source .env/bin/activate
pip install -e .
```

## Usage

To get started with the Gnomes at Night Gym Environment, simply import it into your project and instantiate it:

```python
import gymnasium as gym
import gnomes_at_night_gym

env = gym.make("gnomes_at_night_gym/GnomesAtNight9-boardA")
```