"""
===========================================================
TradePilotAI
Daily Loss Limit Tests
===========================================================
"""

import pytest

from risk.daily_loss_limit import DailyLossLimit



def test_maximum_loss_calculation():

    risk = DailyLossLimit(
        starting_balance=10000,
        max_loss_percent=2,
    )


    assert risk.maximum_loss == 200



def test_trading_allowed_when_loss_is_small():

    risk = DailyLossLimit(
        starting_balance=10000,
        max_loss_percent=2,
    )


    assert risk.trading_allowed(
        9900
    )



def test_trading_stops_after_limit():

    risk = DailyLossLimit(
        starting_balance=10000,
        max_loss_percent=2,
    )


    assert not risk.trading_allowed(
        9800
    )



def test_invalid_balance_fails():

    with pytest.raises(ValueError):

        DailyLossLimit(
            starting_balance=0
        )