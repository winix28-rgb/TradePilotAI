"""
===========================================================
TradePilotAI
Backtest Result
===========================================================

Represents the outcome of a completed backtest.
"""

from dataclasses import dataclass
from datetime import datetime

from analytics.portfolio_analytics import PortfolioAnalytics
from portfolio.portfolio_manager import PortfolioManager


@dataclass(frozen=True)
class BacktestResult:
    """
    Represents the outcome of a completed backtest.
    """

    portfolio: PortfolioManager
    analytics: PortfolioAnalytics

    start_date: datetime
    end_date: datetime

    initial_cash: float
    final_value: float

    @property
    def net_profit(self) -> float:
        """
        Net realised profit.
        """
        return self.final_value - self.initial_cash

    @property
    def return_percent(self) -> float:
        """
        Percentage return.
        """

        if self.initial_cash == 0:
            return 0.0

        return (
            self.net_profit
            / self.initial_cash
        ) * 100