"""
===========================================================
TradePilotAI
Risk Analyser
===========================================================

Provides high-level portfolio risk statistics based on the
equity curve.
"""

from __future__ import annotations

from analytics.drawdown import DrawdownCalculator
from backtesting.equity_point import EquityPoint


class RiskAnalyser:
    """
    Analyses portfolio risk from an equity curve.
    """

    def __init__(
        self,
        equity_curve: list[EquityPoint],
    ) -> None:

        self._equity_curve = equity_curve
        self._drawdown = DrawdownCalculator.calculate(
            equity_curve
        )

    @property
    def max_drawdown(self) -> float:
        """
        Maximum drawdown percentage.
        """
        return self._drawdown.percent

    @property
    def max_drawdown_amount(self) -> float:
        """
        Maximum drawdown amount.
        """
        return self._drawdown.amount

    @property
    def peak_equity(self) -> float:
        return self._drawdown.peak

    @property
    def trough_equity(self) -> float:
        return self._drawdown.trough

    @property
    def current_equity(self) -> float:

        if not self._equity_curve:
            return 0.0

        return self._equity_curve[-1].equity

    @property
    def current_drawdown_amount(self) -> float:

        if not self._equity_curve:
            return 0.0

        peak = max(
            point.equity
            for point in self._equity_curve
        )

        return peak - self.current_equity

    @property
    def current_drawdown(self) -> float:

        if not self._equity_curve:
            return 0.0

        peak = max(
            point.equity
            for point in self._equity_curve
        )

        if peak == 0:
            return 0.0

        return (
            self.current_drawdown_amount
            / peak
        ) * 100