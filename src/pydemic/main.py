"""A text-based implementation of the board game Pandemic."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from inspect import cleandoc
from random import shuffle
from sys import exit
from time import sleep

import pydemic.cards as cards
import pydemic.maps as maps
import pydemic.pieces as pieces
import pydemic.roles as roles
import pydemic.shared as shared
from pydemic.format import as_color, cards_to_string, indent, prompt_prefix
from pydemic.version import __version__


# FUNCTIONS
# Generic actions
def draw_infect(*args):
    """Draw a card from the infection deck.

    syntax: infect
    """
    shared.infection_deck.draw()
    shared.infect_count -= 1


def draw_player(*args):
    """Draw a card from the player deck.

    syntax: draw
    """
    card = shared.player_deck.draw()
    shared.draw_count -= 1
    if card.type == 'epidemic':
        print('An epidemic occurred.')
        epidemic()
        shared.player_deck.discard(card)
    else:
        print(f'{as_color(card.name, card.color)} was drawn.')
        shared.current_player.add_card(card)


def play_event(*args):
    """Play an event card.

    syntax: event PLAYER EVENT_CARD
    """
    if len(args) != 2:
        print('Event failed: Incorrect number of arguments')
        return
    if args[0] not in shared.players:
        print('Event failed: Nonexistent player specified.')
        return
    player = shared.players[args[0]]
    player.event(args[1:])  # Slice to maintain as list


def quit(*args):
    """Quit the game.

    syntax: quit
    """
    if len(args) != 0:
        print(f'Action failed: Incorrect number of arguments.')
        return

    text = input(f'{prompt_prefix}Are you sure you want to quit? (y/n) ').lower()
    if text == 'y' or text == 'yes':
        print('Thanks for playing!')
        exit()


def print_neighbors(*args):
    """Display the neighbors of a given city.

    If the CITY argument is omitted, the city of the current player is used.

    syntax: neighbors [CITY]
    """
    if len(args) == 0:
        city = shared.cities[shared.current_player.city]
    elif len(args) == 1:
        try:
            city = shared.cities[args[0]]
        except KeyError:
            print('Action failed: Nonexistent city specified.')
    else:
        print('Action failed: Incorrect number of arguments.')

    print(f'The neighbors of {as_color(city.name, city.color)} are:')
    for city in city.neighbors:
        city = shared.cities[city]
        print(f'{indent}{as_color(city.name, city.color)}')


def print_status(*args):
    """Display the current state of the game.

    syntax: status
    """
    if len(args) != 0:
        print(f'Action failed: Incorrect number of arguments.')
        return

    print()
    print(f'-------------------- TURN {shared.turn_count} --------------------')

    for disease in shared.diseases.values():
        print(as_color(disease.color.upper(), disease.color))
        print(f'{indent}Status:', disease.status.name.lower())
        print(f'{indent}Cubes remaining:', disease.cubes)
    print()

    for player in shared.players.values():
        print(player.name.upper(), f'({player.role.upper()})')
        player.print_status(indent)
    print()

    for city in shared.cities.values():
        header = False
        for color, cubes in city.cubes.items():
            if cubes > 0:
                if not header:  # Add header
                    print(as_color(city.name.upper(), city.color))
                    header = True
                print(f'{indent}{as_color(color, color)}:', cubes)
        if city.station:
            if not header:
                print(as_color(city.name.upper(), city.color))
                header = True
            print(f'{indent}Research station: True')
    print()

    print('Infection rate:', shared.infection_track.rate)
    print('Outbreaks:', shared.outbreak_track.count)
    print('Cards remaining:', len(shared.player_deck.draw_pile))
    print('Infection discard:', cards_to_string(shared.infection_deck.discard_pile))
    print()

    print(f'Turn: {shared.current_player.name}')


# Flow control
def main():
    # CONSTANTS
    player_min, player_max = 2, 4
    player_min_word, player_max_word = 'two', 'four'
    epidemic_min, epidemic_max = 4, 6
    epidemic_min_word, epidemic_max_word = 'four', 'six'

    # PARSING
    # Add arguments
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
    parser.add_argument('--map', default='default', help='the name of the map')
    parser.add_argument('--start_city', default='atlanta', help='the name of the starting city')
    parser.add_argument(
        '--outbreak_max',
        default=8,
        type=int,
        help='the maximum number of outbreaks before game over',
    )
    parser.add_argument(
        '--infection_seq',
        default='2,2,2,3,3,4,4',
        help=(
            'the sequence of the infection rate track; entries must be positive and increasing'
        ),
    )
    parser.add_argument(
        '--cube-num', default=24, type=int, help='the total number of cubes for each disease'
    )
    parser.add_argument('--station_num', default=6, type=int, help='the total number of stations')
    args = parser.parse_args()

    # Parameter checks
    # Get player settings
    player_num = args.player_num
    player_names = args.player_names
    if player_names is not None:
        player_names = player_names.strip(',').split(',')
        player_num = len(player_names)
        if player_num < player_min or player_num > player_max:
            print(
                f'The number of entries in argument player_names is not between '
                f'{player_min_word} and {player_max_word}. Quitting...'
            )
            exit(1)
        if len(set(player_names)) != player_num:
            print('Argument player_names are not unique. Quitting...')
            exit(1)
    elif player_num is not None and (
        player_num < player_min or player_num > player_max
    ):
        print(
            f'Argument player_num must be between {player_min_word} and {player_max_word}. '
            f'Quitting...'
        )
        exit(1)

    # Get epidemic settings
    epidemic_num = args.epidemic_num
    if epidemic_num is not None and (epidemic_num < epidemic_min or epidemic_num > epidemic_max):
        print(
            f'Argument epidemic_num must be between '
            f'{epidemic_min_word} and {epidemic_max_word}. Quitting...'
            )
        exit(1)

    # Get map settings
    if args.map not in maps.maps:
        print(f'Argument map {args.map} is not in library. Quitting...')
        exit(1)
    map = maps.maps[args.map]
    if args.start_city not in map:
        print(f'Argument start_city {args.start_city} not in map {args.map}. Quitting...')
        exit(1)
    start_city = args.start_city

    # Get outbreak and infection track settings
    if args.outbreak_max < 0:
        print(f'Argument outbreak_max must be non-negative. Quitting...')
    outbreak_max = args.outbreak_max
    infection_seq = []
    for entry in args.infection_seq.split(','):
        try:
            value = int(entry)
        except ValueError:
            print(f'Could not convert "{entry}" to integer in argument infection_seq. Quitting...')
            exit(1)
        if value <= 0:
            print('Non-positive entry found in argument infection_seq. Quitting...')
            exit(1)
        infection_seq.append(value)

    # Get cube and station number settings
    if args.cube_num < 1:
        print('Argument cube_num must be positive. Quitting')
        exit(1)
    cube_num = args.cube_num
    if args.station_num < 1:
        print('Argument station_num must be positive. Quitting...')
        exit(1)
    station_num = args.station_num

    # INITIALIZATION
    # Print greeting
    print(f'Welcome to Pydemic {__version__}! Are you ready to save humanity?')

    # player_num and player_names dialog(s)
    if player_num is None:
        print()
        while not player_num:
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
            player_num = value
    if player_names is None:
        print()
        i = 1
        player_names = []
        while i < player_num + 1:
            text = input(f"{prompt_prefix}Enter player {i}'s name: ")
            if text in player_names:
                print('Name is not unique. Please try again.')
            else:
                player_names.append(text)
                i += 1
    start_hand_num = 6 - player_num

    # epidemic_num dialog
    if epidemic_num is None:
        print()
        while not epidemic_num:
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
            epidemic_num = value

    # Count unique disease colors
    colors = set([attrs.color for attrs in map.values()])

    # Instantiate diseases
    for color in colors:
        shared.diseases[color] = pieces.Disease(color, cube_num)

    # Instantiate trackers
    shared.outbreak_track = pieces.OutbreakTrack(outbreak_max)
    shared.infection_track = pieces.InfectionTrack(infection_seq)

    # Instantiate cities and associated cards
    city_cards = []
    infection_cards = []
    shared.station_count = station_num
    for city, attrs in map.items():
        shared.cities[city] = pieces.City(city, attrs.neighbors, attrs.color, colors)
        city_cards.append(cards.CityCard(city, attrs.color, attrs.population))
        infection_cards.append(cards.InfectionCard(city, attrs.color))
    shared.cities[start_city].add_station()  # Add research station to start city

    # Instantiate decks
    shared.player_deck = cards.PlayerDeck(city_cards + cards.event_cards)
    shared.infection_deck = cards.InfectionDeck(infection_cards)

    # Instantiate players
    role_list = list(roles.roles)
    shuffle(role_list)
    for player in player_names:
        role = role_list.pop()
        shared.players[player] = roles.roles[role](player)
        starting_cards = [shared.player_deck.draw() for _ in range(start_hand_num)]
        for card in starting_cards:
            shared.players[player].add_card(card)

    # Infect cities
    for _ in range(3):
        for i in range(3, 0, -1):
            shared.infection_deck.draw(i, verbose=False)

    # Add epidemics
    shared.player_deck.add_epidemics(epidemic_num)

    # Set turns and initial positions
    shared.turn_count = 0
    player_names = turn_order(player_names)
    for player in shared.players.values():
        player.city = start_city  # Set separately from instantiation so special abilities do not interfere with setup

    # PLAY
    while True:
        # Turn setup
        turn = shared.turn_count % player_num
        shared.current_player = shared.players[player_names[turn]]
        shared.draw_count = 2
        shared.infect_count = shared.infection_track.rate
        sleep(1)
        print_status()

        # Player actions
        print()
        while shared.current_player.action_count > 0:
            commands = {
                **shared.current_player.actions,
                'neighbors': print_neighbors,
                'event': play_event,
                'status': print_status,
                'quit': quit,
            }
            prompt = (
                f'{prompt_prefix}Enter your next command '
                f'({shared.current_player.action_count} action(s) remaining): '
            )
            interface(commands, prompt)

        # Draw cards
        print()
        while shared.draw_count > 0:
            commands = {
                'draw': draw_player,
                'event': play_event,
                'status': print_status,
                'quit': quit,
            }
            prompt = (
                f'{prompt_prefix}Draw or play event card '
                f'({shared.draw_count} draw(s) remaining): '
            )
            interface(commands, prompt)
            shared.outbreak_track.reset()  # Reset outbreak after each draw

        # Infect cities
        print()
        while shared.infect_count > 0:
            commands = {
                'infect': draw_infect,
                'event': play_event,
                'status': print_status,
                'quit': quit,
            }
            prompt = (
                f'{prompt_prefix}Infect or play event card '
                f'({shared.infect_count} infect(s) remaining): '
            )
            interface(commands, prompt)
            shared.outbreak_track.reset()  # Reset outbreak after each draw

        # Turn cleanup
        shared.current_player.reset()
        shared.turn_count += 1


def interface(commands, prompt):
    args = input(prompt).lower().split()
    if len(args) == 0:
        return
    command = args[0]
    if command == 'help':
        if len(args) == 1:
            print(f'The available commands are: ')
            for command, cmd in commands.items():
                docstring = cmd.__doc__ if cmd.__doc__ else 'NO HELP FOUND'
                docstring = cleandoc(docstring)
                summary = docstring.split('\n')[0]
                print(f'{indent}{command}: {summary}')
        elif len(args) == 2:
            command = args[1]
            try:
                cmd = commands[command]
            except KeyError:
                print(f'{command} is not a currently available command.')
                return
            docstring = cmd.__doc__ if cmd.__doc__ else 'NO HELP FOUND'
            docstring = cleandoc(docstring)
            print(docstring)
        else:
            print(
                'Use "help" for an overview of all currently available commands '
                'or "help COMMAND" for more information on a specific command.'
            )
    else:
        try:
            cmd = commands[command]
        except KeyError:
            print('No currently available command exists with that name. Please try again.')
            return
        args = args[1:]
        cmd(*args)


def turn_order(player_names):
    max_pop = 0
    max_card = ''
    max_player = ''
    for name in player_names:
        player = shared.players[name]
        for card in player.hand.values():
            if isinstance(card, cards.CityCard) and card.population > max_pop:
                max_pop = card.population
                max_card = card
                max_player = player.name
    idx = player_names.index(max_player)
    print()
    print(
        f'{max_player} has the card with the highest population: '
        f'{as_color(max_card.name, max_card.color)} ({max_pop:,})'
    )
    print(f'{max_player} will start the turn order.')
    return player_names[idx:] + player_names[:idx]


def epidemic():
    # Increase
    shared.infection_track.increment()

    # Infect
    shared.infection_deck.infect()

    # Play Resilient Population event if available
    for player in shared.players.values():
        in_hand = 'resilient_population' in player.hand
        if in_hand:  # TODO: Check contingency planner card
            text = input(
                f'{prompt_prefix}Resilient Population event card detected in hand. '
                f'Play now? (y/n) '
            ).lower()
            if text == 'y' or text == 'yes':
                player.hand['resilient_population'].event()
                player.discard('resilient_population')

    # Intensify
    shared.infection_deck.intensify()
