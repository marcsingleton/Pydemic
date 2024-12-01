"""Tests for roles."""

import pydemic.cards as cards
from .utils import default_init


# Generic action tests
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
    assert player.action_count == action_count - 1
    assert card not in player.hand.values()
    

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
    assert player.action_count == action_count
    assert card in player.hand.values()


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
    assert player.action_count == action_count - 1
    assert card not in player.hand.values()


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
    assert player.action_count == action_count
    assert card in player.hand.values()


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


def test_shuttle_fail_no_station_target():
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
    assert player.action_count == action_count
    assert card in player.hand.values()


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
    player_2.set_city(state, city_2)
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


def test_cure_success():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    cure_cards = []
    for card_name in ['atlanta', 'washington', 'chicago', 'new_york', 'london']:
        card = cards.pop_by_name(state.player_deck.draw_pile, card_name)
        cure_cards.append(card)
        player.add_card(state, card)
    city.add_station(state)
    action_count = player.action_count
    player.cure(state, color)
    assert not state.disease_track.is_active(color)
    for card in cure_cards:
        assert card not in player.hand.values()
    assert player.action_count == action_count - 1


def test_cure_fail_no_station():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    cure_cards = []
    for card_name in ['atlanta', 'washington', 'chicago', 'new_york', 'london']:
        card = cards.pop_by_name(state.player_deck.draw_pile, card_name)
        cure_cards.append(card)
        player.add_card(state, card)
    action_count = player.action_count
    player.cure(state, color)
    assert state.disease_track.is_active(color)
    for card in cure_cards:
        assert card in player.hand.values()
    assert player.action_count == action_count


def test_cure_fail_insufficient_cards():
    state = default_init(role_map={'A': 'researcher'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    cure_cards = []
    for card_name in ['atlanta', 'washington', 'chicago', 'new_york']:
        card = cards.pop_by_name(state.player_deck.draw_pile, card_name)
        cure_cards.append(card)
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
    state = default_init(role_map={'A': 'contingency planner'})
    player = state.players['A']
    card = cards.pop_by_name(state.player_deck.draw_pile, 'one_quiet_night')
    state.player_deck.discard(card)
    action_count = player.action_count
    player.contingency(state, card.name)
    assert player.contingency_slot is card
    assert player.action_count == action_count - 1
    assert card not in state.player_deck.discard_pile


def test_contingency_fail_occupied():
    state = default_init(role_map={'A': 'contingency planner'})
    player = state.players['A']
    card_1 = cards.pop_by_name(state.player_deck.draw_pile, 'one_quiet_night')
    card_2 = cards.pop_by_name(state.player_deck.draw_pile, 'government_grant')
    state.player_deck.discard(card_1)
    state.player_deck.discard(card_2)
    player.contingency(state, card_1.name)
    action_count = player.action_count
    player.contingency(state, card_2.name)
    assert player.contingency_slot is card_1
    assert player.action_count == action_count
    assert card_1 not in state.player_deck.discard_pile
    assert card_2 in state.player_deck.discard_pile


def test_contingency_no_card():
    state = default_init(role_map={'A': 'contingency planner'})
    player = state.players['A']
    card = cards.pop_by_name(state.player_deck.draw_pile, 'one_quiet_night')
    action_count = player.action_count
    player.contingency(state, card.name)
    assert player.contingency_slot is None
    assert player.action_count == action_count
    assert card not in state.player_deck.discard_pile


def test_treat_medic():
    state = default_init(role_map={'A': 'medic'})
    player = state.players['A']
    city = state.cities['atlanta']
    color = 'blue'
    player.set_city(state, city)
    city.add_disease(state, color, 3)
    player.treat(state, color)
    assert city.cubes[color] == 0
