"""
===========================================================
TradePilotAI OS
Supply & Demand Trade Levels
===========================================================

Calculates the trade levels after a valid S&D entry.

Rules:

Demand / Long:
    Stop = 5 pips below the Demand zone.

Supply / Short:
    Stop = 5 pips above the Supply zone.

Take Profit:
    2 x actual entry-to-stop distance.

The actual entry is the OPEN of the candle following the
valid entry candle.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import SupplyDemandZone, ZoneType


@dataclass(slots=True)
class TradeLevels:
    """Calculated levels for a proposed S&D trade."""

    direction: str

    entry_price: float
    stop_loss: float
    take_profit: float

    risk_distance: float
    risk_value: float

    pip_size: float
    stop_pips: float


class SupplyDemandTradeLevelEngine:
    """Calculate stop loss, take profit and risk."""

    def __init__(
        self,
        pip_size: float = 0.0001,
        stop_buffer_pips: float = 5.0,
        reward_risk: float = 2.0,
        price_decimals: int = 5,
    ) -> None:
        self.pip_size = pip_size
        self.stop_buffer_pips = stop_buffer_pips
        self.reward_risk = reward_risk
        self.price_decimals = price_decimals

    def _round_price(self, price: float) -> float:
        """Round an FX price to the configured precision."""

        return round(price, self.price_decimals)

    def _round_pips(self, pips: float) -> float:
        """Round pip calculations to avoid floating-point noise."""

        return round(pips, 5)

    def calculate(
        self,
        zone: SupplyDemandZone,
        entry_price: float,
        risk_value: float = 0.0,
    ) -> TradeLevels:
        """
        Calculate trade levels from the actual trade entry.

        The entry price must be the opening price of the candle
        following the valid entry candle.
        """

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        if zone.top <= zone.bottom:
            raise ValueError(
                "Zone top must be greater than zone bottom."
            )

        buffer = (
            self.stop_buffer_pips
            * self.pip_size
        )

        if zone.zone_type == ZoneType.DEMAND:
            direction = "BUY"

            stop_loss = self._round_price(
                zone.bottom - buffer
            )

            risk_distance = self._round_price(
                entry_price - stop_loss
            )

            if risk_distance <= 0:
                raise ValueError(
                    "Demand entry must be above the stop loss."
                )

            take_profit = self._round_price(
                entry_price
                + (
                    risk_distance
                    * self.reward_risk
                )
            )

        elif zone.zone_type == ZoneType.SUPPLY:
            direction = "SELL"

            stop_loss = self._round_price(
                zone.top + buffer
            )

            risk_distance = self._round_price(
                stop_loss - entry_price
            )

            if risk_distance <= 0:
                raise ValueError(
                    "Supply entry must be below the stop loss."
                )

            take_profit = self._round_price(
                entry_price
                - (
                    risk_distance
                    * self.reward_risk
                )
            )

        else:
            raise ValueError(
                "Zone must be either DEMAND or SUPPLY."
            )

        stop_pips = self._round_pips(
            risk_distance / self.pip_size
        )

        return TradeLevels(
            direction=direction,
            entry_price=self._round_price(entry_price),
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_distance=risk_distance,
            risk_value=float(risk_value),
            pip_size=self.pip_size,
            stop_pips=stop_pips,
        )