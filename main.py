"""
===========================================================
TradePilotAI
Main
===========================================================

Application entry point.
"""

from backtesting.performance import Performance
from backtesting.statistics import Statistics
from core.strategy_engine import StrategyEngine
from data.data_loader import DataLoader
from indicators.indicator_engine import IndicatorEngine
from strategies.rsi_mean_reversion import RSIMeanReversionStrategy


def print_trade_history(trades):
    """Display completed trades."""

    print("=" * 60)
    print("Trade History")
    print("=" * 60)

    if not trades:
        print("No completed trades found.")
        return

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


def print_statistics(stats: Statistics):
    """Display summary statistics."""

    print("=" * 60)
    print("Backtest Summary")
    print("=" * 60)

    print(f"Total Trades      : {stats.total_trades}")
    print(f"Winning Trades    : {stats.winning_trades}")
    print(f"Losing Trades     : {stats.losing_trades}")

    print()

    print(f"Win Rate          : {stats.win_rate:.2f}%")
    print(f"Net Profit        : {stats.net_profit:.2f}")
    print(f"Average Profit    : {stats.average_profit:.2f}")

    print()

    print(f"Average Winner    : {stats.average_winner:.2f}")
    print(f"Average Loser     : {stats.average_loser:.2f}")

    print()

    print(f"Largest Winner    : {stats.largest_winner:.2f}")
    print(f"Largest Loser     : {stats.largest_loser:.2f}")

    print()

    print(f"Average Duration  : {stats.average_trade_duration:.1f} days")

    print("=" * 60)


def print_performance(performance: Performance):
    """Display advanced performance metrics."""

    print("=" * 60)
    print("Performance Metrics")
    print("=" * 60)

    print(f"Gross Profit      : {performance.gross_profit:.2f}")
    print(f"Gross Loss        : {performance.gross_loss:.2f}")

    if performance.profit_factor == float("inf"):
        print("Profit Factor     : Infinite")
    else:
        print(f"Profit Factor     : {performance.profit_factor:.2f}")

    print(f"Expectancy        : {performance.expectancy:.2f}")

    if performance.reward_risk_ratio == float("inf"):
        print("Reward/Risk Ratio : Infinite")
    else:
        print(f"Reward/Risk Ratio : {performance.reward_risk_ratio:.2f}")

    print("=" * 60)


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

    stats = Statistics(trades)
    performance = Performance(stats)

    print_trade_history(trades)

    print_statistics(stats)

    print_performance(performance)


if __name__ == "__main__":
    main()