"""
===========================================================
TradePilotAI
Markdown Formatter
===========================================================

Formats PerformanceReport objects as Markdown.
"""


class MarkdownFormatter:
    """
    Formats a PerformanceReport into GitHub-compatible Markdown.
    """

    def __init__(self, report):
        self.report = report

    def to_markdown(self) -> str:

        net_profit = (
            self.report.analytics.realised_profit
            + self.report.analytics.realised_loss
        )

        return f"""# TradePilotAI Strategy Report

## Backtest

| Metric | Value |
|--------|------:|
| Initial Capital | £{self.report.result.initial_cash:,.2f} |
| Final Value | £{self.report.result.final_value:,.2f} |
| Net Profit | £{net_profit:,.2f} |

## Trading

| Metric | Value |
|--------|------:|
| Total Trades | {self.report.analytics.total_trades} |
| Winning Trades | {self.report.analytics.winning_trades} |
| Losing Trades | {self.report.analytics.losing_trades} |
| Win Rate | {self.report.win_rate:.2f}% |
| Profit Factor | {self.report.profit_factor:.2f} |
| Expectancy | £{self.report.expectancy:,.2f} |
| Average Winner | £{self.report.average_winner:,.2f} |
| Average Loser | £{self.report.average_loser:,.2f} |
| Largest Winner | £{self.report.largest_winner:,.2f} |
| Largest Loser | £{self.report.largest_loser:,.2f} |
"""