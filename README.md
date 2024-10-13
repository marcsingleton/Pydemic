# Pydemic

## Background
This is a text-based implementation of the cooperative board game Pandemic. I first started working on it sometime in 2018 back in my early days of learning Python. At the time, I was curious about object-oriented programming and was looking for a good project to start using it. Games are a great fit for object-oriented patterns since they often have complex and interacting behaviors that are represented by literal objects. I had recently bought the game and was familiar with its rules, so I naturally chose it for this project. I was also curious about finding the optimal strategy, so a longer range goal was to hook the text-based interface up to a reinforcement learning system.

In the end, I got a mostly working and mostly complete implementation up and running before running out of steam. Years later, I came across it again while re-organizing my coding projects and thought it was a shame I left it almost finished. While there are still a few things I could do to bring it to a "professional" level of polish, my main goal was to make it stable and to develop its interface to a point where a player already familiar with the rules could reasonably discover how to use it.

## Dependencies
Pydemic was developed with Python 3.12.3, but to my knowledge, it doesn't use any features specific to this version and is likely compatible with any relatively recent Python release. (3.10 is specified as a minimum dependency to be on the safe side though.)

Text is colored using ANSI escape sequences for 8-bit colors, so a compatible terminal emulator is required to properly display the output. Pydemic also uses Python's [readline interface](https://docs.python.org/3/library/readline.html) for command completion, which is only supported on Unix-like operating systems. Windows users should install WSL.

## Installation
First, clone (or download the repo directly) with:

```
git clone https://github.com/marcsingleton/Pydemic.git
```

I recommend installing into a virtual environment. To create one and activate it, use:

```
VENV_PATH=/path/to/new/virtual/environment
python -m venv $VENV_PATH
source $VENV_PATH/bin/activate
```

where `VENV_PATH` is the path to the Pydemic installation.

Finally, to install, run:

```
pip install /path/to/Pydemic
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
