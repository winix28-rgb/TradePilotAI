"""
===========================================================
TradePilotAI
Backtest Runner Tests
===========================================================
"""

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData
from backtesting.backtest_result import BacktestResult

from backtesting.backtest_runner import BacktestRunner

from config.config_manager import ConfigManager


def create_test_data():

    candles = [
        Candle(
            timestamp=datetime(2025, 1, 1),
            open=100,
            high=105,
            low=95,
            close=100,
            volume=1000,
        ),

        Candle(
            timestamp=datetime(2025, 1, 2),
            open=101,
            high=106,
            low=96,
            close=102,
            volume=1000,
        ),
    ]

    return HistoricalData(candles)


def test_backtest_runner_returns_result():

    config = ConfigManager.load(
        "config/default_config.yaml"
    )

    runner = BacktestRunner(
        config
    )

    data = create_test_data()

    result = runner.run(
        symbol="RR.L",
        historical_data=data,
    )

    assert isinstance(
        result,
        BacktestResult,
    )


def test_backtest_runner_uses_config_cash():

    config = ConfigManager.load(
        "config/default_config.yaml"
    )

    runner = BacktestRunner(
        config
    )

    data = create_test_data()

    result = runner.run(
        symbol="RR.L",
        historical_data=data,
    )

    assert result.initial_cash == 100000