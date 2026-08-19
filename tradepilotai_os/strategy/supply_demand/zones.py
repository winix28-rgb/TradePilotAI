"""
===========================================================
TradePilotAI OS
Supply & Demand Zone Engine
===========================================================

Creates and manages Supply/Demand zones after a structure
breakout.

This module does NOT:
    - detect entry candles
    - execute trades
    - calculate position size
    - determine take profit
    - apply news rules

Those are separate strategy components.
"""

from __future__ import annotations

from typing import Any

from .models import (
    MarketStructure,
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)


class SupplyDemandZoneEngine:
    """
    Create Supply/Demand zones from a confirmed structure.

    The engine deliberately keeps zone boundaries explicit.
    The caller supplies the structure/base candle boundaries
    identified from the price structure.
    """

    def create_demand_zone(
        self,
        symbol: str,
        structure_start_time: Any,
        structure_start_price: float,
        zone_top: float,
        zone_bottom: float,
        breakout_time: Any,
        breakout_price: float,
    ) -> SupplyDemandZone:
        """
        Create a Demand zone following a bullish breakout.

        The zone becomes active after the breakout candle has
        closed. The breakout/departure gap is not mitigation.
        """

        self._validate_zone_boundaries(
            zone_type=ZoneType.DEMAND,
            zone_top=zone_top,
            zone_bottom=zone_bottom,
            breakout_price=breakout_price,
        )

        return SupplyDemandZone(
            symbol=symbol,
            zone_type=ZoneType.DEMAND,
            top=float(zone_top),
            bottom=float(zone_bottom),
            created_at=breakout_time,
            breakout_time=breakout_time,
            status=ZoneStatus.ACTIVE,
            structure_start_time=structure_start_time,
            structure_start_price=float(structure_start_price),
            breakout_price=float(breakout_price),
        )

    def create_supply_zone(
        self,
        symbol: str,
        structure_start_time: Any,
        structure_start_price: float,
        zone_top: float,
        zone_bottom: float,
        breakout_time: Any,
        breakout_price: float,
    ) -> SupplyDemandZone:
        """
        Create a Supply zone following a bearish breakout.

        The zone becomes active after the breakout candle has
        closed. The breakout/departure gap is not mitigation.
        """

        self._validate_zone_boundaries(
            zone_type=ZoneType.SUPPLY,
            zone_top=zone_top,
            zone_bottom=zone_bottom,
            breakout_price=breakout_price,
        )

        return SupplyDemandZone(
            symbol=symbol,
            zone_type=ZoneType.SUPPLY,
            top=float(zone_top),
            bottom=float(zone_bottom),
            created_at=breakout_time,
            breakout_time=breakout_time,
            status=ZoneStatus.ACTIVE,
            structure_start_time=structure_start_time,
            structure_start_price=float(structure_start_price),
            breakout_price=float(breakout_price),
        )

    def activate_zone(
        self,
        zone: SupplyDemandZone,
        breakout_candle_closed: bool,
    ) -> SupplyDemandZone:
        """
        Activate a zone only after the breakout candle closes.

        A breakout candle closing does not constitute mitigation.
        """

        if not breakout_candle_closed:
            raise ValueError(
                "A zone cannot become active before the "
                "breakout candle has closed."
            )

        if zone.status == ZoneStatus.MITIGATED:
            raise ValueError(
                "A mitigated zone cannot be reactivated."
            )

        zone.status = ZoneStatus.ACTIVE

        return zone

    def start_retest(
        self,
        zone: SupplyDemandZone,
        timestamp: Any,
    ) -> SupplyDemandZone:
        """
        Mark the beginning of a zone retest.

        The first candle entering the zone is candle 1.
        """

        if not zone.is_active:
            return zone

        if zone.retest_started_at is None:
            zone.retest_started_at = timestamp
            zone.retest_candle_count = 1
        else:
            zone.retest_candle_count += 1

        zone.status = ZoneStatus.RETESTING

        return zone

    def mitigate_zone(
        self,
        zone: SupplyDemandZone,
        timestamp: Any,
        reason: str,
    ) -> SupplyDemandZone:
        """
        Mark an active zone as mitigated.

        This method records mitigation only. It does not decide
        whether the candle is an entry candle.

        Entry/mitigation exclusivity is handled by the entry
        engine.
        """

        if zone.status == ZoneStatus.MITIGATED:
            return zone

        if zone.status == ZoneStatus.TRADED:
            return zone

        zone.status = ZoneStatus.MITIGATED
        zone.mitigation_time = timestamp
        zone.mitigation_reason = reason

        return zone

    def mark_traded(
        self,
        zone: SupplyDemandZone,
        entry_pattern,
        entry_candle_time: Any,
        trade_start_time: Any,
        trade_start_price: float,
    ) -> SupplyDemandZone:
        """
        Mark a zone as having produced a trade.

        The actual trade begins on the candle following the
        valid entry candle.
        """

        if zone.status == ZoneStatus.MITIGATED:
            raise ValueError(
                "A mitigated zone cannot produce a trade."
            )

        zone.entry_pattern = entry_pattern
        zone.entry_candle_time = entry_candle_time
        zone.trade_start_time = trade_start_time
        zone.trade_start_price = float(trade_start_price)

        zone.entry_time = trade_start_time
        zone.entry_price = float(trade_start_price)

        zone.status = ZoneStatus.TRADED

        return zone

    @staticmethod
    def _validate_zone_boundaries(
        zone_type: ZoneType,
        zone_top: float,
        zone_bottom: float,
        breakout_price: float,
    ) -> None:
        """Validate basic zone geometry."""

        if zone_top <= zone_bottom:
            raise ValueError(
                "Zone top must be greater than zone bottom."
            )

        if zone_type == ZoneType.DEMAND:
            if breakout_price <= zone_top:
                raise ValueError(
                    "Demand breakout price must be above the zone."
                )

        if zone_type == ZoneType.SUPPLY:
            if breakout_price >= zone_bottom:
                raise ValueError(
                    "Supply breakout price must be below the zone."
                )