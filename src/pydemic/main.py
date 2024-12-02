"""A text-based implementation of the board game Pandemic."""

import readline
import sys
from inspect import cleandoc
from random import shuffle
from sys import exit
from time import sleep

import pydemic.argfuncs as argfuncs
import pydemic.cards as cards
import pydemic.constants as constants
import pydemic.exceptions as exceptions
import pydemic.pieces as pieces
import pydemic.roles as roles
from pydemic.display import style, indent, prompt_prefix
from pydemic.state import GameState


# Generic commands
def draw_infect(state, *args):
    """Draw a card from the infection deck.

    syntax: infect
    """
    state.infection_deck.draw(state)
    state.infect_count -= 1


def draw_player(state, *args):
    """Draw a card from the player deck.

    syntax: draw
    """
    card = state.player_deck.draw()
    state.draw_count -= 1
    if card.type == 'epidemic':
        print('An epidemic occurred.')
        epidemic(state)
        state.player_deck.discard(card)
    else:
        print(f'{card.display()} was drawn.')
        state.current_player.add_card(state, card)


def play_event(state, *args):
    """Play an event card.

    syntax: event EVENT_CARD
    """
    if len(args) != 1:
        print('Event failed: Incorrect number of arguments')
        return
    for player in state.players.values():
        if player.has_event(args[0]):
            try:
                player.event(state, args[0])
            except exceptions.EventError as error:
                print('Event failed:', error)
                return
            print('Event succeeded!')
            return
    print('Event failed: No player has the specified card.')


def quit(state, *args):
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


def print_neighbors(state, *args):
    """Display the neighbors of a given city.

    If the CITY argument is omitted, the city of the current player is used.

    syntax: neighbors [CITY]
    """
    if len(args) == 0:
        city = state.current_player.city
    elif len(args) == 1:
        try:
            city = state.cities[args[0]]
        except KeyError:
            print('Action failed: Nonexistent city specified.')
            return
    else:
        print('Action failed: Incorrect number of arguments.')
        return

    print(f'The neighbors of {city.display()} are:')
    for neighbor in city.neighbors.values():
        print(f'{indent}{neighbor.display()}')


def print_status(state, *args):
    """Display the current state of the game.

    syntax: status [player_discard|infection_discard]
    """
    if len(args) == 0:
        print()
        print(f'-------------------- TURN {state.turn_count} --------------------')

        disease_track = state.disease_track
        for color in disease_track.colors:
            header = f'{style(color.upper(), color=color)} '
            header += f'-- {disease_track.statuses[color].name.upper()}'
            print(header)
            line = disease_track.cubes[color] * '▪'
            line = ' '.join([line[i : i + 5] for i in range(0, len(line), 5)])
            print(f'{indent}{style(line, color=color)}')
        print()

        for player_name in state.player_order:
            player = state.players[player_name]
            print(f'{style(player.name.upper(), color=player.color)} -- {player.role.upper()}')
            player.print_status(indent)
        print()

        for city in state.cities.values():
            has_piece = city.station or any(city.cubes.values()) or city.players
            if not has_piece:
                continue
            header = style(city.name.upper(), color=city.color)
            if city.station:
                header += ' ⌂'
            print(header)
            for color, cubes in city.cubes.items():
                if cubes > 0:
                    print(f'{indent}{style(cubes * '▪', color=color)}')
            for player_name, player in city.players.items():
                print(f'{indent}{style('▲', color=player.color)} {player_name}')
        print()

        track_prefix = 'Infection rate: '
        track_string = '--'.join([str(value) for value in state.infection_track.track])
        print(track_prefix + track_string)
        print((len(track_prefix) + 3 * state.infection_track.position) * ' ' + '^')
        print()

        track_prefix = 'Outbreaks: '
        track_string = '--'.join([str(value) for value in range(state.outbreak_track.max)]) + '--X'
        print(track_prefix + track_string)
        print((len(track_prefix) + 3 * state.outbreak_track.count) * ' ' + '^')
        print()

        card_string = len(state.player_deck.draw_pile) * '❘'
        card_string = ' '.join([card_string[i : i + 5] for i in range(0, len(card_string), 5)])
        print('Player deck:', card_string)
        print()

        print(f'Turn: {state.current_player.name}')
    elif len(args) == 1:
        if args[0] == 'player_discard':
            print('PLAYER DISCARD')
            for card in state.player_deck.discard_pile:
                print(f'{indent}{card.display()}')
        elif args[0] == 'infection_discard':
            print('INFECTION DISCARD')
            for card in state.infection_deck.discard_pile:
                print(f'{indent}{card.display()}')
        else:
            print(f'Action failed: Argument is not "player_discard" or "infection_discard."')
    else:
        print(f'Action failed: Incorrect number of arguments.')


