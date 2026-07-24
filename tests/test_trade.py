"""
===========================================================
TradePilotAI
Trade Tests
===========================================================
"""

from datetime import datetime, timedelta

from models.trade import Trade


def test_profit():

    trade = Trade(
        symbol="RR.L",
        quantity=100,
        entry_price=250,
        exit_price=270,
        entry_date=datetime.now(),
        exit_date=datetime.now(),
    )

    assert trade.profit == 2000


def test_return_percent():

    trade = Trade(
        symbol="RR.L",
        quantity=100,
        entry_price=250,
        exit_price=275,
        entry_date=datetime.now(),
        exit_date=datetime.now(),
    )

    assert trade.return_percent == 10.0


def test_duration():

    start = datetime.now()
    end = start + timedelta(days=5)

    trade = Trade(
        symbol="RR.L",
        quantity=10,
        entry_price=100,
        exit_price=105,
        entry_date=start,
        exit_date=end,
    )

    assert trade.duration.days == 5