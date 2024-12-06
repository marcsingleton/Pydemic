"""Tests for roles."""

import pytest

import pydemic.cards as cards
from .utils import default_init


# Generic player tests
def test_ground_success():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['washington']
    player.set_city(state, city_1)
    action_count = player.action_count
    player.ground(state, city_2.name)
    assert player.city is city_2
    assert player.action_count == action_count - 1


def test_ground_fail():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    action_count = player.action_count
    player.ground(state, city_2.name)
    assert player.city is city_1
    assert player.action_count == action_count


def test_direct_success():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.direct(state, city_2.name)
    assert player.city is city_2
    assert card not in player.hand.values()
    assert player.action_count == action_count - 1


def test_direct_fail():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.direct(state, city_2.name)
    assert player.city is city_1
    assert card in player.hand.values()
    assert player.action_count == action_count


def test_charter_success():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.charter(state, city_2.name)
    assert player.city is city_2
    assert card not in player.hand.values()
    assert player.action_count == action_count - 1


def test_charter_fail():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.charter(state, city_2.name)
    assert player.city is city_1
    assert card in player.hand.values()
    assert player.action_count == action_count


def test_shuttle_success():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    city_1.add_station(state)
    city_2.add_station(state)
    action_count = player.action_count
    player.shuttle(state, city_2.name)
    assert player.city is city_2
    assert player.action_count == action_count - 1


def test_shuttle_fail_no_station_current():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    city_2.add_station(state)
    action_count = player.action_count
    player.shuttle(state, city_2.name)
    assert player.city is city_1
    assert player.action_count == action_count


def test_shuttle_fail_no_station_target():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    city_1.add_station(state)
    action_count = player.action_count
    player.shuttle(state, city_2.name)
    assert player.city is city_1
    assert player.action_count == action_count


def test_shuttle_fail_no_station_both():
    state = default_init()
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    action_count = player.action_count
    player.shuttle(state, city_2.name)
    assert player.city is city_1
    assert player.action_count == action_count