# Flow control
def main():
    readline.parse_and_bind('tab: menu-complete')
    readline.set_completer(lambda x: None)

    args = argfuncs.parse_args(
        sys.argv[1:],
        constants.player_min_word,
        constants.player_max_word,
        constants.epidemic_min_word,
        constants.epidemic_max_word,
        constants.default_map,
        constants.start_city,
        constants.outbreak_max,
        constants.infection_seq,
        constants.cube_num,
        constants.station_num,
    )

    argfuncs.check_args(
        args,
        constants.player_min,
        constants.player_max,
        constants.player_min_word,
        constants.player_max_word,
        constants.epidemic_min,
        constants.epidemic_max,
        constants.epidemic_min_word,
        constants.epidemic_max_word,
    )

    argfuncs.dialog_args(
        args,
        constants.player_min,
        constants.player_max,
        constants.player_min_word,
        constants.player_max_word,
        constants.epidemic_min,
        constants.epidemic_max,
        constants.epidemic_min_word,
        constants.epidemic_max_word,
    )

    state = initialize_state(args)

    initialize_game(state, args)

    game_loop(state)


def initialize_state(args, role_map=None):
    # Count unique disease colors
    colors = set([attrs.color for attrs in args.map.values()])

    # Instantiate cities and associated cards
    cities = {}
    city_cards = []
    infection_cards = []
    for city_name, attrs in args.map.items():
        cities[city_name] = pieces.City(city_name, attrs.color, colors)
        city_cards.append(cards.CityCard(city_name, attrs.color, attrs.population))
        infection_cards.append(cards.Card('infection', city_name, attrs.color))
    for city_name, attrs in args.map.items():
        city = cities[city_name]
        neighbors = {neighbor_name: cities[neighbor_name] for neighbor_name in attrs.neighbors}
        city.neighbors = neighbors

    # Instantiate diseases
    disease_track = pieces.DiseaseTrack(colors, args.cube_num)

    # Instantiate players
    role_map = {} if role_map is None else role_map
    unassigned_players = list(set(args.player_names) - set(role_map.keys()))
    unassigned_roles = list(set(roles.roles) - set(role_map.values()))
    shuffle(unassigned_roles)

    players = {}
    for player_name, role_name in role_map.items():
        players[player_name] = roles.roles[role_name](player_name)
    for player_name in unassigned_players:
        role = unassigned_roles.pop()
        players[player_name] = roles.roles[role](player_name)
    player_order = args.player_names  # Use initial order of names until starting hand is dealt

    # Instantiate decks
    player_deck = cards.PlayerDeck(city_cards + cards.event_cards)
    infection_deck = cards.InfectionDeck(infection_cards)

    # Instantiate trackers
    outbreak_track = pieces.OutbreakTrack(args.outbreak_max)
    infection_track = pieces.InfectionTrack(args.infection_seq)

    # Combine all pieces, cards, and players into state
    state = GameState(
        cities,
        disease_track,
        players,
        player_order,
        player_deck,
        infection_deck,
        outbreak_track,
        infection_track,
        args.station_num,
        turn_count=0,
        draw_count=0,
        infect_count=0,
    )

    return state


def initialize_game(state, args):
    # Add research station to start city
    state.cities[args.start_city].add_station(state)

    # Infect cities
    for _ in range(3):
        for i in range(3, 0, -1):
            state.infection_deck.draw(state, i, verbose=False)

    # Set initial positions, hands, and order
    start_hand_num = 6 - args.player_num
    for player in state.players.values():
        player.set_city(state, state.cities[args.start_city])  # Set separately from instantiation so special abilities do not interfere with setup # fmt: skip
        starting_cards = [state.player_deck.draw() for _ in range(start_hand_num)]
        for card in starting_cards:
            player.add_card(state, card)
    state.player_order = get_player_order(args.player_names, state.players)

    # Add epidemics to deck
    state.player_deck.add_epidemics(args.epidemic_num)


