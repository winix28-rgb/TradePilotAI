"""
===========================================================
TradePilotAI OS
Strategy Engine Test
===========================================================
"""

import pandas as pd

from tradepilotai_os.market_data import YahooMarketDataProvider
from tradepilotai_os.indicators.indicator_engine import IndicatorEngine
from tradepilotai_os.strategy.strategy_engine import StrategyEngine


def test_strategy_engine():

    provider = YahooMarketDataProvider()

    print("\nDownloading market data...")

    data = provider.history("RR")

    print(f"Downloaded {len(data)} candles")

    data = IndicatorEngine.add_indicators(data)

    engine = StrategyEngine()

    signal = engine.evaluate(
        "RR",
        data,
    )

    print()
    print("=" * 60)
    print("STRATEGY ENGINE RESULT")
    print("=" * 60)

    print(signal)

    assert signal.symbol == "RR"

    assert signal.signal in (
        "BUY",
        "SELL",
        "HOLD",
    )

    assert signal.price > 0

    assert signal.stop_loss > 0

    assert signal.target > 0


def test_signal_engine_uses_hold_for_non_triggering_conditions():
    data = pd.DataFrame(
        {
            "Close": [100 + (idx * 0.3) for idx in range(30)],
            "RSI": [52 + (idx % 3) for idx in range(30)],
            "EMA12": [100.2 + (idx * 0.15) for idx in range(30)],
            "EMA26": [100.0 + (idx * 0.10) for idx in range(30)],
        }
    )

    signal = StrategyEngine().evaluate("TEST", data)

    assert signal.signal == "HOLD"
    assert "No qualifying setup" in signal.reasons
    assert 0 <= signal.confidence <= 100