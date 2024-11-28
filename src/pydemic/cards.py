"""Definitions of card and deck objects."""

import abc
from random import shuffle

import pydemic.exceptions as exceptions
from pydemic.display import style, cards_to_string, indent, prompt_prefix


# Cards and Decks
class Card:
    def __init__(self, type, name=None, color=None):
        self.type = type
        self.name = name
        self.color = color

    def display(self):
        return style(self.name, color=self.color)


class CityCard(Card):
    def __init__(self, city_name, color, population):
        super().__init__('city', city_name, color)
        self.population = population


class EventCard(Card):
    def __init__(self, event_name, event_func):
        super().__init__('event', event_name, 'gold')
        self.event = event_func

    def display(self):
        return style(self.name, color=self.color, bold=True)


class Deck(abc.ABC):
    def __init__(self, cards):
        self.discard_pile = []
        self.draw_pile = cards

        shuffle(self.draw_pile)

    @abc.abstractmethod
    def draw(self):
        pass


class InfectionDeck(Deck):
    def draw(self, state, cubes=1, verbose=True):
        card = self.draw_pile.pop()
        city = state.cities[card.name]
        try:
            city.add_disease(state, card.color, cubes, verbose=verbose)
        except exceptions.PropertyError as error:
            print(
                f'{city.display()} was not infected '
                f'with {style(card.color, color=card.color)}:',
                error,
            )
        self.discard_pile.append(card)

    def infect(self, state):
        self.draw(state, cubes=3, idx=0)

    def intensify(self):
        shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []

    def remove(self, city_name):
        try:
            pop_by_name(self.discard_pile, city_name)
        except KeyError:
            raise exceptions.PropertyError('City not in discard pile.')


class PlayerDeck(Deck):
    def add_epidemics(self, epidemic_num):
        subdecks = [self.draw_pile[i::epidemic_num] for i in range(epidemic_num)]
        for deck in subdecks:
            deck.append(Card('epidemic', 'epidemic', 'lime'))
            shuffle(deck)
        self.draw_pile = [card for subdeck in subdecks for card in subdeck]

    def draw(self):
        try:
            return self.draw_pile.pop()
        except IndexError:
            raise exceptions.GameOverLose('The player deck ran out of cards.')

    def discard(self, card):
        self.discard_pile.append(card)

    def retrieve(self, card_name):
        try:
            card = pop_by_name(self.discard_pile, card_name)
        except KeyError:
            raise exceptions.PropertyError
        return card


def pop_by_name(pile, card_name):
    idx = False
    for i, card in enumerate(pile):
        if card.name == card_name:
            idx = i
            break
    if idx is not False:
        return pile.pop(idx)
    else:
        raise KeyError


# Events
def air_lift(state):
    args = input(f'{prompt_prefix}Enter a player and a destination city: ').split()
    if len(args) != 2:
        raise exceptions.EventError('Incorrect number of arguments.')
    if args[0] not in state.players:
        raise exceptions.EventError('Nonexistent player specified.')
    if args[1] not in state.cities:
        raise exceptions.EventError('Nonexistent city specified.')

    state.players[args[0]].set_city(state, state.cities[args[1]])


def forecast(state):
    top = state.infection_deck.draw_pile[:-7:-1]  # Reverse so pop order reads left to right
    bottom = state.infection_deck.draw_pile[:-6]

    print(cards_to_string(top))
    args = input(
        f'{prompt_prefix}'
        'Enter the re-ordered indices of the above cards, e.g. "135042" from top to bottom: '
    )
    if len(args) != 6:
        raise exceptions.EventError('Incorrect number of arguments.')
    if set([sym for sym in args]) != set(['0', '1', '2', '3', '4', '5']):
        raise exceptions.EventError('Incorrect form of arguments.')

    try:
        top = [top[int(i)] for i in args][::-1]  # Reverse so pop order is left to right
    except IndexError:
        raise exceptions.EventError('Missing card in arguments.')
    state.infection_deck.draw_pile = bottom + top


def government_grant(state):
    args = input(f'{prompt_prefix}Enter a city to place a research station: ').split()
    if len(args) == 1:
        if args[0] not in state.cities:
            raise exceptions.EventError('Nonexistent city specified.')
        try:
            state.cities[args[0]].add_station(state)
        except exceptions.StationAddError as error:
            raise exceptions.EventError(error)
    else:
        raise exceptions.EventError('Incorrect number of arguments.')


def one_quiet_night(state):
    state.infect_count = 0


def resilient_population(state):
    print('PLAYER DISCARD')
    for card in state.player_deck.discard_pile:
        print(f'{indent}{card.display()}')
    args = input(
        f'{prompt_prefix}Enter a city to remove from the infection deck discard pile: '
    ).split()
    if len(args) != 1:
        raise exceptions.EventError('Incorrect number of arguments.')
    if args[0] not in state.cities:
        raise exceptions.EventError('Nonexistent city specified.')

    try:
        state.infection_deck.remove(args[0])
    except exceptions.PropertyError as error:
        raise exceptions.EventError(error)


events = {
    'air_lift': air_lift,
    'forecast': forecast,
    'government_grant': government_grant,
    'one_quiet_night': one_quiet_night,
    'resilient_population': resilient_population,
}
event_cards = [EventCard(name, event) for name, event in events.items()]
