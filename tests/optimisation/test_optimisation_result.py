"""
===========================================================
TradePilotAI
Optimisation Result Tests
===========================================================
"""

from optimisation.optimisation_result import OptimisationResult


def test_properties():

    result = OptimisationResult(
        parameters={
            "ema_fast": 12,
            "ema_slow": 26,
            "buy_rsi": 30,
            "sell_rsi": 70,
        },
        net_profit=18250,
        win_rate=61.5,
        profit_factor=2.10,
        max_drawdown=8.5,
        expectancy=152.50,
        total_trades=120,
    )

    assert result.net_profit == 18250
    assert result.win_rate == 61.5
    assert result.profit_factor == 2.10
    assert result.max_drawdown == 8.5
    assert result.expectancy == 152.50
    assert result.total_trades == 120


def test_score():

    result = OptimisationResult(
        parameters={},
        net_profit=10000,
        win_rate=55,
        profit_factor=2.0,
        max_drawdown=10,
        expectancy=100,
        total_trades=50,
    )

    assert result.score == 180.0


def test_higher_drawdown_reduces_score():

    conservative = OptimisationResult(
        parameters={},
        net_profit=10000,
        win_rate=60,
        profit_factor=2.0,
        max_drawdown=5,
        expectancy=100,
        total_trades=100,
    )

    aggressive = OptimisationResult(
        parameters={},
        net_profit=10000,
        win_rate=60,
        profit_factor=2.0,
        max_drawdown=25,
        expectancy=100,
        total_trades=100,
    )

    assert conservative.score > aggressive.score


def test_zero_drawdown_gives_highest_score():

    result = OptimisationResult(
        parameters={},
        net_profit=10000,
        win_rate=60,
        profit_factor=2.0,
        max_drawdown=0,
        expectancy=100,
        total_trades=100,
    )

    assert result.score == 200.0