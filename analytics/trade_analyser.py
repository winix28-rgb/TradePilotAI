"""
===========================================================
TradePilotAI
Trade Analyser
===========================================================

Provides statistical analysis of completed trades.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable

from models.trade import Trade


class TradeAnalyser:
    """
    Performs statistical analysis on completed trades.

    The analyser is intentionally independent of the rest of
    the backtesting engine and only requires a collection of
    completed Trade objects.
    """

    def __init__(self, trades: Iterable[Trade]):
        """
        Initialise the analyser.

        Parameters
        ----------
        trades:
            Iterable of completed Trade objects.
        """

        self._trades = tuple(trades)

        self._winners = tuple(
            trade
            for trade in self._trades
            if trade.profit > 0
        )

        self._losers = tuple(
            trade
            for trade in self._trades
            if trade.profit < 0
        )

    # --------------------------------------------------
    # Trade Counts
    # --------------------------------------------------

    @property
    def total_trades(self) -> int:
        """Return the total number of completed trades."""
        return len(self._trades)

    @property
    def winning_trades(self) -> int:
        """Return the number of winning trades."""
        return len(self._winners)

    @property
    def losing_trades(self) -> int:
        """Return the number of losing trades."""
        return len(self._losers)

    # --------------------------------------------------
    # Profit Statistics
    # --------------------------------------------------

    @property
    def realised_profit(self) -> float:
        """Return total realised profit."""
        return sum(
            trade.profit
            for trade in self._winners
        )

    @property
    def realised_loss(self) -> float:
        """Return total realised loss."""
        return sum(
            trade.profit
            for trade in self._losers
        )

    @property
    def net_profit(self) -> float:
        """Return overall net profit."""
        return (
            self.realised_profit
            + self.realised_loss
        )

    @property
    def average_winner(self) -> float:
        """Return the average winning trade."""

        if self.winning_trades == 0:
            return 0.0

        return (
            self.realised_profit
            / self.winning_trades
        )

    @property
    def average_loser(self) -> float:
        """Return the average losing trade."""

        if self.losing_trades == 0:
            return 0.0

        return (
            self.realised_loss
            / self.losing_trades
        )

    @property
    def largest_winner(self) -> float:
        """Return the largest winning trade."""

        if not self._winners:
            return 0.0

        return max(
            trade.profit
            for trade in self._winners
        )

    @property
    def largest_loser(self) -> float:
        """Return the largest losing trade."""

        if not self._losers:
            return 0.0

        return min(
            trade.profit
            for trade in self._losers
        )
            # --------------------------------------------------
    # Performance Metrics
    # --------------------------------------------------

    @property
    def win_rate(self) -> float:
        """
        Return the percentage of winning trades.
        """

        if self.total_trades == 0:
            return 0.0

        return (
            self.winning_trades
            / self.total_trades
        ) * 100

    @property
    def profit_factor(self) -> float:
        """
        Return the profit factor.
        """

        gross_loss = abs(self.realised_loss)

        if gross_loss == 0:
            return 0.0

        return self.realised_profit / gross_loss

    @property
    def expectancy(self) -> float:
        """
        Return the average profit per trade.
        """

        if self.total_trades == 0:
            return 0.0

        return self.net_profit / self.total_trades

    # --------------------------------------------------
    # Duration Statistics
    # --------------------------------------------------

    @property
    def average_duration(self) -> timedelta:
        """
        Return the average trade duration.
        """

        if self.total_trades == 0:
            return timedelta(0)

        total_seconds = sum(
            trade.duration.total_seconds()
            for trade in self._trades
        )

        return timedelta(
            seconds=total_seconds / self.total_trades
        )

    @property
    def longest_duration(self) -> timedelta:
        """
        Return the longest trade duration.
        """

        if not self._trades:
            return timedelta(0)

        return max(
            trade.duration
            for trade in self._trades
        )

    @property
    def shortest_duration(self) -> timedelta:
        """
        Return the shortest trade duration.
        """

        if not self._trades:
            return timedelta(0)

        return min(
            trade.duration
            for trade in self._trades
        )

    # --------------------------------------------------
    # Convenience
    # --------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of completed trades.
        """

        return self.total_trades

    def __bool__(self) -> bool:
        """
        Return True if any trades exist.
        """

        return self.total_trades > 0