"""
===========================================================
TradePilotAI OS
Supply & Demand Strategy Orchestrator
===========================================================

STEP 4 - PORTFOLIO RISK CONTROL

Connects the complete Supply & Demand strategy flow:

    Zone
      ↓
    Retest
      ↓
    Entry Pattern
      ↓
    Entry Candle
      ↓
    Following Candle OPEN
      ↓
    Trade Levels
      ↓
    Portfolio Risk Assessment
      ↓
    Trade Lifecycle
      ↓
    Stop Loss / Take Profit
      ↓
    Trade Closed

The orchestrator coordinates the existing specialist
engines.

IMPORTANT
---------

This module does NOT redefine any S&D strategy rules.

Existing rules remain unchanged:

    Maximum open trades:
        5

    Maximum total portfolio risk:
        5%

    Entry pattern:
        Existing Entry Engine rules

    Trade start:
        OPEN of candle following entry candle

    Stop loss:
        Existing Trade Level Engine rules

    Take profit:
        Existing Trade Level Engine rules

The PortfolioRiskController determines whether a proposed
trade may be added to the currently open portfolio.

Broker execution is NOT handled here.
"""

from __future__ import annotations

from .entry_engine import (
    EntryDecision,
    SupplyDemandEntryEngine,
)

from .models import (
    SupplyDemandZone,
    ZoneType,
)

from .orchestrator_models import (
    StrategyStage,
    SupplyDemandOrchestratorState,
)

from .retest import (
    RetestCandle,
    SupplyDemandRetestEngine,
)

from .trade_levels import (
    SupplyDemandTradeLevelEngine,
    TradeLevels,
)

from tradepilotai_os.risk.portfolio_risk import (
    PortfolioRiskAssessment,
    PortfolioRiskController,
)

from tradepilotai_os.trading.trade_lifecycle import (
    TradeCandle,
    TradeLifecycle,
    TradeLifecycleEngine,
)


