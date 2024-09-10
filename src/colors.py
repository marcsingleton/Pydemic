"""Functions for displaying text with color and formatting."""

color_codes = {'red': '31',
                'blue': '34',
                'yellow': '33',
                'black': '30',
                'white': '37'}

def as_color(text, color, bold=False):
    color_code = color_codes[color]
    weight = 1 if bold else 0
    string = f'\033[{weight};{color_code}m{text}\033[0;m'
    return string

def as_underline(text):
    return f"\033[4m{text}\033[0m"
