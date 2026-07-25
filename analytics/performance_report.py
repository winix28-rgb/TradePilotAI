"""
===========================================================
TradePilotAI
Performance Report
===========================================================

Provides a single interface to all backtest performance
statistics.
"""

from backtesting.backtest_result import BacktestResult


class PerformanceReport:
    """
    High-level interface for analysing a completed backtest.
    """

    def __init__(self, result: BacktestResult):
        self._result = result

    @property
    def result(self) -> BacktestResult:
        return self._result

    @property
    def analytics(self):
        return self.result.analytics

    @property
    def portfolio(self):
        return self.result.portfolio

    @property
    def equity_curve(self):
        return self.result.equity_curve

    # --------------------------------------------------
    # Performance Metrics
    # --------------------------------------------------

    @property
    def win_rate(self) -> float:

        if self.analytics.total_trades == 0:
            return 0.0

        return (
            self.analytics.winning_trades
            / self.analytics.total_trades
        ) * 100

    @property
    def profit_factor(self) -> float:

        gross_profit = self.analytics.realised_profit
        gross_loss = abs(self.analytics.realised_loss)

        if gross_loss == 0:
            return 0.0

        return gross_profit / gross_loss

    @property
    def average_winner(self) -> float:

        if self.analytics.winning_trades == 0:
            return 0.0

        return (
            self.analytics.realised_profit
            / self.analytics.winning_trades
        )

    @property
    def average_loser(self) -> float:

        if self.analytics.losing_trades == 0:
            return 0.0

        return (
            self.analytics.realised_loss
            / self.analytics.losing_trades
        )

    @property
    def largest_winner(self) -> float:

        winners = [
            trade.profit
            for trade in self.portfolio.trade_history
            if trade.profit > 0
        ]

        if not winners:
            return 0.0

        return max(winners)

    @property
    def largest_loser(self) -> float:

        losers = [
            trade.profit
            for trade in self.portfolio.trade_history
            if trade.profit < 0
        ]

        if not losers:
            return 0.0

        return min(losers)

    @property
    def expectancy(self) -> float:

        if self.analytics.total_trades == 0:
            return 0.0

        net_profit = (
            self.analytics.realised_profit
            + self.analytics.realised_loss
        )

        return net_profit / self.analytics.total_trades

    # --------------------------------------------------
    # Report Output
    # --------------------------------------------------

    def to_text(self) -> str:
        """
        Return a formatted text report.
        """

        net_profit = (
            self.analytics.realised_profit
            + self.analytics.realised_loss
        )

        lines = [
            "=" * 57,
            "TradePilotAI Strategy Report",
            "=" * 57,
            "",
            "BACKTEST",
            "-" * 57,
            f"Initial Capital     £{self.result.initial_cash:,.2f}",
            f"Final Value         £{self.result.final_value:,.2f}",
            f"Net Profit          £{net_profit:,.2f}",
            "",
            "TRADING",
            "-" * 57,
            f"Total Trades        {self.analytics.total_trades}",
            f"Winning Trades      {self.analytics.winning_trades}",
            f"Losing Trades       {self.analytics.losing_trades}",
            "",
            f"Win Rate            {self.win_rate:.2f}%",
            f"Profit Factor       {self.profit_factor:.2f}",
            f"Expectancy          £{self.expectancy:,.2f}",
            "",
            f"Average Winner      £{self.average_winner:,.2f}",
            f"Average Loser       £{self.average_loser:,.2f}",
            "",
            f"Largest Winner      £{self.largest_winner:,.2f}",
            f"Largest Loser       £{self.largest_loser:,.2f}",
        ]

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_text()