"""
===========================================================
TradePilotAI
RSI Indicator
===========================================================

Calculates Relative Strength Index.
"""

from __future__ import annotations


def calculate_rsi(
    prices: list[float],
    period: int = 14,
) -> list[float]:
    """
    Calculate RSI values.

    Returns a list the same length as prices.
    """

    if period <= 0:
        raise ValueError(
            "RSI period must be greater than zero."
        )

    if not prices:
        return []

    if len(prices) <= period:
        return [50.0] * len(prices)


    rsi_values = [50.0] * len(prices)


    gains: list[float] = []
    losses: list[float] = []


    # Calculate price changes

    for index in range(1, len(prices)):

        change = (
            prices[index]
            -
            prices[index - 1]
        )

        if change > 0:

            gains.append(change)
            losses.append(0.0)

        else:

            gains.append(0.0)
            losses.append(abs(change))


    average_gain = (
        sum(gains[:period])
        /
        period
    )

    average_loss = (
        sum(losses[:period])
        /
        period
    )


    # RSI calculation

    for price_index in range(
        period + 1,
        len(prices),
    ):

        change_index = price_index - 1


        if average_loss == 0:

            rsi_values[price_index] = 100.0

        else:

            relative_strength = (
                average_gain
                /
                average_loss
            )

            rsi_values[price_index] = (
                100
                -
                (
                    100
                    /
                    (
                        1
                        +
                        relative_strength
                    )
                )
            )


        gain = gains[change_index]

        loss = losses[change_index]


        average_gain = (
            (
                average_gain
                *
                (period - 1)
            )
            +
            gain
        ) / period


        average_loss = (
            (
                average_loss
                *
                (period - 1)
            )
            +
            loss
        ) / period


    return rsi_values