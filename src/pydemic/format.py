"""Functions for displaying text with color and formatting."""

import sys
from time import sleep

color_codes = {
    'red': '160',
    'blue': '75',
    'yellow': '227',
    'black': '244',
    'light_blue': '116',
    'purple': '141',
    'orange': '214',
    'light_green': '114',
    'green': '36',
    'brown': '137',
    'white': '231',
}
indent = 4 * ' '
prompt_prefix = '>>> '


def as_color(text, color):
    color_code = color_codes.get(color, None)
    if color_code is None:
        string = text
    else:
        string = f'\033[38;5;{color_code}m{text}\033[0;m'
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
