"""
===========================================================
TradePilotAI
EMA Indicator
===========================================================

Calculates Exponential Moving Average.
"""

from __future__ import annotations


def calculate_ema(
    prices: list[float],
    period: int,
) -> list[float]:

    if period <= 0:
        raise ValueError(
            "EMA period must be greater than zero."
        )

    if not prices:
        return []

    multiplier = 2 / (period + 1)

    ema_values = []

    ema = prices[0]

    ema_values.append(ema)

    for price in prices[1:]:

        ema = (
            (price - ema) * multiplier
            + ema
        )

        ema_values.append(ema)

    return ema_values