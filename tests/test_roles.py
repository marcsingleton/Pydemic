"""Tests for roles."""

from .utils import default_init


def test_ground_success():
    state = default_init()
    player = state.players['A']
    player.set_city(state, state.cities['atlanta'])
    action_count = player.action_count
    player.ground(state, 'washington')
    assert player.city.name == 'washington'
    assert player.action_count == action_count - 1


def test_ground_fail():
    state = default_init()
    player = state.players['A']
    player.set_city(state, state.cities['atlanta'])
    action_count = player.action_count
    player.ground(state, 'london')
    assert player.city.name == 'atlanta'
    assert player.action_count == action_count


def test_treat():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    city.add_disease(state, color, 3)
    player.treat(state, color)
    assert city.cubes[color] == 2


def test_treat_medic():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    city.add_disease(state, color, 3)
    player.treat(state, color)
    assert city.cubes[color] == 0
