"""
===========================================================
TradePilotAI
Statistics Engine
===========================================================

Purpose
-------
Calculates basic statistics from completed trades.

The Statistics class is intentionally independent of any
trading strategy. It only requires a list of completed
Trade objects.
"""

from dataclasses import dataclass
from typing import List

from models.trade import Trade


@dataclass(slots=True)
class Statistics:

    trades: List[Trade]

    @property
    def total_trades(self) -> int:
        return len(self.trades)

    @property
    def winning_trades(self) -> int:
        return sum(1 for trade in self.trades if trade.profit > 0)

    @property
    def losing_trades(self) -> int:
        return sum(1 for trade in self.trades if trade.profit <= 0)

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0

        return (self.winning_trades / self.total_trades) * 100

    @property
    def net_profit(self) -> float:
        return sum(trade.profit for trade in self.trades)

    @property
    def average_profit(self) -> float:
        if self.total_trades == 0:
            return 0.0

        return self.net_profit / self.total_trades

    @property
    def average_winner(self) -> float:
        winners = [trade.profit for trade in self.trades if trade.profit > 0]

        if not winners:
            return 0.0

        return sum(winners) / len(winners)

    @property
    def average_loser(self) -> float:
        losers = [trade.profit for trade in self.trades if trade.profit <= 0]

        if not losers:
            return 0.0

        return sum(losers) / len(losers)

    @property
    def largest_winner(self) -> float:
        winners = [trade.profit for trade in self.trades if trade.profit > 0]

        return max(winners, default=0.0)

    @property
    def largest_loser(self) -> float:
        losers = [trade.profit for trade in self.trades if trade.profit <= 0]

        return min(losers, default=0.0)

    @property
    def average_trade_duration(self) -> float:
        if self.total_trades == 0:
            return 0.0

        return (
            sum(trade.duration_days for trade in self.trades)
            / self.total_trades
        )