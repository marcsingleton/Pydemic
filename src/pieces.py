"""Definitions of game pieces."""

import exceptions
import shared


class City:
    stations = None

    def __init__(self, name, neighbors, color, colors, cube_max=3):
        self.color = color
        self.cubes = {color: 0 for color in colors}
        self.cube_max = cube_max
        self.name = name
        self.neighbors = neighbors
        self.players = set()
        self.station = False

    def add_disease(self, color, n=1, verbose=True):
        if self.immunity(color):
            raise exceptions.PropertyError(f'{self.name} is immune.')

        delta = min(n, self.cube_max - self.cubes[color])
        shared.diseases[color].remove(delta)
        self.cubes[color] += delta
        if verbose:
            print(f'{self.name} was infected with {color}.')
        if n > delta:
            self.outbreak(color)

    def outbreak(self, color):
        if (self.name, color) not in shared.outbreak_track.resolved:
            print(f'{self.name} outbroke!')
            shared.outbreak_track.resolved.add((self.name, color))  # Append to resolved first to prevent infinite loop between adjacent cities
            shared.outbreak_track.increment()
            for neighbor in self.neighbors:
                neighbor = shared.cities[neighbor]
                try:
                    neighbor.add_disease(color)
                except exceptions.PropertyError:  # Catch immunity errors but print nothing
                    pass

    def remove_disease(self, color):
        if self.cubes[color] == 0:
            raise exceptions.PropertyError(f'{self.name} is not infected with {color}.')

        if shared.diseases[color].status == 'cured':
            n = self.cubes[color]
            self.cubes[color] -= n
            shared.diseases[color].add(n)
        else:
            self.cubes[color] -= 1
            shared.diseases[color].add(1)

    def add_station(self):
        if self.station:
            raise exceptions.StationAddError(f'{self.name} has a research station.')
        elif City.stations < 1:
            raise exceptions.StationAddError('No research stations are available.')
        else:
            City.stations -= 1
            self.station = True

    def remove_station(self):
        if not self.station:
            raise exceptions.StationRemoveError(f'{self.name} does not have a research station.')
        else:
            self.station = False
            City.stations += 1

    def immunity(self, color):
        for player in shared.players.values():
            if player.immunity(self.name, color):
                return True
        return False


class Disease:
    def __init__(self, color, cube_num=24):
        self.color = color
        self.cubes = cube_num
        self.status = 'active'  # active, cured, or eradicated
        self.cube_num = cube_num

    def add(self, n=1):
        self.cubes += n
        if self.status == 'cured' and self.cubes == self.cube_num:
            self.status = 'eradicated'

    def remove(self, n=1):
        if self.status == 'eradicated':
            raise exceptions.PropertyError(f'{self.color} is eradicated.')

        if self.cubes >= n:
            self.cubes -= n
        else:
            raise exceptions.GameOver(f'Depleted {self.color} disease cubes.')

    def set_cured(self):
        if self.status != 'active':
            raise exceptions.PropertyError(f'{self.color} already cured.')

        if self.cubes == self.cube_num:
            self.status = 'eradicated'
        else:
            self.status = 'cured'


class OutbreakTrack:
    def __init__(self, max=8):
        self.count = 0
        self.max = max
        self.resolved = set()

    def increment(self):
        self.count += 1
        if self.count == self.max:
            raise exceptions.GameOver('Maximum outbreaks reached.')

    def reset(self):
        self.resolved.clear()


class InfectionTrack:
    def __init__(self, track=[2, 2, 2, 3, 3, 4, 4]):
        self.pos = 0
        self.track = track
        self.rate = self.track[self.pos]

    def increment(self):
        self.pos += 1
        self.rate = self.track[self.pos]
