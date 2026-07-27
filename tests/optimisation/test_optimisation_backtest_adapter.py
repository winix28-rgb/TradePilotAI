"""
===========================================================
TradePilotAI
Optimisation Backtest Adapter Tests
===========================================================
"""

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData
from backtesting.backtest_runner import BacktestRunner

from models.application_config import ApplicationConfig
from models.strategy_config import StrategyConfig

from optimisation.backtest_adapter import (
    OptimisationBacktestRunner,
)


def create_historical_data():

    candles = []


    prices = [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
    ]


    for price in prices:

        candles.append(

            Candle(

                timestamp=datetime(
                    2025,
                    1,
                    1,
                ),

                open=price,

                high=price + 1,

                low=price - 1,

                close=price,

                volume=1000,

            )

        )


    return HistoricalData(
        candles
    )



def test_optimisation_adapter_returns_backtest_result():

    config = ApplicationConfig()


    adapter = OptimisationBacktestRunner(

        base_config=config,

        symbol="TEST",

        historical_data=create_historical_data(),

        backtest_runner_factory=BacktestRunner,

    )


    strategy_config = StrategyConfig(

        buy_rsi=30,

        exit_rsi=50,

        ema_fast=12,

        ema_slow=26,

    )


    result = adapter.run(
        strategy_config
    )


    assert result is not None

    assert hasattr(
        result,
        "net_profit",
    )

    assert hasattr(
        result,
        "portfolio",
    )