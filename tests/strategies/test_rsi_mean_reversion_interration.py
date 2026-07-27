"""
===========================================================
TradePilotAI
RSI Mean Reversion Integration Tests
===========================================================
"""

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData

from models.strategy_config import StrategyConfig

from strategies.rsi_mean_reversion import (
    RSIMeanReversionStrategy,
)


def create_candle(
    day: int,
    price: float,
) -> Candle:

    return Candle(
        timestamp=datetime(
            2025,
            1,
            day,
        ),
        open=price,
        high=price + 1,
        low=price - 1,
        close=price,
        volume=1000,
    )


def test_strategy_can_be_created_with_configuration():

    config = StrategyConfig(
        buy_rsi=30,
        exit_rsi=50,
        rsi_period=14,
        ema_fast=12,
        ema_slow=26,
    )

    strategy = RSIMeanReversionStrategy(
        config
    )

    assert strategy.config.buy_rsi == 30
    assert strategy.config.exit_rsi == 50
    assert strategy.config.ema_fast == 12
    assert strategy.config.ema_slow == 26


def test_strategy_resets_state():

    strategy = RSIMeanReversionStrategy()

    strategy.reset()

    assert strategy.state is not None