"""
===========================================================
TradePilotAI OS
Supply & Demand Entry Engine
===========================================================

Connects the retest process with the three approved
S&D entry patterns.

ENTRY WINDOW RULE
-----------------

The first four retest candles are the entry-pattern
opportunity window.

A pattern must BEGIN within those first four candles.

Once a multi-candle pattern has begun, it is allowed to
COMPLETE without an additional candle limit.

Examples:

    Candle 3 -> 3-candle reversal begins
    Candle 4 -> second candle
    Candle 5 -> third candle = ENTRY

or:

    Candle 4 -> 3-candle reversal begins
    Candle 5 -> second candle
    Candle 6 -> third candle = ENTRY

The following candle opens the actual trade.

The entry candle and trade-start candle are therefore
always different candles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .entry_patterns import (
    Candle,
    SupplyDemandEntryPatternEngine,
)
from .models import (
    EntryPattern,
    SupplyDemandZone,
    ZoneType,
)
from .retest import (
    RetestCandle,
    SupplyDemandRetestEngine,
)


@dataclass(slots=True)
class EntryDecision:
    """Result of evaluating an S&D retest."""

    valid: bool = False

    pattern: EntryPattern | None = None

    entry_candle_time: Any = None
    entry_candle_close: float | None = None

    trade_start_time: Any = None
    trade_start_price: float | None = None


class SupplyDemandEntryEngine:
    """
    Connect the retest process with the entry-pattern engine.

    The engine looks for the FIRST COMPLETED valid pattern.

    A pattern may only START during retest candles 1-4.

    Once started, the pattern is allowed to complete without
    an additional candle limit.
    """

    ENTRY_OPPORTUNITY_CANDLES = 4

    def __init__(
        self,
        retest_engine: SupplyDemandRetestEngine | None = None,
        pattern_engine: SupplyDemandEntryPatternEngine | None = None,
    ) -> None:

        self.retest_engine = (
            retest_engine
            if retest_engine is not None
            else SupplyDemandRetestEngine()
        )

        self.pattern_engine = (
            pattern_engine
            if pattern_engine is not None
            else SupplyDemandEntryPatternEngine()
        )

    # ---------------------------------------------------------
    # Public entry evaluation
    # ---------------------------------------------------------

    def evaluate(
        self,
        zone: SupplyDemandZone,
        candles: list[RetestCandle],
        zone_type: ZoneType,
    ) -> EntryDecision:
        """
        Evaluate the current retest for the first completed
        valid entry pattern.

        Rules:

        Pin Bar:
            Must occur on candle 1-4.

        Engulfing:
            The pattern must begin within candle 1-4.
            Therefore an engulfing pattern can complete after
            candle 4 if its first candle occurred within the
            opportunity window.

        Three-Candle Reversal:
            The first candle must occur within candle 1-4.
            Completion can therefore occur after candle 4.

        The earliest completed valid pattern is returned.
        """

        if not candles:
            return EntryDecision()

        pattern_candles = [
            self._to_pattern_candle(candle)
            for candle in candles
        ]

        # -----------------------------------------------------
        # Examine completed patterns in chronological order.
        #
        # This is important:
        #
        # We do NOT simply examine the latest candle.
        #
        # We want the FIRST valid completed pattern.
        # -----------------------------------------------------

        for index, current in enumerate(pattern_candles):

            current_number = self._candle_number(
                candles[index],
                index,
            )

            # -------------------------------------------------
            # PIN BAR
            #
            # A Pin Bar is a one-candle pattern.
            #
            # Therefore the candle itself must be inside
            # the first four-candle opportunity window.
            # -------------------------------------------------

            if current_number <= self.ENTRY_OPPORTUNITY_CANDLES:

                if self.pattern_engine.identify_pin_bar(
                    current,
                    zone_type,
                ):
                    return self._entry_decision(
                        candles[index],
                        EntryPattern.PIN_BAR,
                    )

            # -------------------------------------------------
            # ENGULFING
            #
            # The pattern starts on the previous candle.
            #
            # Therefore the previous candle must be within
            # the first four opportunity candles.
            # -------------------------------------------------

            if index >= 1:

                previous = pattern_candles[index - 1]

                previous_number = self._candle_number(
                    candles[index - 1],
                    index - 1,
                )

                if (
                    previous_number
                    <= self.ENTRY_OPPORTUNITY_CANDLES
                    and self.pattern_engine.identify_engulfing(
                        previous,
                        current,
                        zone_type,
                    )
                ):
                    return self._entry_decision(
                        candles[index],
                        EntryPattern.ENGULFING,
                    )

            # -------------------------------------------------
            # THREE-CANDLE REVERSAL
            #
            # The first candle must be within the first four
            # opportunity candles.
            #
            # Once started, completion can happen later.
            # -------------------------------------------------

            if index >= 2:

                first = pattern_candles[index - 2]
                second = pattern_candles[index - 1]
                third = pattern_candles[index]

                first_number = self._candle_number(
                    candles[index - 2],
                    index - 2,
                )

                if (
                    first_number
                    <= self.ENTRY_OPPORTUNITY_CANDLES
                    and self.pattern_engine.identify_three_candle_reversal(
                        first,
                        second,
                        third,
                        zone_type,
                    )
                ):
                    return self._entry_decision(
                        candles[index],
                        EntryPattern.THREE_CANDLE_REVERSAL,
                    )

        return EntryDecision()

    # ---------------------------------------------------------
    # Trade start
    # ---------------------------------------------------------

    def start_trade(
        self,
        zone: SupplyDemandZone,
        decision: EntryDecision,
        following_candle: RetestCandle,
    ) -> EntryDecision:
        """
        Start the trade on the OPEN of the candle following
        the valid entry candle.
        """

        if not decision.valid:
            raise ValueError(
                "Cannot start a trade without a valid entry candle."
            )

        if (
            following_candle.timestamp
            == decision.entry_candle_time
        ):
            raise ValueError(
                "Trade-start candle must be different from "
                "the entry candle."
            )

        decision.trade_start_time = (
            following_candle.timestamp
        )

        decision.trade_start_price = (
            following_candle.open
        )

        zone.entry_pattern = decision.pattern
        zone.entry_candle_time = (
            decision.entry_candle_time
        )
        zone.entry_candle_close = (
            decision.entry_candle_close
        )

        zone.trade_start_time = (
            following_candle.timestamp
        )

        zone.trade_start_price = (
            following_candle.open
        )

        zone.entry_time = (
            following_candle.timestamp
        )

        zone.entry_price = (
            following_candle.open
        )

        return decision

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _to_pattern_candle(
        candle: RetestCandle,
    ) -> Candle:
        """Convert a RetestCandle into a pattern Candle."""

        return Candle(
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
        )

    @staticmethod
    def _candle_number(
        candle: RetestCandle,
        fallback_index: int,
    ) -> int:
        """
        Return the retest candle number.

        RetestCandle normally contains its own candle number.
        The fallback protects against older test fixtures.
        """

        if candle.candle_number > 0:
            return candle.candle_number

        return fallback_index + 1

    @staticmethod
    def _entry_decision(
        candle: RetestCandle,
        pattern: EntryPattern,
    ) -> EntryDecision:
        """Create an EntryDecision for a completed pattern."""

        return EntryDecision(
            valid=True,
            pattern=pattern,
            entry_candle_time=candle.timestamp,
            entry_candle_close=candle.close,
        )