from setuptools import setup

long_description = """
## Installation

You can install the package using pip:

```pip install gnomes-at-night-gym```

## Usage

Here is an example of how to import and use this package:

```python
import gnomes_at_night_gym
env = gym.make("gnomes_at_night_gym:Board9A-v0", render_mode="rgb_array", round=1)
"""

setup(
    name="gnomes_at_night_gym",
    version="0.0.3",
    description='An environment for Gnomes at Night based on OpenAI gym.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Shenghui Chen',
    install_requires=[
        "gymnasium==0.29.1", 
        "pygame==2.5.2", 
        "numpy==1.26.1"
    ],
)