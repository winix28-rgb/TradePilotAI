"""
===========================================================
TradePilotAI
Report Generator
===========================================================

Creates console reports from completed trades,
statistics and performance metrics.
"""

from backtesting.performance import Performance
from backtesting.statistics import Statistics


class ReportGenerator:

    def __init__(
        self,
        statistics: Statistics,
        performance: Performance,
    ):
        self.statistics = statistics
        self.performance = performance

    def print_console(self):

        self._print_header()
        self._print_statistics()
        self._print_performance()
        self._print_footer()

    def _print_header(self):

        print("=" * 60)
        print("TradePilotAI Backtest Report")
        print("=" * 60)
        print()

    def _print_statistics(self):

        s = self.statistics

        print("BACKTEST SUMMARY")
        print("-" * 60)

        print(f"Total Trades      : {s.total_trades}")
        print(f"Winning Trades    : {s.winning_trades}")
        print(f"Losing Trades     : {s.losing_trades}")

        print()

        print(f"Win Rate          : {s.win_rate:.2f}%")
        print(f"Net Profit        : {s.net_profit:.2f}")

        print()

        print(f"Average Profit    : {s.average_profit:.2f}")
        print(f"Average Winner    : {s.average_winner:.2f}")
        print(f"Average Loser     : {s.average_loser:.2f}")

        print()

        print(f"Largest Winner    : {s.largest_winner:.2f}")
        print(f"Largest Loser     : {s.largest_loser:.2f}")

        print()

        print(
            f"Average Duration  : "
            f"{s.average_trade_duration:.1f} days"
        )

        print()

    def _print_performance(self):

        p = self.performance

        print("PERFORMANCE")
        print("-" * 60)

        print(f"Gross Profit      : {p.gross_profit:.2f}")
        print(f"Gross Loss        : {p.gross_loss:.2f}")

        if p.profit_factor == float("inf"):
            print("Profit Factor     : Infinite")
        else:
            print(f"Profit Factor     : {p.profit_factor:.2f}")

        print(f"Expectancy        : {p.expectancy:.2f}")

        if p.reward_risk_ratio == float("inf"):
            print("Reward/Risk Ratio : Infinite")
        else:
            print(
                f"Reward/Risk Ratio : "
                f"{p.reward_risk_ratio:.2f}"
            )

        print()

    def _print_footer(self):

        print("=" * 60)
        print("End of Report")
        print("=" * 60)