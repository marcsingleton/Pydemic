"""Tests for argfuncs."""

from string import ascii_uppercase

import pytest

import pydemic.argfuncs as argfuncs
import pydemic.constants as constants


def parse_args(args):
    args = argfuncs.parse_args(
        args,
        constants.player_min_word,
        constants.player_max_word,
        constants.epidemic_min_word,
        constants.epidemic_max_word,
        constants.default_map,
        constants.start_city,
        constants.outbreak_max,
        constants.infection_seq,
        constants.cube_num,
        constants.station_num,
    )

    return args


def check_args(args):
    args = argfuncs.check_args(
        args,
        constants.player_min,
        constants.player_max,
        constants.player_min_word,
        constants.player_max_word,
        constants.epidemic_min,
        constants.epidemic_max,
        constants.epidemic_min_word,
        constants.epidemic_max_word,
    )

    return args


# argfunc tests
@pytest.mark.parametrize('player_num', range(constants.player_min, constants.player_max + 1))
def test_player_names_success(player_num):
    player_names = list(ascii_uppercase)[:player_num]
    args = ['--player_names', ','.join(player_names)]
    args = parse_args(args)
    check_args(args)
    assert args.player_names == player_names


@pytest.mark.parametrize('player_num', [constants.player_min - 1, constants.player_max + 1])
def test_player_names_fail(player_num):
    player_names = list(ascii_uppercase)[:player_num]
    args = ['--player_names', ','.join(player_names)]
    args = parse_args(args)
    with pytest.raises(SystemExit):
        check_args(args)


@pytest.mark.parametrize('epidemic_num', range(constants.epidemic_min, constants.epidemic_max + 1))
def test_epidemic_num_success(epidemic_num):
    args = ['--epidemic_num', str(epidemic_num)]
    args = parse_args(args)
    check_args(args)
    assert args.epidemic_num == epidemic_num


@pytest.mark.parametrize('epidemic_num', [constants.epidemic_min - 1, constants.epidemic_max + 1])
def test_epidemic_num_fail(epidemic_num):
    args = ['--epidemic_num', str(epidemic_num)]
    args = parse_args(args)
    with pytest.raises(SystemExit):
        check_args(args)


def test_infection_seq_default():
    args = []
    args = parse_args(args)
    check_args(args)
    infection_seq = [int(value) for value in constants.infection_seq.split(',')]
    assert args.infection_seq == infection_seq


def test_infection_seq_empty():
    args = ['--infection_seq', ',,,']
    args = parse_args(args)
    with pytest.raises(SystemExit):
        check_args(args)


def test_infection_seq_nonpositive():
    args = ['--infection_seq', '0,1,2']
    args = parse_args(args)
    with pytest.raises(SystemExit):
        check_args(args)


def test_infection_seq_nonmonotonic():
    args = ['--infection_seq', '1,2,1']
    args = parse_args(args)
    with pytest.raises(SystemExit):
        check_args(args)


def test_infection_seq_nonnumeric():
    args = ['--infection_seq', '1,b,3']
    args = parse_args(args)
    with pytest.raises(SystemExit):
        check_args(args)