class SupplyDemandOrchestrator:
    """
    Coordinate the Supply/Demand specialist engines.

    STEP 4 adds the existing PortfolioRiskController as a
    gate between calculated trade levels and the lifecycle
    trade.

    The orchestrator does not create new strategy rules.
    """

    def __init__(
        self,
        retest_engine: SupplyDemandRetestEngine | None = None,
        entry_engine: SupplyDemandEntryEngine | None = None,
        trade_level_engine: (
            SupplyDemandTradeLevelEngine | None
        ) = None,
        lifecycle_engine: (
            TradeLifecycleEngine | None
        ) = None,
        portfolio_risk_controller: (
            PortfolioRiskController | None
        ) = None,
        state: SupplyDemandOrchestratorState | None = None,
    ) -> None:

        self.retest_engine = (
            retest_engine
            if retest_engine is not None
            else SupplyDemandRetestEngine()
        )

        self.entry_engine = (
            entry_engine
            if entry_engine is not None
            else SupplyDemandEntryEngine(
                retest_engine=self.retest_engine
            )
        )

        self.trade_level_engine = (
            trade_level_engine
            if trade_level_engine is not None
            else SupplyDemandTradeLevelEngine()
        )

        self.lifecycle_engine = (
            lifecycle_engine
            if lifecycle_engine is not None
            else TradeLifecycleEngine()
        )

        self.portfolio_risk_controller = (
            portfolio_risk_controller
            if portfolio_risk_controller is not None
            else PortfolioRiskController()
        )

        self.state = (
            state
            if state is not None
            else SupplyDemandOrchestratorState()
        )

        self.retest_candles: list[
            RetestCandle
        ] = []

        self.last_risk_assessment: (
            PortfolioRiskAssessment | None
        ) = None

    # =========================================================
    # ZONE
    # =========================================================

    def set_active_zone(
        self,
        zone: SupplyDemandZone,
    ) -> None:
        """
        Set the zone currently being processed.
        """

        self.state.set_zone(
            zone
        )

    # =========================================================
    # START RETEST
    # =========================================================

    def start_retest(
        self,
        candle: RetestCandle,
    ) -> RetestCandle:
        """
        Start a retest through the existing Retest Engine.
        """

        if self.state.active_zone is None:
            raise ValueError(
                "Cannot start a retest without an active zone."
            )

        self.retest_candles.clear()

        retest_candle = (
            self.retest_engine.start_retest(
                zone=self.state.active_zone,
                candle=candle,
            )
        )

        self.retest_candles.append(
            retest_candle
        )

        self.state.start_retest()

        self.state.retest_candle_count = (
            retest_candle.candle_number
        )

        self.state.timestamp = (
            retest_candle.timestamp
        )

        return retest_candle

    # =========================================================
    # PROCESS RETEST CANDLE
    # =========================================================

    def process_retest_candle(
        self,
        candle: RetestCandle,
    ) -> RetestCandle:
        """
        Process the next retest candle.
        """

        if self.state.active_zone is None:
            raise ValueError(
                "Cannot process a retest candle without "
                "an active zone."
            )

        if not self.state.retest_started:
            raise ValueError(
                "Cannot process a retest candle before "
                "the retest has started."
            )

        retest_candle = (
            self.retest_engine.process_retest_candle(
                zone=self.state.active_zone,
                candle=candle,
            )
        )

        self.retest_candles.append(
            retest_candle
        )

        self.state.retest_candle_count = (
            retest_candle.candle_number
        )

        self.state.timestamp = (
            retest_candle.timestamp
        )

        self.state.set_stage(
            StrategyStage.LOOKING_FOR_ENTRY
        )

        return retest_candle

    # =========================================================
    # ENTRY EVALUATION
    # =========================================================

    def evaluate_entry(
        self,
        zone_type: ZoneType,
    ) -> EntryDecision:
        """
        Evaluate the current retest through the existing
        SupplyDemandEntryEngine.
        """

        if self.state.active_zone is None:
            raise ValueError(
                "Cannot evaluate entry without an active zone."
            )

        if not self.retest_candles:
            return EntryDecision()

        if (
            self.state.entry_decision is not None
            and self.state.entry_decision.valid
        ):
            return self.state.entry_decision

        decision = self.entry_engine.evaluate(
            zone=self.state.active_zone,
            candles=self.retest_candles,
            zone_type=zone_type,
        )

        if not decision.valid:

            self.state.set_stage(
                StrategyStage.LOOKING_FOR_ENTRY
            )

            return decision

        self.state.set_entry_decision(
            decision
        )

        return decision

    # =========================================================
    # TRADE START
    # =========================================================

    def start_trade(
        self,
        following_candle: RetestCandle,
    ) -> EntryDecision:
        """
        Start the actual trade on the OPEN of the candle
        following the completed entry candle.
        """

        if self.state.active_zone is None:
            raise ValueError(
                "Cannot start a trade without an active zone."
            )

        if self.state.entry_decision is None:
            raise ValueError(
                "Cannot start a trade without "
                "a valid entry decision."
            )

        if not self.state.entry_decision.valid:
            raise ValueError(
                "Cannot start a trade without "
                "a valid entry decision."
            )

        decision = self.entry_engine.start_trade(
            zone=self.state.active_zone,
            decision=self.state.entry_decision,
            following_candle=following_candle,
        )

        if decision.trade_start_time is None:
            raise ValueError(
                "Entry Engine did not provide "
                "a trade-start time."
            )

        if decision.trade_start_price is None:
            raise ValueError(
                "Entry Engine did not provide "
                "a trade-start price."
            )

        self.state.start_trade(
            trade_start_time=decision.trade_start_time,
            trade_start_price=decision.trade_start_price,
        )

        self.state.timestamp = (
            decision.trade_start_time
        )

        return decision

    # =========================================================
    # TRADE LEVELS
    # =========================================================

    def calculate_trade_levels(
        self,
        risk_value: float = 0.0,
    ) -> TradeLevels:
        """
        Calculate trade levels using the actual trade-start
        price.

        The supplied risk_value is carried through to the
        TradeLevels object.

        No new risk rule is introduced here.
        """

        if self.state.active_zone is None:
            raise ValueError(
                "Cannot calculate trade levels without "
                "an active zone."
            )

        if self.state.entry_decision is None:
            raise ValueError(
                "Cannot calculate trade levels without "
                "a valid entry decision."
            )

        if not self.state.entry_decision.valid:
            raise ValueError(
                "Cannot calculate trade levels without "
                "a valid entry decision."
            )

        if self.state.trade_start_price is None:
            raise ValueError(
                "Cannot calculate trade levels before "
                "the actual trade entry price is known."
            )

        levels = (
            self.trade_level_engine.calculate(
                zone=self.state.active_zone,
                entry_price=self.state.trade_start_price,
                risk_value=risk_value,
            )
        )

        self.state.trade_levels = levels

        return levels

    # =========================================================
    # STEP 4 - PORTFOLIO RISK ASSESSMENT
    # =========================================================

    def assess_portfolio_risk(
        self,
        proposed_risk_value: float,
        current_open_trades: int,
        current_risk_value: float,
    ) -> PortfolioRiskAssessment:
        """
        Assess whether the proposed trade can be added to the
        currently open portfolio.

        The existing PortfolioRiskController enforces:

            Maximum open trades = 5
            Maximum total portfolio risk = 5%

        No other risk rule is applied here.
        """

        if self.state.trade_levels is None:
            raise ValueError(
                "Cannot assess portfolio risk before "
                "trade levels have been calculated."
            )

        assessment = (
            self.portfolio_risk_controller.assess(
                current_open_trades=current_open_trades,
                current_risk_value=current_risk_value,
                proposed_risk_value=proposed_risk_value,
            )
        )

        self.last_risk_assessment = assessment

        return assessment

    # =========================================================
    # STEP 4 - OPEN APPROVED TRADE
    # =========================================================

    def open_trade(
        self,
        risk_value: float,
        current_open_trades: int = 0,
        current_risk_value: float = 0.0,
    ) -> TradeLifecycle:
        """
        Assess portfolio risk and open the lifecycle trade
        only when the proposed trade is permitted.

        The risk controller is checked BEFORE the lifecycle
        trade is created.

        Existing S&D rules remain unchanged.
        """

        if self.state.active_zone is None:
            raise ValueError(
                "Cannot open a trade without an active zone."
            )

        if self.state.trade_start_time is None:
            raise ValueError(
                "Cannot open a trade before "
                "the trade has started."
            )

        if self.state.trade_start_price is None:
            raise ValueError(
                "Cannot open a trade without "
                "an actual trade entry price."
            )

        if self.state.trade_levels is None:
            raise ValueError(
                "Cannot open a trade before "
                "trade levels have been calculated."
            )

        if self.state.trade_status.value != "OPEN":
            raise ValueError(
                "Cannot open the lifecycle trade before "
                "the S&D trade is marked OPEN."
            )

        if risk_value <= 0:
            raise ValueError(
                "Risk value must be greater than zero."
            )

        # -----------------------------------------------------
        # Portfolio risk gate
        # -----------------------------------------------------

        assessment = self.assess_portfolio_risk(
            proposed_risk_value=risk_value,
            current_open_trades=current_open_trades,
            current_risk_value=current_risk_value,
        )

        if not assessment.permitted:
            raise ValueError(
                assessment.reason
            )

        levels = self.state.trade_levels

        trade = self.lifecycle_engine.open_trade(
            ticker=self.state.active_zone.symbol,
            direction=levels.direction,
            entry_time=self.state.trade_start_time,
            entry_price=self.state.trade_start_price,
            stop_loss=levels.stop_loss,
            take_profit=levels.take_profit,
            risk_value=risk_value,
        )

        self.state.set_trade_lifecycle(
            trade
        )

        return trade

    # =========================================================
    # PROCESS OPEN TRADE CANDLE
    # =========================================================

    def process_trade_candle(
        self,
        candle: TradeCandle,
    ) -> TradeLifecycle:
        """
        Process one candle against the active lifecycle trade.

        If the lifecycle engine closes the trade, the
        orchestrator state is updated with the complete result.
        """

        if self.state.trade_lifecycle is None:
            raise ValueError(
                "Cannot process a trade candle without "
                "an open lifecycle trade."
            )

        trade = self.lifecycle_engine.process_candle(
            trade=self.state.trade_lifecycle,
            candle=candle,
        )

        self.state.timestamp = (
            candle.timestamp
        )

        if trade.status == "CLOSED":

            if trade.exit_time is None:
                raise ValueError(
                    "Closed trade is missing exit time."
                )

            if trade.exit_price is None:
                raise ValueError(
                    "Closed trade is missing exit price."
                )

            if trade.result is None:
                raise ValueError(
                    "Closed trade is missing result."
                )

            self.state.close_trade(
                exit_time=trade.exit_time,
                exit_price=trade.exit_price,
                trade_result=trade.result,
                exit_reason=trade.exit_reason,
                return_value=trade.return_value,
                return_percent=trade.return_percent,
            )

        return trade

    # =========================================================
    # OPPORTUNITY WINDOW
    # =========================================================

    def within_entry_opportunity_window(
        self,
        candle_number: int,
    ) -> bool:
        """
        Ask the existing Retest Engine whether a candle is
        inside the first four-candle opportunity window.
        """

        return (
            self.retest_engine
            .within_entry_opportunity_window(
                candle_number
            )
        )