"""
===========================================================
TradePilotAI OS
Supply & Demand Trade Lifecycle
===========================================================

Manages an individual trade from opening to closing.

The trade is opened at the OPEN of the candle following
the valid entry candle.

This component handles:

    OPEN
      ↓
    MONITOR
      ↓
    STOP LOSS / TAKE PROFIT
      ↓
    CLOSE
      ↓
    WIN / LOSS
      ↓
    RETURN

It does not:
    - identify zones
    - identify entry candles
    - calculate the original stop loss
    - calculate the original take profit
    - manage portfolio limits
    - handle news events
    - communicate with a broker
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class TradeCandle:
    """OHLC candle used to monitor an open trade."""

    timestamp: Any

    open: float
    high: float
    low: float
    close: float


@dataclass(slots=True)
class TradeLifecycle:
    """Complete lifecycle information for one trade."""

    ticker: str
    direction: str

    entry_time: Any
    entry_price: float

    stop_loss: float
    take_profit: float

    risk_value: float

    status: str = "OPEN"

    exit_time: Any = None
    exit_price: float | None = None
    exit_reason: str | None = None

    result: str | None = None
    return_value: float | None = None
    return_percent: float | None = None


class TradeLifecycleEngine:
    """Monitor and close an individual trade."""

    def open_trade(
        self,
        ticker: str,
        direction: str,
        entry_time: Any,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_value: float,
    ) -> TradeLifecycle:
        """Create a new open trade."""

        direction = direction.upper()

        if direction not in {"BUY", "SELL"}:
            raise ValueError(
                "Trade direction must be BUY or SELL."
            )

        if entry_price <= 0:
            raise ValueError(
                "Entry price must be greater than zero."
            )

        if risk_value <= 0:
            raise ValueError(
                "Risk value must be greater than zero."
            )

        if direction == "BUY":
            if stop_loss >= entry_price:
                raise ValueError(
                    "BUY stop loss must be below entry."
                )

            if take_profit <= entry_price:
                raise ValueError(
                    "BUY take profit must be above entry."
                )

        else:
            if stop_loss <= entry_price:
                raise ValueError(
                    "SELL stop loss must be above entry."
                )

            if take_profit >= entry_price:
                raise ValueError(
                    "SELL take profit must be below entry."
                )

        return TradeLifecycle(
            ticker=ticker,
            direction=direction,
            entry_time=entry_time,
            entry_price=float(entry_price),
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            risk_value=float(risk_value),
        )

    def process_candle(
        self,
        trade: TradeLifecycle,
        candle: TradeCandle,
    ) -> TradeLifecycle:
        """
        Process one candle against an open trade.

        If both SL and TP are touched within the same candle,
        the result is treated conservatively as STOP LOSS.

        This avoids assuming an intrabar price sequence that
        OHLC data cannot prove.
        """

        if trade.status != "OPEN":
            return trade

        if trade.direction == "BUY":

            stop_hit = candle.low <= trade.stop_loss
            target_hit = candle.high >= trade.take_profit

            if stop_hit:
                self._close_trade(
                    trade=trade,
                    exit_time=candle.timestamp,
                    exit_price=trade.stop_loss,
                    exit_reason="STOP_LOSS",
                )
                return trade

            if target_hit:
                self._close_trade(
                    trade=trade,
                    exit_time=candle.timestamp,
                    exit_price=trade.take_profit,
                    exit_reason="TAKE_PROFIT",
                )
                return trade

        else:

            stop_hit = candle.high >= trade.stop_loss
            target_hit = candle.low <= trade.take_profit

            if stop_hit:
                self._close_trade(
                    trade=trade,
                    exit_time=candle.timestamp,
                    exit_price=trade.stop_loss,
                    exit_reason="STOP_LOSS",
                )
                return trade

            if target_hit:
                self._close_trade(
                    trade=trade,
                    exit_time=candle.timestamp,
                    exit_price=trade.take_profit,
                    exit_reason="TAKE_PROFIT",
                )
                return trade

        return trade

    def _close_trade(
        self,
        trade: TradeLifecycle,
        exit_time: Any,
        exit_price: float,
        exit_reason: str,
    ) -> None:
        """Close the trade and calculate its result."""

        trade.status = "CLOSED"
        trade.exit_time = exit_time
        trade.exit_price = float(exit_price)
        trade.exit_reason = exit_reason

        if trade.direction == "BUY":
            price_return = (
                trade.exit_price
                - trade.entry_price
            )
        else:
            price_return = (
                trade.entry_price
                - trade.exit_price
            )

        trade.return_value = price_return

        trade.return_percent = (
            price_return
            / trade.entry_price
            * 100.0
        )

        if exit_reason == "TAKE_PROFIT":
            trade.result = "WIN"

        elif exit_reason == "STOP_LOSS":
            trade.result = "LOSS"

        else:
            trade.result = (
                "WIN"
                if price_return > 0
                else "LOSS"
                if price_return < 0
                else "BREAKEVEN"
            )