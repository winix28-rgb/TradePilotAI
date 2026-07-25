"""
===========================================================
TradePilotAI
Parameter Grid Tests
===========================================================
"""

from optimisation.parameter_grid import ParameterGrid


def test_empty_grid():

    grid = ParameterGrid({})

    assert grid.generate() == []
    assert len(grid) == 0


def test_single_parameter():

    grid = ParameterGrid({

        "ema_fast": [10, 12, 14],

    })

    combinations = grid.generate()

    assert len(combinations) == 3

    assert combinations == [

        {"ema_fast": 10},
        {"ema_fast": 12},
        {"ema_fast": 14},

    ]


def test_two_parameters():

    grid = ParameterGrid({

        "ema_fast": [10, 12],
        "ema_slow": [20, 26],

    })

    combinations = grid.generate()

    assert len(combinations) == 4

    assert {"ema_fast": 10, "ema_slow": 20} in combinations
    assert {"ema_fast": 10, "ema_slow": 26} in combinations
    assert {"ema_fast": 12, "ema_slow": 20} in combinations
    assert {"ema_fast": 12, "ema_slow": 26} in combinations


def test_three_parameters():

    grid = ParameterGrid({

        "ema_fast": [10, 12],
        "ema_slow": [20],
        "buy_rsi": [25, 30],

    })

    assert len(grid) == 4


def test_float_parameters():

    grid = ParameterGrid({

        "risk": [0.5, 1.0],

    })

    combinations = grid.generate()

    assert combinations == [

        {"risk": 0.5},
        {"risk": 1.0},

    ]