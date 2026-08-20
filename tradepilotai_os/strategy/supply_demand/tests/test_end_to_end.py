"""
===========================================================
TradePilotAI OS
Supply & Demand End-to-End Strategy Test
===========================================================

STEP 3

Tests the complete S&D chain:

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
    Trade Lifecycle
      ↓
    WIN / LOSS
"""

from __future__ import annotations

import pytest

from tradepilotai_os.strategy.supply_demand.entry_engine import (
    EntryDecision,
    SupplyDemandEntryEngine,
)

from tradepilotai_os.strategy.supply_demand.entry_patterns import (
    SupplyDemandEntryPatternEngine,
)

from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)

from tradepilotai_os.strategy.supply_demand.retest import (
    RetestCandle,
    SupplyDemandRetestEngine,
)

from tradepilotai_os.strategy.supply_demand.trade_levels import (
    SupplyDemandTradeLevelEngine,
)

from tradepilotai_os.trading.trade_lifecycle import (
    TradeCandle,
    TradeLifecycleEngine,
)


# =========================================================
# TEST DATA
# =========================================================


def make_demand_zone() -> SupplyDemandZone:
    """
    Create an active demand zone suitable for starting
    a retest.
    """

    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27090,
        created_at="2026-08-14 08:00",
        breakout_time="2026-08-14 08:00",
        status=ZoneStatus.ACTIVE,
    )


def make_retest_candle(
    timestamp: str,
    open_price: float,
    high: float,
    low: float,
    close: float,
    candle_number: int,
) -> RetestCandle:
    """Create a retest candle."""

    return RetestCandle(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        candle_number=candle_number,
    )


# =========================================================
# TEST 1
# =========================================================


def test_step_3_zone_to_retest():
    """An active zone can begin a retest."""

    zone = make_demand_zone()

    retest_engine = SupplyDemandRetestEngine()

    first_candle = make_retest_candle(
        "2026-08-14 09:00",
        1.27100,
        1.27104,
        1.27092,
        1.27096,
        1,
    )

    result = retest_engine.start_retest(
        zone,
        first_candle,
    )

    assert result.candle_number == 1

    assert zone.status == ZoneStatus.RETESTING

    assert zone.retest_candle_count == 1


# =========================================================
# TEST 2
# =========================================================


def test_step_3_first_four_candles_are_opportunity_window():
    """
    Candles 1-4 are the entry opportunity window.
    """

    retest_engine = SupplyDemandRetestEngine()

    zone = make_demand_zone()

    candles = [
        make_retest_candle(
            "2026-08-14 09:00",
            1.27100,
            1.27104,
            1.27092,
            1.27096,
            1,
        ),
        make_retest_candle(
            "2026-08-14 10:00",
            1.27096,
            1.27102,
            1.27090,
            1.27094,
            2,
        ),
        make_retest_candle(
            "2026-08-14 11:00",
            1.27094,
            1.27102,
            1.27090,
            1.27092,
            3,
        ),
        make_retest_candle(
            "2026-08-14 12:00",
            1.27092,
            1.27102,
            1.27088,
            1.27090,
            4,
        ),
    ]

    retest_engine.start_retest(
        zone,
        candles[0],
    )

    for current in candles[1:]:
        retest_engine.process_retest_candle(
            zone,
            current,
        )

    assert zone.retest_candle_count == 4

    assert (
        retest_engine.within_entry_opportunity_window(1)
        is True
    )

    assert (
        retest_engine.within_entry_opportunity_window(2)
        is True
    )

    assert (
        retest_engine.within_entry_opportunity_window(3)
        is True
    )

    assert (
        retest_engine.within_entry_opportunity_window(4)
        is True
    )

    assert (
        retest_engine.within_entry_opportunity_window(5)
        is False
    )


# =========================================================
# TEST 3
# =========================================================


