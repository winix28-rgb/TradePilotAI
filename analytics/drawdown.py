"""
===========================================================
TradePilotAI
Drawdown
===========================================================

Provides utilities for calculating maximum drawdown from an
equity curve.
"""

from __future__ import annotations

from dataclasses import dataclass

from backtesting.equity_point import EquityPoint


@dataclass(frozen=True, slots=True)
class Drawdown:
    """
    Represents the maximum drawdown experienced by
    an equity curve.
    """

    peak: float
    trough: float
    amount: float
    percent: float


class DrawdownCalculator:
    """
    Calculates the maximum drawdown of an equity curve.
    """

    @staticmethod
    def calculate(
        equity_curve: list[EquityPoint],
    ) -> Drawdown:

        if not equity_curve:

            return Drawdown(
                peak=0.0,
                trough=0.0,
                amount=0.0,
                percent=0.0,
            )

        peak = equity_curve[0].equity

        max_drawdown = Drawdown(
            peak=peak,
            trough=peak,
            amount=0.0,
            percent=0.0,
        )

        for point in equity_curve:

            if point.equity > peak:
                peak = point.equity

            drawdown_amount = peak - point.equity

            if peak == 0:
                drawdown_percent = 0.0
            else:
                drawdown_percent = (
                    drawdown_amount / peak
                ) * 100

            if drawdown_amount > max_drawdown.amount:

                max_drawdown = Drawdown(
                    peak=peak,
                    trough=point.equity,
                    amount=drawdown_amount,
                    percent=drawdown_percent,
                )

        return max_drawdown