"""Definitions of game pieces."""

from enum import Enum, auto

import pydemic.exceptions as exceptions
from pydemic.display import style


class City:
    def __init__(self, name, color, colors, cube_max=3):
        self.color = color
        self.cubes = {color: 0 for color in colors}
        self.cube_max = cube_max
        self.name = name
        self.neighbors = {}
        self.players = {}
        self.station = False

    def add_disease(self, state, color, n=1, verbose=True):
        if self.immunity(state, color):
            raise exceptions.PropertyError(f'{self.display()} is immune.')

        delta = min(n, self.cube_max - self.cubes[color])
        state.disease_track.remove(color, delta)
        self.cubes[color] += delta
        if verbose:
            if delta == 0:
                msg = (
                    f'{self.display()} was infected '
                    f'with {self.display()}, but no cubes were added.'
                )
            else:
                msg = f'{self.display()} was infected with {delta} {style(color, color=color)}.'
            print(msg)
        if n > delta:
            self.outbreak(state, color)

    def outbreak(self, state, color):
        if (self.name, color) not in state.outbreak_track.resolved:
            print(f'{self.display()} outbroke!')
            state.outbreak_track.resolved.add(
                (self.name, color)
            )  # Append to resolve first to prevent infinite loop between adjacent cities
            state.outbreak_track.increment()
            for neighbor in self.neighbors.values():
                try:
                    neighbor.add_disease(state, color)
                except exceptions.PropertyError:  # Catch immunity errors but print nothing
                    pass

    def remove_disease(self, state, color):
        if self.cubes[color] == 0:
            raise exceptions.PropertyError(
                f'{self.display()} is not infected with {style(color, color=color)}.'
            )

        if state.disease_track.is_cured(color):
            n = self.cubes[color]
            self.cubes[color] -= n
            state.disease_track.add(color, n)
        else:
            self.cubes[color] -= 1
            state.disease_track.add(color, 1)

    def add_station(self, state):
        if self.station:
            raise exceptions.StationAddError(f'{self.display()} has a research station.')
        elif state.station_count < 1:
            raise exceptions.StationAddError('No research stations are available.')
        else:
            state.station_count -= 1
            self.station = True

    def remove_station(self, state):
        if not self.station:
            raise exceptions.StationRemoveError(
                f'{self.display()} does not have a research station.'
            )
        else:
            self.station = False
            state.station_count += 1

    def immunity(self, state, color):
        for player in state.players.values():
            if player.immunity(state, self, color):
                return True
        return False

    def display(self):
        return style(self.name, color=self.color)


class DiseaseState(Enum):
    ACTIVE = auto()
    CURED = auto()
    ERADICATED = auto()


class DiseaseTrack:
    def __init__(self, colors, cube_num=24):
        self.colors = sorted(set(colors))
        self.cubes = {color: cube_num for color in colors}
        self.statuses = {color: DiseaseState.ACTIVE for color in colors}
        self.cube_num = cube_num

    def add(self, color, n=1):
        self.cubes[color] += n
        if self.is_cured(color) and self.cubes[color] == self.cube_num:
            self.statuses[color] = DiseaseState.ERADICATED

    def remove(self, color, n=1):
        if self.statuses[color] is DiseaseState.ERADICATED:
            raise exceptions.PropertyError(f'{style(color, color=color)} is eradicated.')

        if self.cubes[color] >= n:
            self.cubes[color] -= n
        else:
            raise exceptions.GameOverLose(
                f'The disease track ran out of {style(color, color=color)} cubes.'
            )

    def set_cured(self, color):
        if not self.is_active(color):
            raise exceptions.PropertyError(f'{style(color, color=color)} already cured.')

        if self.cubes[color] == self.cube_num:
            self.statuses[color] = DiseaseState.ERADICATED
        else:
            self.statuses[color] = DiseaseState.CURED

        if all([status is not DiseaseState.ACTIVE for status in self.statuses]):
            raise exceptions.GameOverWin

    def is_active(self, color):
        return self.statuses[color] is DiseaseState.ACTIVE

    def is_cured(self, color):
        return self.statuses[color] is DiseaseState.CURED

    def is_eradicated(self, color):
        return self.statuses[color] is DiseaseState.ERADICATED


class OutbreakTrack:
    def __init__(self, max=8):
        self.count = 0
        self.max = max
        self.resolved = set()

    def increment(self):
        self.count += 1
        if self.count == self.max:
            raise exceptions.GameOverLose('The outbreak track reached its max.')

    def reset(self):
        self.resolved.clear()


class InfectionTrack:
    def __init__(self, track):
        self.position = 0
        self.track = track
        self.rate = self.track[self.position]

    def increment(self):
        self.position += 1
        self.rate = self.track[self.position]