def test_step_3_three_candle_reversal_can_begin_on_candle_four():
    """
    Verify the agreed rule:

        Candle 4 = pattern begins
        Candle 5 = continues
        Candle 6 = completes

    Candle 6 becomes the entry candle.

    IMPORTANT:

    Candle 5 is deliberately constructed so it does NOT
    engulf Candle 4.

    This ensures the first completed pattern is the
    intended three-candle reversal rather than an earlier
    engulfing pattern.
    """

    zone = make_demand_zone()

    retest_engine = SupplyDemandRetestEngine()

    pattern_engine = SupplyDemandEntryPatternEngine()

    entry_engine = SupplyDemandEntryEngine(
        retest_engine=retest_engine,
        pattern_engine=pattern_engine,
    )

    candles = [
        make_retest_candle(
            "2026-08-14 09:00",
            1.27100,
            1.27104,
            1.27092,
            1.27096,
            1,
        ),
        make_retest_candle(
            "2026-08-14 10:00",
            1.27096,
            1.27102,
            1.27090,
            1.27094,
            2,
        ),
        make_retest_candle(
            "2026-08-14 11:00",
            1.27094,
            1.27102,
            1.27090,
            1.27092,
            3,
        ),

        # -------------------------------------------------
        # Candle 4
        #
        # First candle of three-candle reversal.
        #
        # Bearish.
        # -------------------------------------------------

        make_retest_candle(
            "2026-08-14 12:00",
            1.27100,
            1.27103,
            1.27088,
            1.27090,
            4,
        ),

        # -------------------------------------------------
        # Candle 5
        #
        # Second candle.
        #
        # Bullish.
        #
        # IMPORTANT:
        # Its body does NOT engulf candle 4.
        # -------------------------------------------------

        make_retest_candle(
            "2026-08-14 13:00",
            1.27090,
            1.27102,
            1.27089,
            1.27098,
            5,
        ),

        # -------------------------------------------------
        # Candle 6
        #
        # Third candle.
        #
        # Bullish.
        #
        # Close is above Candle 4 open.
        # -------------------------------------------------

        make_retest_candle(
            "2026-08-14 14:00",
            1.27098,
            1.27112,
            1.27097,
            1.27108,
            6,
        ),
    ]

    retest_engine.start_retest(
        zone,
        candles[0],
    )

    for current in candles[1:]:
        retest_engine.process_retest_candle(
            zone,
            current,
        )

    decision = entry_engine.evaluate(
        zone=zone,
        candles=candles,
        zone_type=ZoneType.DEMAND,
    )

    assert decision.valid is True

    assert (
        decision.pattern
        == EntryPattern.THREE_CANDLE_REVERSAL
    )

    assert (
        decision.entry_candle_time
        == "2026-08-14 14:00"
    )

    assert (
        decision.entry_candle_close
        == pytest.approx(1.27108)
    )


# =========================================================
# TEST 4
# =========================================================


def test_step_3_following_candle_is_actual_trade_entry():
    """
    The trade starts on the OPEN of the following candle.
    """

    zone = make_demand_zone()

    entry_engine = SupplyDemandEntryEngine()

    decision = EntryDecision(
        valid=True,
        pattern=EntryPattern.THREE_CANDLE_REVERSAL,
        entry_candle_time="2026-08-14 14:00",
        entry_candle_close=1.27108,
    )

    following_candle = make_retest_candle(
        "2026-08-14 15:00",
        1.27120,
        1.27130,
        1.27110,
        1.27125,
        7,
    )

    result = entry_engine.start_trade(
        zone=zone,
        decision=decision,
        following_candle=following_candle,
    )

    assert result.valid is True

    assert (
        result.trade_start_time
        == "2026-08-14 15:00"
    )

    assert (
        result.trade_start_price
        == pytest.approx(1.27120)
    )

    assert (
        zone.entry_time
        == "2026-08-14 15:00"
    )

    assert (
        zone.entry_price
        == pytest.approx(1.27120)
    )


# =========================================================
# TEST 5
# =========================================================


def test_step_3_trade_levels_use_actual_entry():
    """
    Stop:

        Demand bottom 1.27090
        minus 5 pips
        = 1.27040

    Actual entry:

        1.27120

    Risk:

        0.00080

    TP:

        1.27280
    """

    zone = make_demand_zone()

    levels_engine = SupplyDemandTradeLevelEngine()

    levels = levels_engine.calculate(
        zone=zone,
        entry_price=1.27120,
        risk_value=100.0,
    )

    assert levels.direction == "BUY"

    assert (
        levels.entry_price
        == pytest.approx(1.27120)
    )

    assert (
        levels.stop_loss
        == pytest.approx(1.27040)
    )

    assert (
        levels.risk_distance
        == pytest.approx(0.00080)
    )

    assert (
        levels.stop_pips
        == pytest.approx(8.0)
    )

    assert (
        levels.take_profit
        == pytest.approx(1.27280)
    )

    assert (
        levels.risk_value
        == pytest.approx(100.0)
    )


# =========================================================
# TEST 6
# =========================================================


def test_step_3_trade_lifecycle_opens_at_actual_entry():
    """Connect trade levels to the lifecycle engine."""

    zone = make_demand_zone()

    levels_engine = SupplyDemandTradeLevelEngine()

    levels = levels_engine.calculate(
        zone=zone,
        entry_price=1.27120,
        risk_value=100.0,
    )

    lifecycle_engine = TradeLifecycleEngine()

    trade = lifecycle_engine.open_trade(
        ticker=zone.symbol,
        direction=levels.direction,
        entry_time="2026-08-14 15:00",
        entry_price=levels.entry_price,
        stop_loss=levels.stop_loss,
        take_profit=levels.take_profit,
        risk_value=levels.risk_value,
    )

    assert trade.status == "OPEN"

    assert trade.direction == "BUY"

    assert (
        trade.entry_price
        == pytest.approx(1.27120)
    )

    assert (
        trade.stop_loss
        == pytest.approx(1.27040)
    )

    assert (
        trade.take_profit
        == pytest.approx(1.27280)
    )

    assert (
        trade.risk_value
        == pytest.approx(100.0)
    )


