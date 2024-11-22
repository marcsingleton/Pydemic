"""Tests for pieces."""

from itertools import chain

import pytest

import pydemic.exceptions as exceptions
from .utils import default_init


def test_add_disease_simple():
    state = default_init()
    city = state.cities['atlanta']
    color = 'blue'
    track_cube_num = state.disease_track.cubes[color]
    city.add_disease(state, color, 1)
    assert city.cubes[color] == 1
    assert state.disease_track.cubes[color] == track_cube_num - 1


def test_add_disease_outbreak():
    state = default_init()
    city = state.cities['atlanta']
    color = 'blue'
    city.add_disease(state, color, city.cube_max)
    track_cube_num = state.disease_track.cubes[color]
    city.add_disease(state, color, 1)
    assert city.cubes[color] == city.cube_max
    for neighbor in city.neighbors.values():
        assert neighbor.cubes[color] == 1
    assert state.disease_track.cubes[color] == track_cube_num - len(city.neighbors)
    assert state.outbreak_track.count == 1


def test_add_disease_chain_outbreak():
    state = default_init()
    city_1 = state.cities['atlanta']
    city_2 = state.cities['washington']
    color = 'blue'
    city_1.add_disease(state, color, city_1.cube_max)
    city_2.add_disease(state, color, city_2.cube_max)
    track_cube_num = state.disease_track.cubes[color]
    city_1.add_disease(state, color, 1)
    assert city_1.cubes[color] == city_1.cube_max
    assert city_2.cubes[color] == city_2.cube_max
    shared_neighbors = set(city_1.neighbors) & set(city_2.neighbors)
    unique_neighbors_1 = set(city_1.neighbors) - set(city_2.neighbors) - set([city_2.name])
    unique_neighbors_2 = set(city_2.neighbors) - set(city_1.neighbors) - set([city_1.name])
    for neighbor_name in shared_neighbors:
        assert state.cities[neighbor_name].cubes[color] == 2
    for neighbor_name in chain(unique_neighbors_1, unique_neighbors_2):
        assert state.cities[neighbor_name].cubes[color] == 1
    additional_cubes = 2 * len(shared_neighbors) + len(unique_neighbors_1) + len(unique_neighbors_2)
    assert state.disease_track.cubes[color] == track_cube_num - additional_cubes
    assert state.outbreak_track.count == 2


def test_add_disease_game_over_lose():
    state = default_init()
    city = state.cities['atlanta']
    color = 'blue'
    state.disease_track.cubes[color] = 0
    with pytest.raises(exceptions.GameOverLose):
        city.add_disease(state, color, 1)


def test_add_disease_immune():
    state = default_init(role_map={'A': 'quarantine specialist'})
    city = state.cities['atlanta']
    player = state.players['A']
    color = 'blue'
    player.set_city(state, city)
    track_cube_num = state.disease_track.cubes[color]
    with pytest.raises(exceptions.PropertyError):
        city.add_disease(state, color, 1)
    assert city.cubes[color] == 0
    assert state.disease_track.cubes[color] == track_cube_num


def test_add_station_to_city_without():
    state = default_init()
    city = state.cities['atlanta']
    station_count = state.station_count
    city.add_station(state)
    assert city.station
    assert state.station_count == station_count - 1


def test_add_station_to_city_with():
    state = default_init()
    city = state.cities['atlanta']
    city.add_station(state)
    station_count = state.station_count
    with pytest.raises(exceptions.StationAddError):
        city.add_station(state)
    assert city.station
    assert state.station_count == station_count


def test_add_station_with_none_available():
    state = default_init()
    city = state.cities['atlanta']
    state.station_count = 0
    with pytest.raises(exceptions.StationAddError):
        city.add_station(state)
    assert not city.station
    assert state.station_count == 0


def test_remove_station_from_city_with():
    state = default_init()
    city = state.cities['atlanta']
    city.add_station(state)
    station_count = state.station_count
    city.remove_station(state)
    assert not city.station
    assert state.station_count == station_count + 1


def test_remove_station_from_city_without():
    state = default_init()
    city = state.cities['atlanta']
    station_count = state.station_count
    with pytest.raises(exceptions.StationRemoveError):
        city.remove_station(state)
    assert not city.station
    assert state.station_count == station_count
