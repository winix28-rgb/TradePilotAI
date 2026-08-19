"""
===========================================================
TradePilotAI OS
Supply & Demand Zone Detector
===========================================================

Creates Supply/Demand zones from an identified:

    1. Structure-start candle
    2. Breakout candle

The complete automatic identification of the structure-start
candle will be added once the H1 visual structure rules are
fully encoded.

Zone boundaries use the COMPLETE candle range:

    Zone High = candle High
    Zone Low  = candle Low

Wicks are included.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import SupplyDemandZone, ZoneType
from .zones import SupplyDemandZoneEngine


@dataclass(slots=True)
class ZoneDetectionInput:
    """
    Explicit information describing a confirmed structure break.
    """

    symbol: str

    structure_start_time: Any
    structure_start_open: float
    structure_start_high: float
    structure_start_low: float
    structure_start_close: float

    breakout_time: Any
    breakout_open: float
    breakout_high: float
    breakout_low: float
    breakout_close: float

    bullish_breakout: bool


class SupplyDemandZoneDetector:
    """
    Create a Supply/Demand zone from a confirmed structure break.

    This component does not detect entry candles or mitigation.
    """

    def __init__(
        self,
        zone_engine: SupplyDemandZoneEngine | None = None,
    ) -> None:
        self.zone_engine = (
            zone_engine
            if zone_engine is not None
            else SupplyDemandZoneEngine()
        )

    def detect(
        self,
        setup: ZoneDetectionInput,
    ) -> SupplyDemandZone:
        """
        Create the zone from the structure-start candle.

        The entire structure-start candle is used:

            High = zone top
            Low  = zone bottom
        """

        self._validate_setup(setup)

        zone_top = float(setup.structure_start_high)
        zone_bottom = float(setup.structure_start_low)

        if setup.bullish_breakout:
            return self.zone_engine.create_demand_zone(
                symbol=setup.symbol,
                structure_start_time=setup.structure_start_time,
                structure_start_price=setup.structure_start_close,
                zone_top=zone_top,
                zone_bottom=zone_bottom,
                breakout_time=setup.breakout_time,
                breakout_price=setup.breakout_close,
            )

        return self.zone_engine.create_supply_zone(
            symbol=setup.symbol,
            structure_start_time=setup.structure_start_time,
            structure_start_price=setup.structure_start_close,
            zone_top=zone_top,
            zone_bottom=zone_bottom,
            breakout_time=setup.breakout_time,
            breakout_price=setup.breakout_close,
        )

    @staticmethod
    def _validate_setup(
        setup: ZoneDetectionInput,
    ) -> None:
        """Validate the supplied structure-break information."""

        if setup.structure_start_high <= setup.structure_start_low:
            raise ValueError(
                "Structure-start candle High must be above Low."
            )

        if setup.bullish_breakout:
            if setup.breakout_close <= setup.structure_start_high:
                raise ValueError(
                    "Bullish breakout must close above the "
                    "structure-start candle High."
                )

        else:
            if setup.breakout_close >= setup.structure_start_low:
                raise ValueError(
                    "Bearish breakout must close below the "
                    "structure-start candle Low."
                )