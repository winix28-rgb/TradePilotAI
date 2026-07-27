"""
===========================================================
TradePilotAI
Maximum Position Manager Tests
===========================================================
"""

import pytest

from risk.max_position_manager import MaxPositionManager



def test_position_allowed_below_limit():

    manager = MaxPositionManager(
        maximum_positions=5
    )


    assert manager.can_open_position(
        3
    )



def test_position_rejected_at_limit():

    manager = MaxPositionManager(
        maximum_positions=5
    )


    assert not manager.can_open_position(
        5
    )



def test_remaining_capacity():

    manager = MaxPositionManager(
        maximum_positions=10
    )


    assert manager.remaining_capacity(
        4
    ) == 6



def test_invalid_maximum_positions():

    with pytest.raises(ValueError):

        MaxPositionManager(
            maximum_positions=0
        )



def test_negative_positions_fail():

    manager = MaxPositionManager(
        maximum_positions=5
    )


    with pytest.raises(ValueError):

        manager.can_open_position(
            -1
        )