def get_player_order(player_names, players):
    max_pop = 0
    max_card = ''
    max_player = ''
    for name in player_names:
        player = players[name]
        for card in player.hand.values():
            if isinstance(card, cards.CityCard) and card.population > max_pop:
                max_pop = card.population
                max_card = card
                max_player = player.name
    idx = player_names.index(max_player)
    print()
    print(
        f'{max_player} has the card with the highest population: '
        f'{max_card.display()} ({max_pop:,})'
    )
    print(f'{max_player} will start the turn order.')
    return player_names[idx:] + player_names[:idx]


def game_loop(state):
    while True:
        # Turn setup
        state.draw_count = 2
        state.infect_count = state.infection_track.rate
        sleep(1)
        print_status(state)

        # Player actions
        print()
        while state.current_player.action_count > 0:
            commands = {
                **state.current_player.actions,
                'neighbors': print_neighbors,
                'event': play_event,
                'status': print_status,
                'quit': quit,
            }
            prompt = (
                f'{prompt_prefix}Enter your next command '
                f'({state.current_player.action_count} action(s) remaining): '
            )
            interface(state, commands, prompt)

        # Draw cards
        print()
        while state.draw_count > 0:
            commands = {
                'draw': draw_player,
                'event': play_event,
                'status': print_status,
                'quit': quit,
            }
            prompt = (
                f'{prompt_prefix}Draw or play event card '
                f'({state.draw_count} draw(s) remaining): '
            )
            interface(state, commands, prompt)
            state.outbreak_track.reset()  # Reset outbreak after each draw

        # Infect cities
        print()
        while state.infect_count > 0:
            commands = {
                'infect': draw_infect,
                'event': play_event,
                'status': print_status,
                'quit': quit,
            }
            prompt = (
                f'{prompt_prefix}Infect or play event card '
                f'({state.infect_count} infect(s) remaining): '
            )
            interface(state, commands, prompt)
            state.outbreak_track.reset()  # Reset outbreak after each draw

        # Turn cleanup
        state.current_player.reset()
        state.turn_count += 1


def epidemic(state):
    # Increase
    state.infection_track.increment()

    # Infect
    state.infection_deck.infect(state)

    # Play Resilient Population event if available
    # This isn't the most flexible approach, but Resilient Population is the only game element that
    # has this behavior, so it's okay as a one-off. An event model where epidemic listeners
    # register with an Epidemic object would generalize this code if multiple game elements needed
    # to react to different parts of an epidemic.
    for player in state.players.values():
        if player.has_event('resilient_population'):
            text = input(
                f'{prompt_prefix}Resilient Population event card detected in hand. '
                f'Play now? (y/n) '
            ).lower()
            if text == 'y' or text == 'yes':
                player.event(state, 'resilient_population')

    # Intensify
    state.infection_deck.intensify()


# Interface
def make_completer(commands):
    def completer(text, state):
        args = readline.get_line_buffer().split()
        if len(args) == 0:
            matches = [command for command in commands if command.startswith(text)]
        else:
            matches = []
        if state < len(matches):
            return matches[state]
        else:
            return None

    return completer


def interface(state, commands, prompt):
    completer = make_completer(commands)
    readline.set_completer(completer)

    args = input(prompt).lower().strip().split()
    if len(args) == 0:
        return
    command = args[0]
    args = args[1:]
    if command == 'help':
        help(commands, *args)
    else:
        try:
            cmd = commands[command]
        except KeyError:
            print('No currently available command exists with that name. Please try again.')
            return
        cmd(state, *args)

    readline.set_completer(lambda x: None)


def help(commands, *args):
    """Display available commands or syntax for a specific command.

    syntax: help [COMMAND]
    """
    commands = commands.copy()
    commands['help'] = help
    if len(args) == 0:
        print(f'The available commands are: ')
        for command, cmd in commands.items():
            docstring = cmd.__doc__ if cmd.__doc__ else 'NO HELP FOUND'
            docstring = cleandoc(docstring)
            summary = docstring.split('\n')[0]
            print(f'{indent}{command}: {summary}')
    elif len(args) == 1:
        command = args[0]
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
