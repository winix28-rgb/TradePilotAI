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


def main():

    print("=" * 60)
    print("TradePilotAI")
    print("=" * 60)

    print("\nLoading market data...")

    data = DataLoader.load_yahoo("RR.L")

    print(f"Loaded {len(data)} bars")

    print("\nCalculating indicators...")

    data = IndicatorEngine.add_indicators(data)

    print("\nRunning strategy...\n")

    strategy = RSIMeanReversionStrategy()

    engine = StrategyEngine(strategy)

    trades = engine.run(data)

    print("=" * 60)
    print("Trade History")
    print("=" * 60)

    if not trades:
        print("No completed trades found.")

    for number, trade in enumerate(trades, start=1):

        print()

        print(f"Trade #{number}")

        print("-" * 40)

        print(f"Entry Date : {trade.entry_date.date()}")
        print(f"Exit Date  : {trade.exit_date.date()}")

        print(f"Entry Price: {trade.entry_price:.2f}")
        print(f"Exit Price : {trade.exit_price:.2f}")

        print(f"Profit     : {trade.profit:.2f}")

        print(f"Return     : {trade.return_percent:.2f}%")

        print(f"Duration   : {trade.duration_days} days")

        print(f"Reason     : {trade.exit_reason}")

    print()

    print("=" * 60)

    print(f"Completed Trades : {len(trades)}")

    print("=" * 60)


if __name__ == "__main__":
    main()