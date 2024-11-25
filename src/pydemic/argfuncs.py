"""Functions for argument-related functions."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import pydemic.maps as maps
from pydemic.display import prompt_prefix
from pydemic.version import __version__


def parse_args(
    args,
    player_min_word,
    player_max_word,
    epidemic_min_word,
    epidemic_max_word,
    default_map,
    start_city,
    outbreak_max,
    infection_seq,
    cube_num,
    station_num,
):
    parser = ArgumentParser(
        prog='pydemic',
        description='A text-based implementation of the board game Pandemic.',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--player_num',
        default=None,
        type=int,
        help=(
            f'the number of players; '
            f'must be between {player_min_word} and {player_max_word}; '
            f'ignored when player_names is given'
        ),
    )
    parser.add_argument(
        '--player_names',
        default=None,
        help=(
            'a comma-delimited list of unique player names; '
            'leading and trailing commas are ignored; '
            'player_num is inferred from this list'
        ),
    )
    parser.add_argument(
        '--epidemic_num',
        default=None,
        type=int,
        help=(
            f'the number of epidemics; '
            f'must be between {epidemic_min_word} and {epidemic_max_word}'
        ),
    )
    parser.add_argument(
        '--map',
        default=default_map,
        help='the name of the map',
    )
    parser.add_argument(
        '--start_city',
        default=start_city,
        help='the name of the starting city',
    )
    parser.add_argument(
        '--outbreak_max',
        default=outbreak_max,
        type=int,
        help='the maximum number of outbreaks before game over',
    )
    parser.add_argument(
        '--infection_seq',
        default=infection_seq,
        help='the sequence of the infection rate track; entries must be positive and increasing',
    )
    parser.add_argument(
        '--cube-num',
        default=cube_num,
        type=int,
        help='the total number of cubes for each disease',
    )
    parser.add_argument(
        '--station_num',
        default=station_num,
        type=int,
        help='the total number of stations',
    )

    return parser.parse_args(args)


def check_args(
    args,
    player_min,
    player_max,
    player_min_word,
    player_max_word,
    epidemic_min,
    epidemic_max,
    epidemic_min_word,
    epidemic_max_word,
):
    # Get player settings
    if args.player_names is not None:
        args.player_names = args.player_names.strip(',').split(',')
        args.player_num = len(args.player_names)
        if args.player_num < player_min or args.player_num > player_max:
            print(
                f'The number of entries in argument player_names is not between '
                f'{player_min_word} and {player_max_word}. Quitting...'
            )
            exit(1)
        if len(set(args.player_names)) != args.player_num:
            print('Argument player_names are not unique. Quitting...')
            exit(1)
    elif args.player_num is not None and (
        args.player_num < player_min or args.player_num > player_max
    ):
        print(
            f'Argument player_num must be between {player_min_word} and {player_max_word}. '
            f'Quitting...'
        )
        exit(1)

    # Get epidemic settings
    if args.epidemic_num is not None and (
        args.epidemic_num < epidemic_min or args.epidemic_num > epidemic_max
    ):
        print(
            f'Argument epidemic_num must be between '
            f'{epidemic_min_word} and {epidemic_max_word}. Quitting...'
        )
        exit(1)

    # Get map settings
    if args.map not in maps.maps:
        print(f'Argument map {args.map} is not in library. Quitting...')
        exit(1)
    args.map = maps.maps[args.map]
    if args.start_city not in args.map:
        print(f'Argument start_city {args.start_city} not in map {args.map}. Quitting...')
        exit(1)

    # Get outbreak settings
    if args.outbreak_max < 0:
        print(f'Argument outbreak_max must be non-negative. Quitting...')
        exit(1)

    # Get infection_seq settings
    args.infection_seq = args.infection_seq.strip(',').split(',')
    if not args.infection_seq:
        print('Argument infection_seq is empty. Quitting...')
        exit(1)

    infection_seq = []
    for entry in args.infection_seq:
        try:
            value = int(entry)
        except ValueError:
            print(f'Could not convert "{entry}" to integer in argument infection_seq. Quitting...')
            exit(1)
        if value <= 0:
            print('Non-positive entry found in argument infection_seq. Quitting...')
            exit(1)
        if infection_seq and value < infection_seq[-1]:
            print('Argument infection_seq is not monotonic. Quitting...')
            exit(1)
        infection_seq.append(value)
    args.infection_seq = infection_seq

    # Get cube number settings
    if args.cube_num < 1:
        print('Argument cube_num must be positive. Quitting')
        exit(1)

    # Get station number settings
    if args.station_num < 1:
        print('Argument station_num must be positive. Quitting...')
        exit(1)


def dialog_args(
    args,
    player_min,
    player_max,
    player_min_word,
    player_max_word,
    epidemic_min,
    epidemic_max,
    epidemic_min_word,
    epidemic_max_word,
):
    # Print greeting
    print(f'Welcome to Pydemic {__version__}! Are you ready to save humanity?')

    # player_num and player_names dialog(s)
    if args.player_num is None:
        print()
        while not args.player_num:
            text = input(
                f'{prompt_prefix}Enter a number between {player_min_word} and {player_max_word} '
                f'for the number of players: '
            )
            try:
                value = int(text)
            except ValueError:
                print(f'{text} is not a valid number. Please try again.')
                continue
            if value < player_min or value > player_max:
                print(
                    f'The number of players must be between {player_min_word} and {player_max_word}. '
                    f'Please try again.'
                )
                continue
            args.player_num = value
    if args.player_names is None:
        print()
        i = 1
        args.player_names = []
        while i < args.player_num + 1:
            text = input(f"{prompt_prefix}Enter player {i}'s name: ")
            if text in args.player_names:
                print('Name is not unique. Please try again.')
            else:
                args.player_names.append(text)
                i += 1

    # epidemic_num dialog
    if args.epidemic_num is None:
        print()
        while not args.epidemic_num:
            text = input(
                f'{prompt_prefix}'
                f'Enter a number between {epidemic_min_word} and {epidemic_max_word} '
                f'for the number of epidemics in play: '
            )
            try:
                value = int(text)
            except ValueError:
                print(f'{text} is not a valid number. Please try again.')
                continue
            if value < epidemic_min or value > epidemic_max:
                print(
                    f'The number of epidemics must be between '
                    f'{epidemic_min_word} and {epidemic_max_word}. Please try again.'
                )
                continue
            args.epidemic_num = value
