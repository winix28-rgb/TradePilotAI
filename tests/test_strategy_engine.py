"""
===========================================================
TradePilotAI OS
Strategy Engine Test
===========================================================
"""

from tradepilotai_os.market_data import YahooMarketDataProvider
from tradepilotai_os.indicators.indicator_engine import IndicatorEngine
from tradepilotai_os.strategy.strategy_engine import StrategyEngine


def test_strategy_engine():

    provider = YahooMarketDataProvider()

    print("\nDownloading market data...")

    data = provider.history("RR", interval="1h")

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