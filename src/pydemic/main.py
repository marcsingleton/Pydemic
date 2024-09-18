"""A text-based implementation of the board game Pandemic."""

from random import shuffle
from time import sleep

import pydemic.cards as cards
import pydemic.maps as maps
import pydemic.pieces as pieces
import pydemic.roles as roles
import pydemic.shared as shared
from pydemic.format import as_color, cards_to_string, indent
from pydemic.version import __version__


# FUNCTIONS
# Generic actions
def draw_infect(*args):
    """Draw a card from the infection deck.

    syntax: draw
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
        current_player.add_card(card)


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


def print_neighbors(*args):
    """Display the neighbors of a given city.
    
    If the CITY argument is omitted, the city of the current player is used.
    
    syntax: neighbors [CITY]
    """
    if len(args) == 0:
        city = shared.cities[current_player.city]
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
    print()
    print(f'-------------------- TURN {turn_count} --------------------')

    for disease in shared.diseases.values():
        print(as_color(disease.color.upper(), disease.color))
        print(f'{indent}Status:', disease.status.name.lower())
        print(f'{indent}Cubes remaining:', disease.cubes)
    print()

    for player in shared.players.values():
        print(player.name.upper(), f'({player.role.upper()})')
        print(f'{indent}Location:', as_color(player.city, shared.cities[player.city].color))
        print(f'{indent}Hand:', cards_to_string(player.hand.values()))
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

    print(f'Turn: {current_player.name}')


# Flow control
def main():
    # INITIALIZATION
    # Print greeting
    print(f'Welcome to Pydemic {__version__}! Are you ready to save humanity?')
    print()

    # Get player settings
    player_num = None
    while not player_num:
        text = input('Enter a number between two and four for the number of players: ')
        try:
            value = int(text)
        except ValueError:
            print(f'{text} is not a valid number. Please try again.')
            continue
        if value < 2 or value > 4:
            print('The number of players must be between two and four. Please try again.')
            continue
        player_num = value
    player_names = []
    for i in range(1, player_num + 1):
        text = input(f"Enter player {i}'s name: ")
        player_names.append(text)
    start_hand_num = 6 - player_num
    print()

    # Get epidemic settings
    epidemic_num = None
    while not epidemic_num:
        text = input('Enter a number between four and six for the number of epidemics in play: ')
        try:
            value = int(text)
        except ValueError:
            print(f'{text} is not a valid number. Please try again.')
            continue
        if value < 2 or value > 4:
            print('The number of epidemics must be between four and six. Please try again.')
            continue
        epidemic_num = value
    print()

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
    pieces.City.stations = station_num
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
    turn_count = 0
    player_names = turn_order(player_names)
    for player in shared.players.values():
        player.city = start_city  # Set separately from instantiation so special abilities do not interfere with setup

    # PLAY
    while True:
        # Turn setup
        turn = turn_count % player_num
        current_player = shared.players[player_names[turn]]
        shared.draw_count = 2
        shared.infect_count = shared.infection_track.rate
        sleep(1)
        print_status()

        # Player actions
        print()
        while current_player.action_count > 0:
            commands = {
                **current_player.actions,
                'neighbors': print_neighbors,
                'event': play_event,
                'status': print_status,
            }
            prompt = (
                f'Enter your next command ({current_player.action_count} action(s) remaining): '
            )
            interface(commands, prompt)

        # Draw cards
        print()
        while shared.draw_count > 0:
            commands = {
                'draw': draw_player,
                'event': play_event,
                'status': print_status,
            }
            prompt = f'Draw or play event card ({shared.draw_count} draw(s) remaining): '
            interface(commands, prompt)
            shared.outbreak_track.reset()  # Reset outbreak after each draw

        # Infect cities
        print()
        while shared.infect_count > 0:
            commands = {
                'infect': draw_infect,
                'event': play_event,
                'status': print_status,
            }
            prompt = f'Infect or play event card ({shared.infect_count} infect(s) remaining): '
            interface(commands, prompt)
            shared.outbreak_track.reset()  # Reset outbreak after each draw

        # Turn cleanup
        current_player.reset()
        turn_count += 1


def interface(commands, prompt):
    args = input(prompt).lower().split()
    if len(args) == 0:
        return
    command = args[0]
    if command == 'help':
        print(f'The available commands are: ')
        for command in commands:
            print(f'{indent}{command}')
        return
    try:
        cmd = commands[command]
    except KeyError:
        print('No valid command exists with that name. Try again.')
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
                'Resilient Population event card detected in hand. Play now? (y/n) '
            ).lower()
            if text == 'y' or text == 'yes':
                player.hand['resilient_population'].event()
                player.discard('resilient_population')

    # Intensify
    shared.infection_deck.intensify()


# SETTINGS
# Advanced game settings
map = maps.default
start_city = 'atlanta'
outbreak_max = 8
infection_seq = [2, 2, 2, 3, 3, 4, 4]
cube_num = 24
station_num = 6
