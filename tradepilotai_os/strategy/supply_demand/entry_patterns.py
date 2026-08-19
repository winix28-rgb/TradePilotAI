"""
===========================================================
TradePilotAI OS
Supply & Demand Entry Pattern Engine
===========================================================

Identifies the three valid S&D entry patterns:

    1. Pin Bar
    2. Engulfing
    3. Three-Candle Reversal

This module ONLY appraises candles.

It does NOT:
    - decide whether a zone is being retested
    - determine mitigation
    - execute trades
    - calculate risk
    - calculate stop loss
    - calculate take profit

The first valid pattern found during the retest will later
become the entry candle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import EntryPattern, ZoneType


@dataclass(slots=True)
class Candle:
    """OHLC representation of one candle."""

    timestamp: Any

    open: float
    high: float
    low: float
    close: float

    @property
    def body_size(self) -> float:
        """Absolute size of the candle body."""

        return abs(self.close - self.open)

    @property
    def range_size(self) -> float:
        """Complete High-to-Low candle range."""

        return self.high - self.low

    @property
    def bullish(self) -> bool:
        """True when the candle closes above its open."""

        return self.close > self.open

    @property
    def bearish(self) -> bool:
        """True when the candle closes below its open."""

        return self.close < self.open


class SupplyDemandEntryPatternEngine:
    """
    Appraise candles for the three approved S&D entry patterns.
    """

    PIN_BAR_MAX_BODY_PERCENT = 0.50

    # ---------------------------------------------------------
    # Public appraisal methods
    # ---------------------------------------------------------

    def identify_pin_bar(
        self,
        candle: Candle,
        zone_type: ZoneType,
    ) -> bool:
        """
        Determine whether a candle is a valid Pin Bar.

        The agreed body criterion is:

            body <= 50% of complete candle range

        Demand:
            rejection from below
            lower wick is dominant
            body is toward the top

        Supply:
            rejection from above
            upper wick is dominant
            body is toward the bottom
        """

        if candle.range_size <= 0:
            return False

        body_ratio = (
            candle.body_size / candle.range_size
        )

        if body_ratio > self.PIN_BAR_MAX_BODY_PERCENT:
            return False

        upper_wick = self._upper_wick(candle)
        lower_wick = self._lower_wick(candle)

        if zone_type == ZoneType.DEMAND:
            return (
                lower_wick > upper_wick
                and candle.close >= candle.open
            )

        if zone_type == ZoneType.SUPPLY:
            return (
                upper_wick > lower_wick
                and candle.close <= candle.open
            )

        return False

    def identify_engulfing(
        self,
        previous: Candle,
        current: Candle,
        zone_type: ZoneType,
    ) -> bool:
        """
        Determine whether the current candle forms an engulfing
        pattern against the previous candle.

        The appraisal uses the candle bodies.

        Demand:
            previous bearish
            current bullish
            current body engulfs previous body

        Supply:
            previous bullish
            current bearish
            current body engulfs previous body
        """

        previous_body_high = max(
            previous.open,
            previous.close,
        )

        previous_body_low = min(
            previous.open,
            previous.close,
        )

        current_body_high = max(
            current.open,
            current.close,
        )

        current_body_low = min(
            current.open,
            current.close,
        )

        current_engulfs_previous = (
            current_body_high >= previous_body_high
            and current_body_low <= previous_body_low
        )

        if not current_engulfs_previous:
            return False

        if zone_type == ZoneType.DEMAND:
            return (
                previous.bearish
                and current.bullish
            )

        if zone_type == ZoneType.SUPPLY:
            return (
                previous.bullish
                and current.bearish
            )

        return False

    def identify_three_candle_reversal(
        self,
        first: Candle,
        second: Candle,
        third: Candle,
        zone_type: ZoneType,
    ) -> bool:
        """
        Determine whether three consecutive candles form the
        agreed three-candle reversal.

        Bullish / Demand:

            Candle 1 = bearish
            Candle 2 = bullish
            Candle 3 = bullish
            Candle 3 closes above Candle 1 open

        Bearish / Supply:

            Candle 1 = bullish
            Candle 2 = bearish
            Candle 3 = bearish
            Candle 3 closes below Candle 1 open
        """

        if zone_type == ZoneType.DEMAND:
            return (
                first.bearish
                and second.bullish
                and third.bullish
                and third.close > first.open
            )

        if zone_type == ZoneType.SUPPLY:
            return (
                first.bullish
                and second.bearish
                and third.bearish
                and third.close < first.open
            )

        return False

    # ---------------------------------------------------------
    # Combined appraisal
    # ---------------------------------------------------------

    def identify_first_valid_pattern(
        self,
        candles: list[Candle],
        zone_type: ZoneType,
    ) -> EntryPattern | None:
        """
        Return the first valid entry pattern.

        The patterns are evaluated in chronological order.

        For a single candle:
            Pin Bar

        For two candles:
            Engulfing

        For three candles:
            Three-Candle Reversal

        The caller is responsible for ensuring these candles
        belong to the active zone retest.
        """

        if not candles:
            return None

        # -----------------------------------------------------
        # Pin Bar
        # -----------------------------------------------------

        latest = candles[-1]

        if self.identify_pin_bar(
            latest,
            zone_type,
        ):
            return EntryPattern.PIN_BAR

        # -----------------------------------------------------
        # Engulfing
        # -----------------------------------------------------

        if len(candles) >= 2:
            previous = candles[-2]

            if self.identify_engulfing(
                previous,
                latest,
                zone_type,
            ):
                return EntryPattern.ENGULFING

        # -----------------------------------------------------
        # Three-Candle Reversal
        # -----------------------------------------------------

        if len(candles) >= 3:
            first = candles[-3]
            second = candles[-2]
            third = candles[-1]

            if self.identify_three_candle_reversal(
                first,
                second,
                third,
                zone_type,
            ):
                return EntryPattern.THREE_CANDLE_REVERSAL

        return None

    # ---------------------------------------------------------
    # Wick calculations
    # ---------------------------------------------------------

    @staticmethod
    def _upper_wick(candle: Candle) -> float:
        """Return the upper wick size."""

        return candle.high - max(
            candle.open,
            candle.close,
        )

    @staticmethod
    def _lower_wick(candle: Candle) -> float:
        """Return the lower wick size."""

        return min(
            candle.open,
            candle.close,
        ) - candle.low