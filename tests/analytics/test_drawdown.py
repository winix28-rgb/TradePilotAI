"""
===========================================================
TradePilotAI
Drawdown Tests
===========================================================
"""

from datetime import datetime

from analytics.drawdown import DrawdownCalculator
from backtesting.equity_point import EquityPoint


def point(equity: float) -> EquityPoint:

    return EquityPoint(
        timestamp=datetime(2025, 1, 1),
        equity=equity,
    )


def test_empty_equity_curve():

    result = DrawdownCalculator.calculate([])

    assert result.amount == 0
    assert result.percent == 0


def test_no_drawdown():

    curve = [
        point(10000),
        point(10100),
        point(10200),
        point(10300),
    ]

    result = DrawdownCalculator.calculate(curve)

    assert result.amount == 0
    assert result.percent == 0


def test_simple_drawdown():

    curve = [
        point(10000),
        point(11000),
        point(10500),
    ]

    result = DrawdownCalculator.calculate(curve)

    assert result.peak == 11000
    assert result.trough == 10500
    assert result.amount == 500
    assert round(result.percent, 2) == 4.55


def test_multiple_drawdowns_returns_largest():

    curve = [
        point(10000),
        point(12000),
        point(11800),
        point(9000),
        point(11000),
        point(9500),
    ]

    result = DrawdownCalculator.calculate(curve)

    assert result.peak == 12000
    assert result.trough == 9000
    assert result.amount == 3000
    assert round(result.percent, 2) == 25.00