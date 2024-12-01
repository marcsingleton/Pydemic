"""Tests for cards."""

import pytest

import pydemic.cards as cards
import pydemic.exceptions as exceptions
from .utils import default_init


# Deck tests
def test_infection_deck_draw_simple():
    state = default_init()
    top_card = state.infection_deck.draw_pile[-1]
    city = state.cities[top_card.name]
    color = top_card.color
    state.infection_deck.draw(state)
    assert city.cubes[color] == 1
    assert state.disease_track.cubes[color] == state.disease_track.cube_num - 1


def test_infection_deck_draw_immune():
    state = default_init(role_map={'A': 'quarantine specialist'})
    top_card = state.infection_deck.draw_pile[-1]
    city = state.cities[top_card.name]
    color = top_card.color
    player = state.players['A']
    player.set_city(state, city)
    state.infection_deck.draw(state)
    assert city.cubes[color] == 0
    assert state.disease_track.cubes[color] == state.disease_track.cube_num


def test_infection_deck_remove():
    state = default_init()
    for _ in range(3):
        state.infection_deck.draw(state)
    draw_cards = [card for card in state.infection_deck.discard_pile]
    state.infection_deck.remove(draw_cards[1].name)
    assert draw_cards[0] in state.infection_deck.discard_pile
    assert draw_cards[1] not in state.infection_deck.discard_pile
    assert draw_cards[2] in state.infection_deck.discard_pile


def test_infection_deck_remove_twice():
    state = default_init()
    state.infection_deck.draw(state)
    for _ in range(3):
        state.infection_deck.draw(state)
    draw_cards = [card for card in state.infection_deck.discard_pile]
    state.infection_deck.remove(draw_cards[1].name)
    with pytest.raises(exceptions.PropertyError):
        state.infection_deck.remove(draw_cards[1].name)
    assert draw_cards[1] not in state.infection_deck.discard_pile


def test_player_deck_draw_simple():
    state = default_init()
    top_card = state.player_deck.draw_pile[-1]
    draw_card = state.player_deck.draw()
    assert top_card is draw_card


def test_player_deck_draw_no_cards():
    state = default_init()
    state.player_deck.draw_pile = []
    with pytest.raises(exceptions.GameOverLose):
        state.player_deck.draw()


def test_player_deck_retrieve():
    state = default_init()
    draw_cards = []
    for _ in range(3):
        draw_card = state.player_deck.draw()
        draw_cards.append(draw_card)
        state.player_deck.discard(draw_card)
    target_card = draw_cards[1]
    retrieved_card = state.player_deck.retrieve(target_card.name)
    assert target_card is retrieved_card
    assert draw_cards[0] in state.player_deck.discard_pile
    assert draw_cards[1] not in state.player_deck.discard_pile
    assert draw_cards[2] in state.player_deck.discard_pile


def test_player_deck_retrieve_twice():
    state = default_init()
    draw_cards = []
    for _ in range(3):
        draw_card = state.player_deck.draw()
        draw_cards.append(draw_card)
        state.player_deck.discard(draw_card)
    target_card = draw_cards[1]
    state.player_deck.retrieve(target_card.name)
    with pytest.raises(exceptions.PropertyError):
        state.player_deck.retrieve(target_card.name)
    assert target_card not in state.player_deck.discard_pile


# Event tests
def test_airlift():
    state = default_init()
    city_name_1 = 'atlanta'
    city_name_2 = 'london'
    city_1 = state.cities[city_name_1]
    city_2 = state.cities[city_name_2]
    cards.input = lambda x: f'A {city_name_2}'
    player = state.players['A']
    player.set_city(state, city_1)
    cards.air_lift(state)
    assert player.city is city_2


def test_forecast():
    state = default_init()
    order = [5, 1, 4, 0, 3, 2]
    cards.input = lambda x: ''.join([str(idx) for idx in order])
    old_top = state.infection_deck.draw_pile[-1:-7:-1]
    cards.forecast(state)
    new_top = state.infection_deck.draw_pile[-1:-7:-1]
    for idx, card in zip(order, new_top):
        assert card is old_top[idx]


def test_government_grant():
    state = default_init()
    city_name = 'atlanta'
    city = state.cities[city_name]
    cards.input = lambda x: city_name
    cards.government_grant(state)
    assert city.station


def test_one_quiet_night():
    state = default_init()
    assert state.infect_count == 0


def test_resilient_population():
    state = default_init()
    state.infection_deck.draw(state)
    card = state.infection_deck.discard_pile[0]
    cards.input = lambda x: card.name
    cards.resilient_population(state)
    assert card not in state.infection_deck.discard_pile
