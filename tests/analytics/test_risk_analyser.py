"""
===========================================================
TradePilotAI
Risk Analyser Tests
===========================================================
"""

from datetime import datetime

from analytics.risk_analyser import RiskAnalyser
from backtesting.equity_point import EquityPoint


def point(equity: float) -> EquityPoint:

    return EquityPoint(
        timestamp=datetime(2025, 1, 1),
        equity=equity,
    )


def test_empty_equity_curve():

    analyser = RiskAnalyser([])

    assert analyser.max_drawdown == 0.0
    assert analyser.max_drawdown_amount == 0.0
    assert analyser.current_drawdown == 0.0
    assert analyser.current_drawdown_amount == 0.0
    assert analyser.current_equity == 0.0
    assert analyser.peak_equity == 0.0
    assert analyser.trough_equity == 0.0


def test_maximum_drawdown():

    curve = [
        point(10000),
        point(12000),
        point(9000),
    ]

    analyser = RiskAnalyser(curve)

    assert round(analyser.max_drawdown, 2) == 25.00
    assert analyser.max_drawdown_amount == 3000
    assert analyser.peak_equity == 12000
    assert analyser.trough_equity == 9000


def test_current_equity():

    curve = [
        point(10000),
        point(11000),
        point(10500),
    ]

    analyser = RiskAnalyser(curve)

    assert analyser.current_equity == 10500


def test_current_drawdown():

    curve = [
        point(10000),
        point(12000),
        point(10000),
    ]

    analyser = RiskAnalyser(curve)

    assert analyser.current_drawdown_amount == 2000
    assert round(analyser.current_drawdown, 2) == 16.67


def test_recovered_equity_has_no_current_drawdown():

    curve = [
        point(10000),
        point(12000),
        point(9000),
        point(13000),
    ]

    analyser = RiskAnalyser(curve)

    assert analyser.current_equity == 13000
    assert analyser.current_drawdown_amount == 0.0
    assert analyser.current_drawdown == 0.0

    # Historical maximum drawdown is still retained.
    assert analyser.max_drawdown_amount == 3000
    assert round(analyser.max_drawdown, 2) == 25.00