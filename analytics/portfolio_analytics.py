"""
===========================================================
TradePilotAI
Portfolio Analytics
===========================================================

Calculates performance statistics from a portfolio.
"""

from portfolio.portfolio_manager import PortfolioManager


class PortfolioAnalytics:
    """
    Provides performance statistics for a portfolio.
    """

    def __init__(self, portfolio: PortfolioManager):
        self._portfolio = portfolio

    @property
    def portfolio(self) -> PortfolioManager:
        return self._portfolio

    @property
    def total_trades(self) -> int:
        """
        Total completed trades.
        """
        return len(self.portfolio.trade_history)

    @property
    def winning_trades(self) -> int:
        """
        Number of profitable trades.
        """
        return sum(
            1
            for trade in self.portfolio.trade_history
            if trade.profit > 0
        )

    @property
    def losing_trades(self) -> int:
        """
        Number of losing trades.
        """
        return sum(
            1
            for trade in self.portfolio.trade_history
            if trade.profit < 0
        )

    @property
    def realised_profit(self) -> float:
        """
        Total realised profit.
        """
        return sum(
            trade.profit
            for trade in self.portfolio.trade_history
            if trade.profit > 0
        )

    @property
    def realised_loss(self) -> float:
        """
        Total realised loss.
        """
        return sum(
            trade.profit
            for trade in self.portfolio.trade_history
            if trade.profit < 0
        )

    @property
    def net_profit(self) -> float:
        """
        Net realised profit.
        """
        return sum(
            trade.profit
            for trade in self.portfolio.trade_history
        )