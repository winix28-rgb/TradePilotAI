"""
===========================================================
TradePilotAI
Performance Report
===========================================================

Provides a single interface to all backtest performance
statistics.
"""

from analytics.trade_analyser import TradeAnalyser
from reporting.report_formatter import ReportFormatter


class PerformanceReport:
    """
    High-level interface for analysing a completed backtest.
    """

    def __init__(self, result: BacktestResult):
        self._result = result
        self._trade_analysis = TradeAnalyser(
            result.portfolio.trade_history
        )

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

    @property
    def trade_analysis(self) -> TradeAnalyser:
        """
        Return the trade analyser.
        """
        return self._trade_analysis

    # --------------------------------------------------
    # Performance Metrics
    # --------------------------------------------------

    @property
    def win_rate(self) -> float:
        return self.trade_analysis.win_rate

    @property
    def profit_factor(self) -> float:
        return self.trade_analysis.profit_factor

    @property
    def average_winner(self) -> float:
        return self.trade_analysis.average_winner

    @property
    def average_loser(self) -> float:
        return self.trade_analysis.average_loser

    @property
    def largest_winner(self) -> float:
        return self.trade_analysis.largest_winner

    @property
    def largest_loser(self) -> float:
        return self.trade_analysis.largest_loser

    @property
    def expectancy(self) -> float:
        return self.trade_analysis.expectancy

    # --------------------------------------------------
    # Report Output
    # --------------------------------------------------

    def to_text(self) -> str:
        """
        Return a formatted text report.
        """
        return ReportFormatter(self).to_text()

    def __str__(self) -> str:
        return self.to_text()