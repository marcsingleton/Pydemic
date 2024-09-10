"""Definitions of card and deck objects."""

import abc
from random import shuffle

import exceptions
import shared
from format import as_color

class Card:
    def __init__(self, type):
        self.type = type
        self.color = None


class CityCard(Card):
    def __init__(self, city, color, population):
        super().__init__('city')
        self.color = color
        self.name = city
        self.population = population

    def __repr__(self):
        return as_color(self.name, self.color)


class EventCard(Card):
    def __init__(self, event_name, event_func):
        super().__init__('event')
        self.event = event_func
        self.name = event_name

    def __repr__(self):
        return as_color(self.name, 'white')


class InfectionCard(Card):
    def __init__(self, city, color):
        super().__init__('infection')
        self.color = color
        self.name = city

    def __repr__(self):
        return as_color(self.name, self.color)


class Deck(abc.ABC):
    def __init__(self, cards):
        self.discard_pile = []
        self.draw_pile = cards

        shuffle(self.draw_pile)

    @abc.abstractmethod
    def draw(self):
        pass


class InfectionDeck(Deck):
    def draw(self, cubes=1, idx=-1, verbose=True):
        card = self.draw_pile.pop(idx)
        city = shared.cities[card.name]
        try:
            city.add_disease(card.color, cubes, verbose=verbose)
        except exceptions.PropertyError as error:
            print(f'{card} was not infected with {as_color(card.color, card.color)}:', error)
        self.discard_pile.append(card)

    def infect(self):
        self.draw(cubes=3, idx=0)

    def intensify(self):
        shuffle(self.discard_pile)
        self.draw_pile += self.discard_pile
        self.discard_pile = []

    def remove(self, city):
        idx = False
        for i, card in enumerate(self.discard_pile):
            if card.name == city:
                idx = i
                break
        if idx is not False:
            del self.discard_pile[idx]
        else:
            raise exceptions.PropertyError('City not in discard pile.')


class PlayerDeck(Deck):
    def add_epidemics(self, epidemic_num):
        subdecks = [self.draw_pile[i::epidemic_num] for i in range(epidemic_num)]
        for deck in subdecks:
            deck.append(Card('epidemic'))
            shuffle(deck)
        self.draw_pile = [card for subdeck in subdecks for card in subdeck]

    def draw(self):
        try:
            return self.draw_pile.pop()
        except IndexError:
            raise exceptions.GameOver('Player deck depleted.')

    def discard(self, card):
        self.discard_pile.append(card)

    def retrieve(self, card_name):
        idx = False
        for i, card in enumerate(self.discard_pile):
            if card.name == card_name:
                idx = i
                break
        if idx is not False:
            self.discard_pile.pop(idx)
        else:
            raise exceptions.PropertyError


def air_lift():
    args = input('Enter a player and a destination city: ').split()
    if len(args) != 2:
        raise exceptions.EventError('Incorrect number of arguments.')
    if args[0] not in shared.players:
        raise exceptions.EventError('Nonexistent player specified.')
    if args[1] not in shared.cities:
        raise exceptions.EventError('Nonexistent city specified.')

    shared.players[args[0]].city = args[1]


def forecast():
    top = shared.infection_deck.draw_pile[:-7:-1]  # Reverse so pop order reads left to right
    bottom = shared.infection_deck.draw_pile[:-6]

    print(top)
    args = input('Enter the re-ordered indices of the above cards, e.g. "135042" from top to bottom: ')
    if len(args) != 6:
        raise exceptions.EventError('Incorrect number of arguments.')
    if set([sym for sym in args]) != set(['0', '1', '2', '3', '4', '5']):
        raise exceptions.EventError('Incorrect form of arguments.')

    try:
        top = [top[int(i)] for i in args][::-1]  # Reverse so pop order is left to right
    except IndexError:
        raise exceptions.EventError('Missing card in arguments.')
    shared.infection_deck.draw_pile = bottom + top


def government_grant():
    args = input('Enter one or two cities to place or transfer a research station, respectively: ').split()
    if len(args) == 1:
        if args[0] not in shared.cities:
            raise exceptions.EventError('Nonexistent city specified.')
        try:
            shared.cities[args[0]].add_station()
        except exceptions.StationAddError as error:
            raise exceptions.EventError(error)
    elif len(args) == 2:
        if args[0] not in shared.cities or args[1] not in shared.cities:
            raise exceptions.EventError('Nonexistent city specified.')
        try:
            shared.cities[args[0]].remove_station()
            shared.cities[args[1]].add_station()
        except exceptions.StationRemoveError as error:
            raise exceptions.EventError(error)
        except exceptions.StationAddError as error:
            shared.cities[args[0]].add_station()
            raise exceptions.EventError(error)
    else:
        raise exceptions.EventError('Incorrect number of arguments.')


def one_quiet_night():
    shared.infect_count = 0


def resilient_population():
    args = input('Enter a city to remove from the infection deck discard pile: ').split()
    if len(args) != 1:
        raise exceptions.EventError('Incorrect number of arguments.')
    if args[0] not in shared.cities:
        raise exceptions.EventError('Nonexistent city specified.')

    try:
        shared.infection_deck.remove(args[0])
    except exceptions.PropertyError as error:
        raise exceptions.EventError(error)


events = {'air_lift': air_lift,
          'forecast': forecast,
          'government_grant': government_grant,
          'one_quiet_night': one_quiet_night,
          'resilient_population': resilient_population}
event_cards = [EventCard(name, event) for name, event in events.items()]
