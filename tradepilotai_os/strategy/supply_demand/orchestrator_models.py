"""
===========================================================
TradePilotAI OS
Supply & Demand Orchestrator Models
===========================================================

Step 1 / Step 2 of the S&D orchestration process.

This module defines the state carried by the S&D strategy
orchestrator.

IMPORTANT
---------

This module does NOT:

- identify zones
- identify breakouts
- identify retracements
- identify entry patterns
- calculate trade levels
- execute trades

It only represents the current state of the strategy.

The actual strategy logic remains inside the existing
specialist engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .entry_engine import EntryDecision
from .models import SupplyDemandZone
from .trade_levels import TradeLevels

from tradepilotai_os.trading.trade_lifecycle import (
    TradeLifecycle,
)


class StrategyStage(str, Enum):
    """
    Current stage of the Supply & Demand strategy.
    """

    IDLE = "IDLE"

    ZONE_IDENTIFIED = "ZONE_IDENTIFIED"

    BREAKOUT_CONFIRMED = "BREAKOUT_CONFIRMED"

    RETESTING = "RETESTING"

    LOOKING_FOR_ENTRY = "LOOKING_FOR_ENTRY"

    ENTRY_IDENTIFIED = "ENTRY_IDENTIFIED"

    WAITING_FOR_TRADE_START = "WAITING_FOR_TRADE_START"

    TRADE_OPEN = "TRADE_OPEN"

    TRADE_CLOSED = "TRADE_CLOSED"


class TradeStatus(str, Enum):
    """
    Current status of the trade lifecycle.
    """

    NOT_STARTED = "NOT_STARTED"

    WAITING = "WAITING"

    OPEN = "OPEN"

    CLOSED = "CLOSED"


@dataclass(slots=True)
class SupplyDemandOrchestratorState:
    """
    Complete state carried by the S&D orchestrator.

    The state deliberately keeps strategy stages separate
    from trade status.

    This allows us to distinguish between:

        ENTRY_IDENTIFIED
        WAITING_FOR_TRADE_START

    and:

        TRADE_OPEN

    and:

        TRADE_CLOSED
    """

    # -------------------------------------------------------
    # Current processing state
    # -------------------------------------------------------

    timestamp: Any = None

    stage: StrategyStage = StrategyStage.IDLE

    # -------------------------------------------------------
    # Active zone
    # -------------------------------------------------------

    active_zone: SupplyDemandZone | None = None

    # -------------------------------------------------------
    # Retest state
    # -------------------------------------------------------

    retest_started: bool = False

    retest_candle_count: int = 0

    # -------------------------------------------------------
    # Entry state
    # -------------------------------------------------------

    entry_decision: EntryDecision | None = None

    entry_candle_time: Any = None

    entry_candle_close: float | None = None

    # -------------------------------------------------------
    # Trade start
    # -------------------------------------------------------

    trade_start_time: Any = None

    trade_start_price: float | None = None

    # -------------------------------------------------------
    # Trade levels
    # -------------------------------------------------------

    trade_levels: TradeLevels | None = None

    # -------------------------------------------------------
    # Trade lifecycle
    # -------------------------------------------------------

    trade_status: TradeStatus = TradeStatus.NOT_STARTED

    trade_lifecycle: TradeLifecycle | None = None

    # -------------------------------------------------------
    # Trade result
    # -------------------------------------------------------

    exit_time: Any = None

    exit_price: float | None = None

    exit_reason: str | None = None

    trade_result: float | None = None

    return_value: float | None = None

    return_percent: float | None = None

    # -------------------------------------------------------
    # State history
    # -------------------------------------------------------

    stage_history: list[StrategyStage] = field(
        default_factory=list
    )

    def set_stage(
        self,
        stage: StrategyStage,
    ) -> None:
        """
        Move the orchestrator to a new strategy stage.

        The transition is recorded in stage_history.
        """

        self.stage = stage

        self.stage_history.append(
            stage
        )

    def set_zone(
        self,
        zone: SupplyDemandZone,
    ) -> None:
        """
        Set the active supply/demand zone.
        """

        self.active_zone = zone

        self.set_stage(
            StrategyStage.ZONE_IDENTIFIED
        )

    def start_retest(
        self,
    ) -> None:
        """
        Mark the active zone as being retested.
        """

        self.retest_started = True

        self.retest_candle_count = 0

        self.set_stage(
            StrategyStage.RETESTING
        )

    def add_retest_candle(
        self,
    ) -> None:
        """
        Record another candle belonging to the retest.
        """

        if not self.retest_started:
            raise ValueError(
                "Cannot add a retest candle before "
                "the retest has started."
            )

        self.retest_candle_count += 1

        self.set_stage(
            StrategyStage.LOOKING_FOR_ENTRY
        )

    def set_entry_decision(
        self,
        decision: EntryDecision,
    ) -> None:
        """
        Record a valid entry decision.

        The entry candle is recorded separately from the
        future trade-start candle.
        """

        if not decision.valid:
            raise ValueError(
                "Cannot record an invalid entry decision."
            )

        self.entry_decision = decision

        self.entry_candle_time = (
            decision.entry_candle_time
        )

        self.entry_candle_close = (
            decision.entry_candle_close
        )

        self.set_stage(
            StrategyStage.ENTRY_IDENTIFIED
        )

        self.trade_status = TradeStatus.WAITING

        self.set_stage(
            StrategyStage.WAITING_FOR_TRADE_START
        )

    def start_trade(
        self,
        trade_start_time: Any,
        trade_start_price: float,
    ) -> None:
        """
        Record the start of the actual trade.

        The trade begins at the OPEN of the candle following
        the entry candle.
        """

        if self.entry_decision is None:
            raise ValueError(
                "Cannot start a trade without "
                "an entry decision."
            )

        if (
            trade_start_time
            == self.entry_candle_time
        ):
            raise ValueError(
                "Trade-start candle must be different "
                "from the entry candle."
            )

        self.trade_start_time = (
            trade_start_time
        )

        self.trade_start_price = (
            trade_start_price
        )

        self.trade_status = TradeStatus.OPEN

        self.set_stage(
            StrategyStage.TRADE_OPEN
        )

    def set_trade_lifecycle(
        self,
        trade: TradeLifecycle,
    ) -> None:
        """
        Store the active TradeLifecycle object.

        The lifecycle engine remains responsible for
        monitoring the trade and determining when it closes.
        """

        self.trade_lifecycle = trade

        self.trade_status = TradeStatus.OPEN

        self.set_stage(
            StrategyStage.TRADE_OPEN
        )

    def close_trade(
        self,
        exit_time: Any,
        exit_price: float,
        trade_result: float,
        exit_reason: str | None = None,
        return_value: float | None = None,
        return_percent: float | None = None,
    ) -> None:
        """
        Record the closure of an open trade.

        The detailed exit information normally comes from
        TradeLifecycleEngine.
        """

        if self.trade_status != TradeStatus.OPEN:
            raise ValueError(
                "Cannot close a trade that is not open."
            )

        self.exit_time = exit_time

        self.exit_price = exit_price

        self.exit_reason = exit_reason

        self.trade_result = trade_result

        self.return_value = return_value

        self.return_percent = return_percent

        self.trade_status = TradeStatus.CLOSED

        self.set_stage(
            StrategyStage.TRADE_CLOSED
        )