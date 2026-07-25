"""
===========================================================
TradePilotAI
Report Formatter
===========================================================

Responsible for formatting PerformanceReport objects.
"""

from typing import Any


class ReportFormatter:
    """
    Formats PerformanceReport objects into various output
    formats.

    Initially supports plain text output.
    """

    def __init__(self, report: Any):
        self.report = report

    def to_text(self) -> str:
        """
        Return a formatted text report.
        """

        net_profit = (
            self.report.analytics.realised_profit
            + self.report.analytics.realised_loss
        )

        lines = [
            "=" * 57,
            "TradePilotAI Strategy Report",
            "=" * 57,
            "",
            "BACKTEST",
            "-" * 57,
            f"Initial Capital     £{self.report.result.initial_cash:,.2f}",
            f"Final Value         £{self.report.result.final_value:,.2f}",
            f"Net Profit          £{net_profit:,.2f}",
            "",
            "TRADING",
            "-" * 57,
            f"Total Trades        {self.report.analytics.total_trades}",
            f"Winning Trades      {self.report.analytics.winning_trades}",
            f"Losing Trades       {self.report.analytics.losing_trades}",
            "",
            f"Win Rate            {self.report.win_rate:.2f}%",
            f"Profit Factor       {self.report.profit_factor:.2f}",
            f"Expectancy          £{self.report.expectancy:,.2f}",
            "",
            f"Average Winner      £{self.report.average_winner:,.2f}",
            f"Average Loser       £{self.report.average_loser:,.2f}",
            "",
            f"Largest Winner      £{self.report.largest_winner:,.2f}",
            f"Largest Loser       £{self.report.largest_loser:,.2f}",
        ]

        return "\n".join(lines)