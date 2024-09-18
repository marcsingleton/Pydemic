"""Functions for displaying text with color and formatting."""

import sys
from time import sleep

color_codes = {
    'red': '31',
    'blue': '34',
    'yellow': '33',
    'black': '30',
    'white': '37',
    None: '',
}
indent = 4 * ' '
prompt_prefix = '>>> '


def as_color(text, color, bold=False):
    color_code = color_codes[color]
    weight = 1 if bold else 0
    string = f'\033[{weight};{color_code}m{text}\033[0;m'
    return string


def as_underline(text):
    return f'\033[4m{text}\033[0m'


def cards_to_string(cards):
    cards_string = ', '.join([as_color(card.name, card.color) for card in cards])
    return '[' + cards_string + ']'


def slow_print(*args, sep=' ', end='\n'):
    for arg in args:
        arg = str(arg)
        for char in arg:
            sys.stdout.write(char)
            sys.stdout.flush()
            sleep(0.01)
        sys.stdout.write(sep)
    sleep(0.15)
    sys.stdout.write(end)
