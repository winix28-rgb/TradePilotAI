"""
===========================================================
TradePilotAI
Strategy Tests
===========================================================
"""

from datetime import datetime

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData
from signals.trade_signal import TradeSignal
from strategies.strategy import Strategy


class DummyStrategy(Strategy):
    """
    Simple strategy used for testing the Strategy interface.
    """

    def generate_signal(
        self,
        symbol: str,
        historical_data: HistoricalData,
        index: int,
    ) -> TradeSignal | None:
        return None


def create_data() -> HistoricalData:
    """
    Create a simple HistoricalData object for testing.
    """

    candle = Candle(
        timestamp=datetime(2025, 1, 1),
        open=100,
        high=105,
        low=99,
        close=104,
        volume=1000,
    )

    return HistoricalData([candle])


def test_strategy_returns_none() -> None:
    """
    Verify that a strategy can return None.
    """

    strategy = DummyStrategy()

    result = strategy.generate_signal(
        symbol="RR.L",
        historical_data=create_data(),
        index=0,
    )

    assert result is None