"""Common utilities for testing."""

import pydemic.argfuncs as argfuncs
import pydemic.main as main
import pydemic.constants as constants


def default_init(player_names='A,B,C,D', epidemic_num='4', role_map=None):
    args = [
        '--player_names', player_names,
        '--epidemic_num', epidemic_num,
    ]

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

    argfuncs.check_args(
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

    state = main.initialize_state(args, role_map=role_map)

    return state
