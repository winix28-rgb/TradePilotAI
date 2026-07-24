"""
===========================================================
TradePilotAI
Performance Metrics
===========================================================

Purpose
-------
Calculates advanced performance metrics from completed trades.
"""

from dataclasses import dataclass

from backtesting.statistics import Statistics


@dataclass(slots=True)
class Performance:

    statistics: Statistics

    @property
    def gross_profit(self) -> float:
        return sum(
            trade.profit
            for trade in self.statistics.trades
            if trade.profit > 0
        )

    @property
    def gross_loss(self) -> float:
        return abs(sum(
            trade.profit
            for trade in self.statistics.trades
            if trade.profit < 0
        ))

    @property
    def profit_factor(self) -> float:
        if self.gross_loss == 0:
            return float("inf")

        return self.gross_profit / self.gross_loss

    @property
    def expectancy(self) -> float:
        return self.statistics.average_profit

    @property
    def reward_risk_ratio(self) -> float:

        average_loss = abs(self.statistics.average_loser)

        if average_loss == 0:
            return float("inf")

        return self.statistics.average_winner / average_loss