def test_station_success():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    player.set_city(state, city)
    card = cards.pop_by_name(state.player_deck.draw_pile, city.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.station(state)
    assert city.station
    assert card not in player.hand.values()
    assert player.action_count == action_count - 1


def test_station_fail_wrong_card():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.station(state)
    assert not city_1.station
    assert card in player.hand.values()
    assert player.action_count == action_count


def test_station_fail_has_station():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    player.set_city(state, city)
    card = cards.pop_by_name(state.player_deck.draw_pile, city.name)
    player.add_card(state, card)
    city.add_station(state)
    action_count = player.action_count
    player.station(state)
    assert city.station
    assert card in player.hand.values()
    assert player.action_count == action_count


def test_treat_success():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    city.add_disease(state, color, 3)
    action_count = player.action_count
    player.treat(state, color)
    assert city.cubes[color] == 2
    assert player.action_count == action_count - 1


def test_treat_fail():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    action_count = player.action_count
    player.treat(state, color)
    assert city.cubes[color] == 0
    assert player.action_count == action_count


def test_share_success():
    state = default_init(role_map={'A': 'medic', 'B': 'scientist'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city = state.cities['atlanta']
    player_1.set_city(state, city)
    player_2.set_city(state, city)
    card = cards.pop_by_name(state.player_deck.draw_pile, city.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.share(state, player_2.name, city.name)
    assert card not in player_1.hand.values()
    assert card in player_2.hand.values()
    assert player_1.action_count == action_count - 1


def test_share_fail_wrong_card():
    state = default_init(role_map={'A': 'medic', 'B': 'scientist'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.share(state, player_2.name, city_1.name)
    assert card in player_1.hand.values()
    assert card not in player_2.hand.values()
    assert player_1.action_count == action_count


def test_share_fail_wrong_city():
    state = default_init(role_map={'A': 'medic', 'B': 'scientist'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_2)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.share(state, player_2.name, city_1.name)
    assert card in player_1.hand.values()
    assert card not in player_2.hand.values()
    assert player_1.action_count == action_count


@pytest.mark.parametrize('role_name', ['researcher', 'scientist'])
def test_cure_success(role_name):
    state = default_init(role_map={'A': role_name})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    cure_cards = [card for card in state.player_deck.draw_pile if card.color == color]
    cure_cards = cure_cards[: player.cure_num]
    for card in cure_cards:
        card = cards.pop_by_name(state.player_deck.draw_pile, card.name)
        player.add_card(state, card)
    city.add_station(state)
    action_count = player.action_count
    player.cure(state, color)
    assert not state.disease_track.is_active(color)
    for card in cure_cards:
        assert card not in player.hand.values()
    assert player.action_count == action_count - 1


@pytest.mark.parametrize('role_name', ['researcher', 'scientist'])
def test_cure_fail_no_station(role_name):
    state = default_init(role_map={'A': role_name})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    cure_cards = [card for card in state.player_deck.draw_pile if card.color == color]
    cure_cards = cure_cards[: player.cure_num]
    for card in cure_cards:
        player.add_card(state, card)
    action_count = player.action_count
    player.cure(state, color)
    assert state.disease_track.is_active(color)
    for card in cure_cards:
        assert card in player.hand.values()
    assert player.action_count == action_count


@pytest.mark.parametrize('role_name', ['researcher', 'scientist'])
def test_cure_fail_insufficient_cards(role_name):
    state = default_init(role_map={'A': role_name})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    cure_cards = [card for card in state.player_deck.draw_pile if card.color == color]
    cure_cards = cure_cards[: player.cure_num - 1]
    for card in cure_cards:
        card = cards.pop_by_name(state.player_deck.draw_pile, card.name)
        player.add_card(state, card)
    city.add_station(state)
    action_count = player.action_count
    player.cure(state, color)
    assert state.disease_track.is_active(color)
    for card in cure_cards:
        assert card in player.hand.values()
    assert player.action_count == action_count


def test_pass():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    action_count = player.action_count
    player.no_action(state)
    assert player.action_count == action_count - 1


# Contingency planner tests
def test_contingency_success():
    state = default_init(role_map={'A': 'contingency_planner'})
    player = state.players['A']
    card = cards.pop_by_name(state.player_deck.draw_pile, 'one_quiet_night')
    state.player_deck.discard(card)
    action_count = player.action_count
    player.contingency(state, card.name)
    assert player.contingency_slot is card
    assert card not in state.player_deck.discard_pile
    assert player.action_count == action_count - 1


def test_contingency_fail_occupied():
    state = default_init(role_map={'A': 'contingency_planner'})
    player = state.players['A']
    card_1 = cards.pop_by_name(state.player_deck.draw_pile, 'one_quiet_night')
    card_2 = cards.pop_by_name(state.player_deck.draw_pile, 'government_grant')
    state.player_deck.discard(card_1)
    state.player_deck.discard(card_2)
    player.contingency(state, card_1.name)
    action_count = player.action_count
    player.contingency(state, card_2.name)
    assert player.contingency_slot is card_1
    assert card_1 not in state.player_deck.discard_pile
    assert card_2 in state.player_deck.discard_pile
    assert player.action_count == action_count


def test_contingency_no_card():
    state = default_init(role_map={'A': 'contingency_planner'})
    player = state.players['A']
    card = cards.pop_by_name(state.player_deck.draw_pile, 'one_quiet_night')
    action_count = player.action_count
    player.contingency(state, card.name)
    assert player.contingency_slot is None
    assert card not in state.player_deck.discard_pile
    assert player.action_count == action_count


# Dispatcher tests
def test_airlift_success():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    player_3 = state.players['C']
    player_1.set_city(state, state.cities['atlanta'])
    player_2.set_city(state, state.cities['london'])
    player_3.set_city(state, state.cities['tokyo'])
    action_count = player_1.action_count
    player_1.airlift(state, player_2.name, player_3.name)
    assert player_2.city is player_3.city
    assert player_1.action_count == action_count - 1


def test_ground_dispatch_success():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['washington']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    action_count = player_1.action_count
    player_1.actions['ground'](state, city_2.name, player_2.name)
    assert player_2.city is city_2
    assert player_1.city is city_1
    assert player_1.action_count == action_count - 1


def test_ground_dispatch_fail():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    action_count = player_1.action_count
    player_1.actions['ground'](state, city_2.name, player_2.name)
    assert player_2.city is city_1
    assert player_1.city is city_1
    assert player_1.action_count == action_count


def test_direct_dispatch_success():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.actions['direct'](state, city_2.name, player_2.name)
    assert player_2.city is city_2
    assert player_1.city is city_1
    assert card not in player_1.hand.values()
    assert player_1.action_count == action_count - 1


def test_direct_dispatch_fail():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.actions['direct'](state, city_2.name, player_2.name)
    assert player_2.city is city_1
    assert player_1.city is city_1
    assert card in player_1.hand.values()
    assert player_1.action_count == action_count


def test_charter_dispatch_success():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.actions['charter'](state, city_2.name, player_2.name)
    assert player_2.city is city_2
    assert player_1.city is city_1
    assert card not in player_1.hand.values()
    assert player_1.action_count == action_count - 1


def test_charter_dispatch_fail():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.actions['charter'](state, city_2.name, player_2.name)
    assert player_2.city is city_1
    assert player_1.city is city_1
    assert card in player_1.hand.values()
    assert player_1.action_count == action_count


def test_shuttle_dispatch_success():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    city_1.add_station(state)
    city_2.add_station(state)
    action_count = player_1.action_count
    player_1.actions['shuttle'](state, city_2.name, player_2.name)
    assert player_2.city is city_2
    assert player_1.city is city_1
    assert player_1.action_count == action_count - 1


def test_shuttle_dispatch_fail_no_station_current():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    city_2.add_station(state)
    action_count = player_1.action_count
    player_1.actions['shuttle'](state, city_2.name, player_2.name)
    assert player_2.city is city_1
    assert player_1.city is city_1
    assert player_1.action_count == action_count


def test_shuttle_dispatch_fail_no_station_target():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    city_1.add_station(state)
    action_count = player_1.action_count
    player_1.actions['shuttle'](state, city_2.name, player_2.name)
    assert player_2.city is city_1
    assert player_1.city is city_1
    assert player_1.action_count == action_count


def test_shuttle_dispatch_fail_no_station_both():
    state = default_init(role_map={'A': 'dispatcher'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    action_count = player_1.action_count
    player_1.actions['shuttle'](state, city_2.name, player_2.name)
    assert player_2.city is city_1
    assert player_1.city is city_1
    assert player_1.action_count == action_count


# Medic tests
def test_treat_medic_success():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    city.add_disease(state, color, 3)
    action_count = player.action_count
    player.treat(state, color)
    assert city.cubes[color] == 0
    assert player.action_count == action_count - 1


def test_treat_medic_fail():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    action_count = player.action_count
    player.treat(state, color)
    assert city.cubes[color] == 0
    assert player.action_count == action_count


def test_medic_auto_treat():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    city.add_disease(state, color, 3)
    state.disease_track.set_cured(color)
    action_count = player.action_count
    player.set_city(state, city)
    assert city.cubes[color] == 0
    assert player.action_count == action_count


def test_medic_immunity():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    assert not player.immunity(state, city, color)
    state.disease_track.set_cured(color)
    assert player.immunity(state, city, color)


def test_medic_not_immunity_not_cured():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    assert not player.immunity(state, city, color)


def test_medic_not_immunity_not_in_city():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    state.disease_track.set_cured(color)
    assert not player.immunity(state, city, color)


# Operations expert tests
def test_opex_shuttle_success():
    state = default_init(role_map={'A': 'operations_expert'})
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    city_3 = state.cities['tokyo']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_3.name)
    player.add_card(state, card)
    city_1.add_station(state)
    action_count = player.action_count
    player.opex_shuttle(state, city_2.name, card.name)
    assert player.city is city_2
    assert card not in player.hand
    assert player.action_count == action_count - 1


def test_opex_shuttle_fail_no_station_current():
    state = default_init(role_map={'A': 'operations_expert'})
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    city_3 = state.cities['tokyo']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_3.name)
    player.add_card(state, card)
    action_count = player.action_count
    player.opex_shuttle(state, city_2.name, card.name)
    assert player.city is city_1
    assert card in player.hand.values()
    assert player.action_count == action_count


def test_opex_shuttle_fail_no_card():
    state = default_init(role_map={'A': 'operations_expert'})
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    city_3 = state.cities['tokyo']
    player.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_3.name)
    action_count = player.action_count
    player.opex_shuttle(state, city_2.name, card.name)
    assert player.city is city_1
    assert player.action_count == action_count


def test_opex_shuttle_fail_twice():
    state = default_init(role_map={'A': 'operations_expert'})
    player = state.players['A']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    city_3 = state.cities['tokyo']
    player.set_city(state, city_1)
    card_A = cards.pop_by_name(state.player_deck.draw_pile, city_3.name)
    card_B = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player.add_card(state, card_A)
    player.add_card(state, card_B)
    city_1.add_station(state)
    city_2.add_station(state)
    player.opex_shuttle(state, city_2.name, card_A.name)
    action_count = player.action_count
    player.opex_shuttle(state, city_3.name, card_B.name)
    assert player.city is city_2
    assert card_B in player.hand.values()
    assert player.action_count == action_count


def test_opex_station_success():
    state = default_init(role_map={'A': 'operations_expert'})
    player = state.players['A']
    city = state.cities['atlanta']
    player.set_city(state, city)
    action_count = player.action_count
    player.station(state)
    assert city.station
    assert player.action_count == action_count - 1


def test_opex_station_fail_has_station():
    state = default_init(role_map={'A': 'operations_expert'})
    player = state.players['A']
    city = state.cities['atlanta']
    player.set_city(state, city)
    city.add_station(state)
    action_count = player.action_count
    player.station(state)
    assert city.station
    assert player.action_count == action_count


# Quarantine specialist tests
def test_quarantine_specialist_immunity():
    state = default_init(role_map={'A': 'quarantine_specialist'})
    player = state.players['A']
    city = state.cities['atlanta']
    for neighbor in city.neighbors.values():
        for color in state.disease_track.colors:
            assert not player.immunity(state, neighbor, color)
    player.set_city(state, city)
    for neighbor in city.neighbors.values():
        for color in state.disease_track.colors:
            assert player.immunity(state, neighbor, color)


# Researcher tests
def test_researcher_share_success():
    state = default_init(role_map={'A': 'researcher', 'B': 'scientist'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city)
    player_2.set_city(state, city)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.share(state, player_2.name, card.name)
    assert card not in player_1.hand.values()
    assert card in player_2.hand.values()
    assert player_1.action_count == action_count - 1


def test_researcher_share_fail_wrong_player():
    state = default_init(role_map={'A': 'researcher', 'B': 'scientist'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_1)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_2.name)
    player_2.add_card(state, card)
    action_count = player_1.action_count
    player_2.share(state, player_2.name, city_1.name)
    assert card not in player_1.hand.values()
    assert card in player_2.hand.values()
    assert player_1.action_count == action_count


def test_share_fail_wrong_city():
    state = default_init(role_map={'A': 'researcher', 'B': 'scientist'})
    player_1 = state.players['A']
    player_2 = state.players['B']
    city_1 = state.cities['atlanta']
    city_2 = state.cities['london']
    player_1.set_city(state, city_1)
    player_2.set_city(state, city_2)
    card = cards.pop_by_name(state.player_deck.draw_pile, city_1.name)
    player_1.add_card(state, card)
    action_count = player_1.action_count
    player_1.share(state, player_2.name, city_1.name)
    assert card in player_1.hand.values()
    assert card not in player_2.hand.values()
    assert player_1.action_count == action_count
