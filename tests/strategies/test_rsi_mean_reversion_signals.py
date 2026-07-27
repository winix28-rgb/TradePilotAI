"""
===========================================================
TradePilotAI
RSI Mean Reversion Signal Tests
===========================================================
"""

from models.strategy_config import StrategyConfig
from models.strategy_state import StrategyStatus

from signals.signal_types import SignalType

from strategies.rsi_mean_reversion import (
    RSIMeanReversionStrategy,
)


def create_strategy():

    return RSIMeanReversionStrategy(
        StrategyConfig(
            buy_rsi=30,
            exit_rsi=50,
            rsi_period=14,
            ema_fast=12,
            ema_slow=26,
        )
    )


def test_oversold_condition_moves_strategy_to_watch():

    strategy = create_strategy()

    previous = {
        "RSI": 40,
        "Low": 100,
        "Close": 100,
        "EMA12": 100,
        "EMA26": 101,
    }

    current = {
        "RSI": 25,
        "Low": 95,
        "Close": 96,
        "EMA12": 99,
        "EMA26": 101,
    }


    signal = strategy.on_bar(
        previous,
        current,
    )


    assert signal == SignalType.NONE

    assert (
        strategy.state.state
        ==
        StrategyStatus.WATCHING_LONG
    )


def test_ema_cross_after_oversold_creates_buy_signal():

    strategy = create_strategy()


    # First bar creates oversold condition

    strategy.on_bar(
        {
            "RSI": 40,
            "Low": 100,
            "Close": 100,
            "EMA12": 100,
            "EMA26": 101,
        },
        {
            "RSI": 25,
            "Low": 95,
            "Close": 96,
            "EMA12": 99,
            "EMA26": 101,
        },
    )


    # EMA crossover occurs

    signal = strategy.on_bar(
        {
            "RSI": 25,
            "Low": 94,
            "Close": 97,
            "EMA12": 99,
            "EMA26": 101,
        },
        {
            "RSI": 35,
            "Low": 96,
            "Close": 102,
            "EMA12": 103,
            "EMA26": 101,
        },
    )


    assert signal == SignalType.BUY

    assert (
        strategy.state.state
        ==
        StrategyStatus.LONG
    )


def test_rsi_exit_closes_long_position():

    strategy = create_strategy()


    strategy.state.state = StrategyStatus.LONG


    signal = strategy.on_bar(
        {
            "RSI": 55,
            "Low": 100,
            "Close": 105,
            "EMA12": 103,
            "EMA26": 101,
        },
        {
            "RSI": 60,
            "Low": 101,
            "Close": 106,
            "EMA12": 104,
            "EMA26": 102,
        },
    )


    assert signal == SignalType.SELL

    assert (
        strategy.state.state
        ==
        StrategyStatus.IDLE
    )