"""
===========================================================
TradePilotAI OS
Supply & Demand Retest Engine
===========================================================

Manages the rebound / retracement into an active
Supply/Demand zone.

RULE:

The first four retest candles are the entry-pattern
opportunity window.

A pattern may BEGIN within those four candles.

Once a valid multi-candle pattern has begun, it is allowed
to complete without an additional candle limit.

Examples:

    Candle 3 -> reversal begins
    Candle 4 -> reversal continues
    Candle 5 -> reversal completes

or:

    Candle 4 -> reversal begins
    Candle 5 -> reversal continues
    Candle 6 -> reversal completes

The entry candle is the candle on which the pattern
actually completes.

The following candle is the trade-start candle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import SupplyDemandZone, ZoneStatus


@dataclass(slots=True)
class RetestCandle:
    """Information about one candle during a zone retest."""

    timestamp: Any
    open: float
    high: float
    low: float
    close: float

    candle_number: int


class SupplyDemandRetestEngine:
    """
    Manage the Supply/Demand retest process.

    The first four candles form the entry opportunity window.

    A completed pattern may occur within those four candles,
    or a multi-candle pattern may begin within those four
    candles and complete afterwards.
    """

    ENTRY_OPPORTUNITY_CANDLES = 4

    def start_retest(
        self,
        zone: SupplyDemandZone,
        candle: RetestCandle,
    ) -> RetestCandle:
        """
        Start a retest when the first candle returns into
        the active zone.

        The first retest candle is candle 1.
        """

        if not zone.is_active:
            raise ValueError(
                "A retest cannot start on an inactive zone."
            )

        if not self._candle_touches_zone(zone, candle):
            raise ValueError(
                "The candle does not return into the zone."
            )

        zone.status = ZoneStatus.RETESTING
        zone.retest_started_at = candle.timestamp
        zone.retest_candle_count = 1

        return RetestCandle(
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            candle_number=1,
        )

    def process_retest_candle(
        self,
        zone: SupplyDemandZone,
        candle: RetestCandle,
    ) -> RetestCandle:
        """
        Process the next retest candle.

        The first four candles are the normal entry window.

        After candle four, processing is still permitted because
        a multi-candle entry pattern may have started during the
        first four candles and still needs to complete.
        """

        if zone.status != ZoneStatus.RETESTING:
            raise ValueError(
                "Zone is not currently being retested."
            )

        zone.retest_candle_count += 1

        return RetestCandle(
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            candle_number=zone.retest_candle_count,
        )

    def within_entry_opportunity_window(
        self,
        candle_number: int,
    ) -> bool:
        """
        Return True when the candle is within the first
        four retest candles.
        """

        return (
            candle_number
            <= self.ENTRY_OPPORTUNITY_CANDLES
        )

    @staticmethod
    def _candle_touches_zone(
        zone: SupplyDemandZone,
        candle: RetestCandle,
    ) -> bool:
        """Return True when the candle range overlaps the zone."""

        return (
            candle.high >= zone.bottom
            and candle.low <= zone.top
        )