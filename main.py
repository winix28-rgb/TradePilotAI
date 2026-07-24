"""
===========================================================
TradePilotAI
Main
===========================================================
"""

from data.data_loader import DataLoader
from indicators.indicator_engine import IndicatorEngine
from strategies.rsi_mean_reversion import RSIMeanReversionStrategy
from core.strategy_engine import StrategyEngine
from signals.signal_types import SignalType


def main():

    print("=" * 60)
    print("TradePilotAI")
    print("=" * 60)

    print("\nLoading market data...")

    data = DataLoader.load_yahoo("RR.L")

    print(f"Loaded {len(data)} bars")

    print("\nCalculating indicators...")

    data = IndicatorEngine.add_indicators(data)

    print("\nColumns:")
    print(data.columns.tolist())

    print("\nLast five rows:")
    print(data.tail())

    print("\nRunning strategy...\n")

    strategy = RSIMeanReversionStrategy()

    engine = StrategyEngine(strategy)

    signals = engine.run(data)

    buy = 0
    sell = 0

    for i, signal in enumerate(signals, start=1):

        if signal == SignalType.BUY:

            buy += 1

            row = data.iloc[i]

            print(f"BUY  {row.name.date()}  {row.Close:.2f}")

        elif signal == SignalType.SELL:

            sell += 1

            row = data.iloc[i]

            print(f"SELL {row.name.date()}  {row.Close:.2f}")

    print("\nFinished")

    print(f"BUY Signals : {buy}")
    print(f"SELL Signals: {sell}")


if __name__ == "__main__":
    main()