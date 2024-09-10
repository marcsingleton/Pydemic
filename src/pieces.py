"""Definitions of game pieces."""

from enum import Enum, auto

import exceptions
import shared
from format import as_color


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
            raise exceptions.PropertyError(f'{as_color(self.name, self.color)} is immune.')

        delta = min(n, self.cube_max - self.cubes[color])
        shared.diseases[color].remove(delta)
        self.cubes[color] += delta
        if verbose:
            print(f'{as_color(self.name, self.color)} was infected with {as_color(color, color)}.')
        if n > delta:
            self.outbreak(color)

    def outbreak(self, color):
        if (self.name, color) not in shared.outbreak_track.resolved:
            print(f'{as_color(self.name, self.color)} outbroke!')
            shared.outbreak_track.resolved.add((self.name, color))  # Append to resolve first to prevent infinite loop between adjacent cities
            shared.outbreak_track.increment()
            for neighbor in self.neighbors:
                neighbor = shared.cities[neighbor]
                try:
                    neighbor.add_disease(color)
                except exceptions.PropertyError:  # Catch immunity errors but print nothing
                    pass

    def remove_disease(self, color):
        if self.cubes[color] == 0:
            raise exceptions.PropertyError(f'{as_color(self.name, self.color)} is not infected with {as_color(color, color)}.')

        if shared.diseases[color].is_cured():
            n = self.cubes[color]
            self.cubes[color] -= n
            shared.diseases[color].add(n)
        else:
            self.cubes[color] -= 1
            shared.diseases[color].add(1)

    def add_station(self):
        if self.station:
            raise exceptions.StationAddError(f'{as_color(self.name, self.color)} has a research station.')
        elif type(self).stations < 1:
            raise exceptions.StationAddError('No research stations are available.')
        else:
            type(self).stations -= 1
            self.station = True

    def remove_station(self):
        if not self.station:
            raise exceptions.StationRemoveError(f'{as_color(self.name, self.color)} does not have a research station.')
        else:
            self.station = False
            type(self).stations += 1

    def immunity(self, color):
        for player in shared.players.values():
            if player.immunity(self.name, color):
                return True
        return False


class DiseaseState(Enum):
    ACTIVE = auto()
    CURED = auto()
    ERADICATED = auto()


class Disease:
    def __init__(self, color, cube_num=24):
        self.color = color
        self.cubes = cube_num
        self.status = DiseaseState.ACTIVE
        self.cube_num = cube_num

    def add(self, n=1):
        self.cubes += n
        if self.is_cured() and self.cubes == self.cube_num:
            self.status = DiseaseState.ERADICATED

    def remove(self, n=1):
        if self.status == DiseaseState.ERADICATED:
            raise exceptions.PropertyError(f'{as_color(self.color, self.color)} is eradicated.')

        if self.cubes >= n:
            self.cubes -= n
        else:
            raise exceptions.GameOver(f'Depleted {as_color(self.color, self.color)} disease cubes.')

    def set_cured(self):
        if not self.is_active():
            raise exceptions.PropertyError(f'{as_color(self.color, self.color)} already cured.')

        if self.cubes == self.cube_num:
            self.status = DiseaseState.ERADICATED
        else:
            self.status = DiseaseState.CURED
    
    def is_active(self):
        return self.status is DiseaseState.ACTIVE
    
    def is_cured(self):
        return self.status is DiseaseState.CURED
    
    def is_eradicated(self):
        return self.status is DiseaseState.ERADICATED


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