# =========================================================
# TEST 7
# =========================================================


def test_step_3_trade_closes_at_take_profit():
    """A BUY trade closes as a WIN at take profit."""

    zone = make_demand_zone()

    levels_engine = SupplyDemandTradeLevelEngine()

    levels = levels_engine.calculate(
        zone=zone,
        entry_price=1.27120,
        risk_value=100.0,
    )

    lifecycle_engine = TradeLifecycleEngine()

    trade = lifecycle_engine.open_trade(
        ticker=zone.symbol,
        direction=levels.direction,
        entry_time="2026-08-14 15:00",
        entry_price=levels.entry_price,
        stop_loss=levels.stop_loss,
        take_profit=levels.take_profit,
        risk_value=levels.risk_value,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 16:00",
        open=1.27130,
        high=1.27290,
        low=1.27120,
        close=1.27270,
    )

    lifecycle_engine.process_candle(
        trade,
        candle,
    )

    assert trade.status == "CLOSED"

    assert (
        trade.exit_reason
        == "TAKE_PROFIT"
    )

    assert (
        trade.exit_price
        == pytest.approx(1.27280)
    )

    assert trade.result == "WIN"


# =========================================================
# TEST 8
# =========================================================


def test_step_3_trade_closes_at_stop_loss():
    """A BUY trade closes as a LOSS at stop loss."""

    zone = make_demand_zone()

    levels_engine = SupplyDemandTradeLevelEngine()

    levels = levels_engine.calculate(
        zone=zone,
        entry_price=1.27120,
        risk_value=100.0,
    )

    lifecycle_engine = TradeLifecycleEngine()

    trade = lifecycle_engine.open_trade(
        ticker=zone.symbol,
        direction=levels.direction,
        entry_time="2026-08-14 15:00",
        entry_price=levels.entry_price,
        stop_loss=levels.stop_loss,
        take_profit=levels.take_profit,
        risk_value=levels.risk_value,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 16:00",
        open=1.27110,
        high=1.27120,
        low=1.27030,
        close=1.27060,
    )

    lifecycle_engine.process_candle(
        trade,
        candle,
    )

    assert trade.status == "CLOSED"

    assert (
        trade.exit_reason
        == "STOP_LOSS"
    )

    assert (
        trade.exit_price
        == pytest.approx(1.27040)
    )

    assert trade.result == "LOSS"


# =========================================================
# TEST 9
# =========================================================


def test_step_3_same_candle_sl_and_tp_uses_stop_loss():
    """
    When both SL and TP are touched in the same OHLC candle,
    STOP LOSS is used conservatively.
    """

    zone = make_demand_zone()

    levels_engine = SupplyDemandTradeLevelEngine()

    levels = levels_engine.calculate(
        zone=zone,
        entry_price=1.27120,
        risk_value=100.0,
    )

    lifecycle_engine = TradeLifecycleEngine()

    trade = lifecycle_engine.open_trade(
        ticker=zone.symbol,
        direction=levels.direction,
        entry_time="2026-08-14 15:00",
        entry_price=levels.entry_price,
        stop_loss=levels.stop_loss,
        take_profit=levels.take_profit,
        risk_value=levels.risk_value,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 16:00",
        open=1.27120,
        high=1.27300,
        low=1.27020,
        close=1.27150,
    )

    lifecycle_engine.process_candle(
        trade,
        candle,
    )

    assert trade.status == "CLOSED"

    assert (
        trade.exit_reason
        == "STOP_LOSS"
    )

    assert (
        trade.exit_price
        == pytest.approx(1.27040)
    )

    assert trade.result == "LOSS"


# =========================================================
# TEST 10
# =========================================================


def test_step_3_trade_return_is_calculated():
    """Verify the final trade return."""

    zone = make_demand_zone()

    levels_engine = SupplyDemandTradeLevelEngine()

    levels = levels_engine.calculate(
        zone=zone,
        entry_price=1.27120,
        risk_value=100.0,
    )

    lifecycle_engine = TradeLifecycleEngine()

    trade = lifecycle_engine.open_trade(
        ticker=zone.symbol,
        direction=levels.direction,
        entry_time="2026-08-14 15:00",
        entry_price=levels.entry_price,
        stop_loss=levels.stop_loss,
        take_profit=levels.take_profit,
        risk_value=levels.risk_value,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 16:00",
        open=1.27130,
        high=1.27290,
        low=1.27120,
        close=1.27270,
    )

    lifecycle_engine.process_candle(
        trade,
        candle,
    )

    expected_return = (
        1.27280
        - 1.27120
    )

    expected_percent = (
        expected_return
        / 1.27120
        * 100.0
    )

    assert (
        trade.return_value
        == pytest.approx(expected_return)
    )

    assert (
        trade.return_percent
        == pytest.approx(expected_percent)
    )