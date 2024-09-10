"""Definitions of player roles."""

import exceptions
import shared

from format import as_underline, indent


class Player:
    def __init__(self, name, role, hand_max=7):
        self.actions = {'ground': self.ground, 'direct': self.direct, 'charter': self.charter, 'shuttle': self.shuttle,
                        'station': self.station, 'treat': self.treat, 'share': self.share, 'cure': self.cure,
                        'pass': self.no_action}
        self.action_num = 4
        self.action_count = self.action_num
        self._city = None
        self.cure_num = 5
        self.hand = {}
        self.hand_max = hand_max
        self.name = name
        self.role = role

    # Property functions
    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, dest):
        if self._city is not None:  # Do not attempt to set parameters for newly instantiated players
            shared.cities[self.city].players.remove(self.name)  # TODO: Mediator

        self._city = dest
        if dest is not None:  # Do not attempt to set parameters while instantiating players
            shared.cities[dest].players.add(self.name)

    # Utility functions
    def add_card(self, card):
        self.hand[card.name] = card
        if len(self.hand) > self.hand_max:
            underlined_card = as_underline('card')
            print()
            print(f'{self.name} has exceeded the hand limit. Please discard a card or play an event card.')
            print(f'{indent}To discard a card, use "discard {underlined_card}".')
            print(f'{indent}To play an event card, use "event {underlined_card}".')
        while len(self.hand) > self.hand_max:
            args = input('Enter your command: ').split()
            if len(args) == 2 and args[0] == 'discard':
                try:
                    self.discard(args[1])
                except exceptions.DiscardError as error:
                    print('Discard failed:', error)
            elif len(args) == 2 and args[0] == 'event':
                try:
                    self.event(args[1])
                except exceptions.EventError as error:
                    print('Event failed:', error)
            else:
                print('Command failed: Incorrect number or form of arguments.')

    def can_share(self, card):
        if card not in self.hand:
            return False, 'Action failed: Player does not have the specified card.'
        if card != self.city:
            return False, "Action failed: Specified card does not match player's current city."
        return True, 'Action succeeded!'

    def discard(self, card):
        try:
            shared.player_deck.discard(self.hand.pop(card))
        except KeyError:
            raise exceptions.DiscardError(f'{card} is not in hand.')

    def immunity(self, city, color):
        return False

    def reset(self):
        self.action_count = self.action_num

    # Player actions
    def ground(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return
        if args[0] not in shared.cities[self.city].neighbors:
            print('Action failed: Destination not within one move.')
            return

        self.city = args[0]
        self.action_count -= 1
        print('Action succeeded!')

    def direct(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        try:
            self.discard(args[0])
        except exceptions.DiscardError as error:
            print('Action failed:', error)
        else:
            self.city = args[0]
            self.action_count -= 1
            print('Action succeeded!')

    def charter(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        try:
            self.discard(self.city)
        except exceptions.DiscardError as error:
            print('Action failed:', error)
        else:
            self.city = args[0]
            self.action_count -= 1
            print('Action succeeded!')

    def shuttle(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        if not shared.cities[self.city].station:
            print('Action failed: Current city does not have research station.')
        elif not shared.cities[args[0]].station:
            print('Action failed: Destination city does not have research station.')
        else:
            self.city = args[0]
            self.action_count -= 1
            print('Action succeeded!')

    def station(self, *args):
        if len(args) == 0:
            try:
                self.discard(self.city)
                shared.cities[self.city].add_station()
            except exceptions.DiscardError as error:
                print('Action failed:', error)
            except exceptions.StationAddError as error:
                self.add_card(shared.player_deck.discard.pop())
                print('Action failed:', error)
            else:
                self.action_count -= 1
                print('Action succeeded!')
        elif len(args) == 1:
            if args[0] not in shared.cities:
                print('Action failed: Nonexistent city specified.')
                return
            try:
                self.discard(self.city)
                shared.cities[args[0]].remove_station()
                shared.cities[self.city].add_station()
            except exceptions.DiscardError as error:
                print('Action failed:', error)
            except exceptions.StationRemoveError as error:
                self.add_card(shared.player_deck.discard.pop())
                print('Action failed:', error)
            except exceptions.StationAddError as error:
                self.add_card(shared.player_deck.discard.pop())
                shared.cities[args[0]].add_station()
                print('Action failed:', error)
            else:
                self.action_count -= 1
                print('Action succeeded!')
        else:
            print('Action failed: Incorrect number of arguments.')

    def treat(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.diseases:
            print('Action failed: Nonexistent disease specified.')
            return

        city = shared.cities[self.city]
        try:
            city.remove_disease(args[0])
        except exceptions.PropertyError as error:
            print('Action failed:', error)
        else:
            self.action_count -= 1
            print('Action succeeded!')

    def share(self, *args):
        if len(args) != 2:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.players:
            print('Action failed: Nonexistent player specified.')
            return
        if shared.players[args[0]].city != self.city:
            print('Action failed: Target player not in same city.')
            return
        target = shared.players[args[0]]
        card = args[1]
        if card in self.hand:
            giver, receiver = self, target
        elif card in target.hand:
            giver, receiver = target, self
        else:
            print('Action failed: Neither player has the specified card.')
        can_share, msg = giver.can_share(card)
        if can_share:
            receiver.add_card(giver.hand.pop(card))
            self.action_count -= 1
            print(msg)
        else:
            print(msg)

    def cure(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.diseases:
            print('Action failed: Nonexistent disease specified.')
            return
        if not shared.cities[self.city].station:
            print('Action failed: Not in city with research station.')
            return

        cards = [card.name for card in self.hand.values() if card.color == args[0]]
        if len(cards) < self.cure_num:
            print('Action failed: Insufficient cards.')
            return
        while len(cards) > self.cure_num:
            items = input(f'Extra {args[0]} cards detected. Please select {len(cards) - self.cure_num} cards to keep.'
                          f'(Separate items with a space.)').split()
            for item in items:
                try:
                    cards.remove(item)
                except ValueError:
                    print('Card not found.')

        try:
            shared.diseases[args[0]].set_cured()
        except exceptions.PropertyError as error:
            print('Action failed:', error)
        else:
            for card in cards:
                self.discard(card)
            self.action_count -= 1
            print('Action succeeded!')

    def event(self, *args):
        if len(args) != 1:
            print('Event failed: Incorrect number of arguments.')
            return
        if args[0] not in self.hand:
            print('Event failed: Player does not have specified card.')
            return
        card = self.hand[args[0]]
        try:
            card.event()
        except exceptions.EventError as error:
            print('Event failed:', error)
        else:
            self.discard(args[0])
            print('Event succeeded!')

    def no_action(self, *args):
        self.action_count -= 1
        print('Action succeeded!')


class ContingencyPlanner(Player):
    def __init__(self, name):
        super().__init__(name, 'contingency planner')
        self.actions = {**self.actions, 'contingency': self.contingency}
        self.contingency_card = None

    def contingency(self, *args):  # TODO: Add behavior for playing card
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if self.contingency_card is not None:
            print('Action failed: Contingency card is occupied.')
            return

        try:
            self.contingency_card = shared.player_deck.retrieve(args[0])
        except exceptions.PropertyError:
            print('Action failed: Event card not in discard pile.')
        else:
            self.action_count -= 1
            print('Action succeeded!')


class Dispatcher(Player):
    def __init__(self, name):
        super().__init__(name, 'dispatcher')
        self.actions = {**self.actions, 'airlift': self.airlift,
                        'ground': self.make_parse('ground'), 'direct': self.make_parse('direct'),
                        'charter': self.make_parse('charter'), 'shuttle': self.make_parse('shuttle')}

    def airlift(self, args):
        if len(args) != 2:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.players or args[1] not in shared.players:
            print('Action failed: Nonexistent player specified.')
            return

        shared.players[args[0]].city = shared.players[args[1]].city

    def ground_dispatch(self, args, target):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return
        if args[0] not in shared.cities[target.city].neighbors:
            print('Action failed: Destination not within one move.')
            return

        target.city = args[0]
        self.action_count -= 1
        print('Action succeeded!')

    def direct_dispatch(self, args, target):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        try:
            self.discard(args[0])
        except exceptions.DiscardError as error:
            print('Action failed:', error)
        else:
            target.city = args[0]
            self.action_count -= 1
            print('Action succeeded!')

    def charter_dispatch(self, args, target):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        try:
            self.discard(self.city)
        except exceptions.DiscardError as error:
            print('Action failed:', error)
        else:
            target.city = args[0]
            self.action_count -= 1
            print('Action succeeded!')

    def shuttle_dispatch(self, args, target):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        if not shared.cities[target.city].station:
            print('Action failed: Current city does not have research station.')
        elif not shared.cities[args[0]].station:
            print('Action failed: Destination city does not have research station.')
        else:
            target.city = args[0]
            self.action_count -= 1
            print('Action succeeded!')

    def make_parse(self, action):
        def f(args):
            return self.parse(args, action)
        return f

    def parse(self, args, action):
        if args[-1] in shared.players:
            key = action + '_dispatch'
            self.__getattribute__(key)(args[:-1], shared.players[args[-1]])
        else:
            key = action
            self.__getattribute__(key)(args)


class Medic(Player):
    def __init__(self, name):
        super().__init__(name, 'medic')

    @property
    def city(self):  # Needed to redefine for subclassing the setter
        return super().city

    @city.setter
    def city(self, dest):
        if self._city is not None:  # Do not attempt to set parameters for newly instantiated players
            shared.cities[self.city].players.remove(self.name)

        self._city = dest
        if dest is not None:  # Do not attempt to set parameters while instantiating players
            shared.cities[dest].players.add(self.name)
            for disease in shared.diseases.values():
                if not disease.is_active():
                    try:
                        shared.cities[dest].remove_disease(disease.color)
                    except exceptions.PropertyError:
                        pass

    def immunity(self, city, color):
        if city == self.city and not shared.diseases[color].is_active():
            return True
        else:
            return False

    def treat(self, *args):
        if len(args) != 1:
            print('Action failed: Incorrect number of arguments.')
            return
        if args[0] not in shared.diseases:
            print('Action failed: Nonexistent disease specified.')
            return

        city = shared.cities[self.city]
        try:
            if city.cubes[args[0]] == 0:
                raise exceptions.PropertyError(f'{city.name} is not infected with {args[0]}.')
            for _ in range(city.cubes[args[0]]):
                city.remove_disease(args[0])
        except exceptions.PropertyError as error:
            print('Action failed:', error)
        else:
            self.action_count -= 1
            print('Action succeeded!')


class OperationsExpert(Player):
    def __init__(self, name):
        super().__init__(name, 'operations expert')
        self.actions = {**self.actions, 'opex_shuttle': self.opex_shuttle, 'station': self.station}
        self.shuttle = False

    def reset(self):
        super().reset()
        self.shuttle = False

    def opex_shuttle(self, *args):
        if self.shuttle:
            print('Action failed: Special move already used this turn.')
            return
        if len(args) != 2:
            print('Action failed: Incorrect number of arguments.')
            return
        if not shared.cities[self.city].station:
            print('Action failed: Current city does not have research station.')
            return
        if args[0] not in shared.cities:
            print('Action failed: Nonexistent city specified.')
            return

        try:
            self.discard(args[1])
        except exceptions.DiscardError as error:
            print('Action failed:', error)
        else:
            self.action_count -= 1
            self.shuttle = True
            print('Action succeeded!')

    def station(self, *args):
        if len(args) == 0:
            try:
                shared.cities[self.city].add_station()
            except exceptions.StationAddError as error:
                print('Action failed:', error)
            else:
                self.action_count -= 1
                print('Action succeeded!')
        elif len(args) == 1:
            if args[0] not in shared.cities:
                print('Action failed: Nonexistent city specified.')
                return
            try:
                shared.cities[args[0]].remove_station()
                shared.cities[self.city].add_station()
            except exceptions.StationRemoveError as error:
                print('Action failed:', error)
            except exceptions.StationAddError as error:
                shared.cities[args[0]].add_station()
                print('Action failed:', error)
            else:
                self.action_count -= 1
                print('Action succeeded!')
        else:
            print('Action failed: Incorrect number of arguments.')


class QuarantineSpecialist(Player):
    def __init__(self, name):
        super().__init__(name, 'quarantine specialist')

    def immunity(self, city, color):
        if self.city and (city == self.city or city in shared.cities[self.city].neighbors):  # Check city is set to avoid KeyError during initialization
            return True
        else:
            return False


class Researcher(Player):
    def __init__(self, name):
        super().__init__(name, 'researcher')
    
    def can_share(self, card):
        if card not in self.hand:
            return False, 'Action failed: Player does not have the specified card.'
        return True, 'Action succeeded!'


class Scientist(Player):
    def __init__(self, name):
        super().__init__(name, 'scientist')
        self.cure_num = 4


roles = {'contingency planner': ContingencyPlanner,
         'dispatcher': Dispatcher,
         'medic': Medic,
         'operations expert': OperationsExpert,
         'quarantine specialist': QuarantineSpecialist,
         'researcher': Researcher,
         'scientist': Scientist}
