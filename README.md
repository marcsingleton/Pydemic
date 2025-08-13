# Pydemic

## Background
The origin of this project dates back to 2018 when, during my early days of learning Python, I was curious about object-oriented programming. Games are a great fit for object-oriented patterns since they have complex behaviors and interactions that are represented by literal objects. I had recently bought the game and was familiar with its rules, so I naturally chose it for this project. I was also curious about finding the optimal strategy, so a longer range goal was to hook the text-based interface up to a reinforcement learning system.

I ultimately managed to get a mostly usable prototype working before running out of steam and taking a break. Years later, I came across it again while re-organizing my coding projects and thought it was a shame I left it almost finished. While it ended up being a much bigger job than I expected (read about it on [my blog](https://marcsingleton.github.io/posts/pydemic-a-command-line-implementation-of-the-board-game-pandemic/)!), I managed to bring it to a point where I felt someone who was already familiar with the rules could reasonably play a game from start to finish.

## Dependencies
Pydemic was developed with Python 3.12.3, but to my knowledge, it doesn't use any features specific to this version and is likely compatible with any relatively recent Python release. (3.10 is specified as a minimum dependency to be on the safe side though.)

Text is colored using ANSI escape sequences for 8-bit colors, so a compatible terminal emulator is required to properly display the output. Pydemic also uses Python's [readline interface](https://docs.python.org/3/library/readline.html) for command completion, which is only supported on Unix-like operating systems. Windows users should install WSL.

## Installation
I recommend installing into a virtual environment. To create one and activate it, use:

```
VENV_PATH=/path/to/new/virtual/environment
python -m venv $VENV_PATH
source $VENV_PATH/bin/activate
```

where `VENV_PATH` is the path to the Pydemic installation.

Then install using:

```
git clone https://github.com/marcsingleton/Pydemic.git
cd Pydemic
pip install .
```

where the path is to the previously downloaded repo.

## Playing
To play the game, use:

```
python -m pydemic
```

after activating the virtual environment with the installation.

The package includes many documented command-line options for speeding game setup and tweaking advanced settings. Use the `-h` flag with the previous command to view these options. I won't explain the rules in any detail since my goal is not to replace the game itself. If you're interested in understanding how game play works, I encourage you to support the creators by buying a set and getting familiar with it as it's meant to be played!

## Possible Enhancements
While I don't expect anyone to find a text-based interface an enjoyable way to play Pandemic, this project has been a great exercise in coding a complex, interactive program. I likely won't work on it again in a major way (except for bugs and compatibility issues), but in the spirit of learning I have some ideas for possible enhancements that could be fun mini-projects. I've listed them in [TODO.md](./TODO.md) in no particular order along with any ideas for their implementation or notes about key challenges:

## License
Pydemic © 2024 by Marc Singleton is licensed under CC BY-NC 4.0.
