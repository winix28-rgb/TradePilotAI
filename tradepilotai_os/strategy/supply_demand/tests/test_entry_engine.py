import pytest

from tradepilotai_os.strategy.supply_demand.entry_engine import (
    SupplyDemandEntryEngine,
)
from tradepilotai_os.strategy.supply_demand.models import (
    EntryPattern,
    SupplyDemandZone,
    ZoneStatus,
    ZoneType,
)
from tradepilotai_os.strategy.supply_demand.retest import (
    RetestCandle,
)


def make_zone():
    return SupplyDemandZone(
        symbol="GBP/USD",
        zone_type=ZoneType.DEMAND,
        top=1.27104,
        bottom=1.27090,
        created_at="2026-08-13 10:00",
        breakout_time="2026-08-13 10:00",
        status=ZoneStatus.RETESTING,
        retest_candle_count=1,
    )


def make_candle(
    timestamp,
    open_price,
    high,
    low,
    close,
    number,
):
    return RetestCandle(
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close,
        candle_number=number,
    )


# ============================================================
# BASIC ENTRY TESTS
# ============================================================


def test_first_valid_pin_bar_becomes_entry_candle():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27100,
            1.27115,
            1.27050,
            1.27110,
            1,
        )
    ]

    decision = engine.evaluate(
        zone=zone,
        candles=candles,
        zone_type=ZoneType.DEMAND,
    )

    assert decision.valid is True
    assert decision.pattern == EntryPattern.PIN_BAR
    assert decision.entry_candle_time == "2026-08-13 14:00"
    assert decision.entry_candle_close == 1.27110
    assert decision.trade_start_time is None
    assert decision.trade_start_price is None


def test_trade_starts_on_following_candle_open():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    entry_candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
        1,
    )

    decision = engine.evaluate(
        zone=zone,
        candles=[entry_candle],
        zone_type=ZoneType.DEMAND,
    )

    following_candle = make_candle(
        "2026-08-13 15:00",
        1.27108,
        1.27125,
        1.27100,
        1.27120,
        2,
    )

    engine.start_trade(
        zone=zone,
        decision=decision,
        following_candle=following_candle,
    )

    assert decision.trade_start_time == "2026-08-13 15:00"
    assert decision.trade_start_price == 1.27108
    assert zone.entry_time == "2026-08-13 15:00"
    assert zone.entry_price == 1.27108


def test_entry_price_is_not_entry_candle_close():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    entry_candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
        1,
    )

    decision = engine.evaluate(
        zone=zone,
        candles=[entry_candle],
        zone_type=ZoneType.DEMAND,
    )

    following_candle = make_candle(
        "2026-08-13 15:00",
        1.27108,
        1.27125,
        1.27100,
        1.27120,
        2,
    )

    engine.start_trade(
        zone=zone,
        decision=decision,
        following_candle=following_candle,
    )

    assert decision.entry_candle_close == 1.27110
    assert decision.trade_start_price == 1.27108
    assert decision.trade_start_price != decision.entry_candle_close


def test_entry_candle_and_trade_start_candle_are_different():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    entry_candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
        1,
    )

    decision = engine.evaluate(
        zone=zone,
        candles=[entry_candle],
        zone_type=ZoneType.DEMAND,
    )

    following_candle = make_candle(
        "2026-08-13 15:00",
        1.27108,
        1.27125,
        1.27100,
        1.27120,
        2,
    )

    engine.start_trade(
        zone=zone,
        decision=decision,
        following_candle=following_candle,
    )

    assert decision.entry_candle_time != decision.trade_start_time


def test_trade_cannot_start_on_entry_candle():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    entry_candle = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27050,
        1.27110,
        1,
    )

    decision = engine.evaluate(
        zone=zone,
        candles=[entry_candle],
        zone_type=ZoneType.DEMAND,
    )

    with pytest.raises(
        ValueError,
        match="different from the entry candle",
    ):
        engine.start_trade(
            zone=zone,
            decision=decision,
            following_candle=entry_candle,
        )


def test_no_valid_pattern_means_no_trade():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    ordinary = make_candle(
        "2026-08-13 14:00",
        1.27100,
        1.27115,
        1.27095,
        1.27105,
        1,
    )

    decision = engine.evaluate(
        zone=zone,
        candles=[ordinary],
        zone_type=ZoneType.DEMAND,
    )

    assert decision.valid is False
    assert decision.pattern is None
    assert decision.trade_start_time is None
    assert decision.trade_start_price is None


# ============================================================
# THREE-CANDLE REVERSAL
# ============================================================


def test_three_candle_reversal_started_on_candle_three_can_complete_on_five():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27110,
            1.27120,
            1.27100,
            1.27108,
            1,
        ),
        make_candle(
            "2026-08-13 15:00",
            1.27108,
            1.27115,
            1.27102,
            1.27106,
            2,
        ),
        # First reversal candle - bearish
        make_candle(
            "2026-08-13 16:00",
            1.27120,
            1.27125,
            1.27095,
            1.27100,
            3,
        ),
        # Second reversal candle - bullish
        make_candle(
            "2026-08-13 17:00",
            1.27100,
            1.27110,
            1.27095,
            1.27105,
            4,
        ),
        # Third reversal candle - bullish
        make_candle(
            "2026-08-13 18:00",
            1.27105,
            1.27130,
            1.27100,
            1.27125,
            5,
        ),
    ]

    decision = engine.evaluate(
        zone=zone,
        candles=candles,
        zone_type=ZoneType.DEMAND,
    )

    assert decision.valid is True
    assert decision.pattern == EntryPattern.THREE_CANDLE_REVERSAL
    assert decision.entry_candle_time == "2026-08-13 18:00"


def test_three_candle_reversal_started_on_candle_four_can_complete_on_six():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27105,
            1.27110,
            1.27100,
            1.27102,
            1,
        ),
        make_candle(
            "2026-08-13 15:00",
            1.27102,
            1.27108,
            1.27098,
            1.27104,
            2,
        ),
        make_candle(
            "2026-08-13 16:00",
            1.27104,
            1.27110,
            1.27098,
            1.27102,
            3,
        ),
        # First reversal candle - bearish
        make_candle(
            "2026-08-13 17:00",
            1.27110,
            1.27115,
            1.27090,
            1.27100,
            4,
        ),
        # Second reversal candle - bullish
        make_candle(
            "2026-08-13 18:00",
            1.27100,
            1.27110,
            1.27095,
            1.27102,
            5,
        ),
        # Third reversal candle - bullish
        make_candle(
            "2026-08-13 19:00",
            1.27102,
            1.27130,
            1.27100,
            1.27120,
            6,
        ),
    ]

    decision = engine.evaluate(
        zone=zone,
        candles=candles,
        zone_type=ZoneType.DEMAND,
    )

    assert decision.valid is True
    assert decision.pattern == EntryPattern.THREE_CANDLE_REVERSAL
    assert decision.entry_candle_time == "2026-08-13 19:00"


def test_trade_starts_after_late_three_candle_reversal():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    candles = [
        make_candle(
            "2026-08-13 14:00",
            1.27105,
            1.27110,
            1.27100,
            1.27102,
            1,
        ),
        make_candle(
            "2026-08-13 15:00",
            1.27102,
            1.27108,
            1.27098,
            1.27104,
            2,
        ),
        make_candle(
            "2026-08-13 16:00",
            1.27104,
            1.27110,
            1.27098,
            1.27102,
            3,
        ),
        make_candle(
            "2026-08-13 17:00",
            1.27110,
            1.27115,
            1.27090,
            1.27100,
            4,
        ),
        make_candle(
            "2026-08-13 18:00",
            1.27100,
            1.27110,
            1.27095,
            1.27102,
            5,
        ),
        make_candle(
            "2026-08-13 19:00",
            1.27102,
            1.27130,
            1.27100,
            1.27120,
            6,
        ),
    ]

    decision = engine.evaluate(
        zone=zone,
        candles=candles,
        zone_type=ZoneType.DEMAND,
    )

    following = make_candle(
        "2026-08-13 20:00",
        1.27118,
        1.27135,
        1.27110,
        1.27125,
        7,
    )

    engine.start_trade(
        zone=zone,
        decision=decision,
        following_candle=following,
    )

    assert decision.entry_candle_time == "2026-08-13 19:00"
    assert decision.trade_start_time == "2026-08-13 20:00"
    assert decision.trade_start_price == 1.27118


# ============================================================
# FOUR-CANDLE OPPORTUNITY WINDOW
# ============================================================


def test_pin_bar_after_candle_four_is_not_a_new_entry():
    engine = SupplyDemandEntryEngine()
    zone = make_zone()

    candles = [
        # Candle 1
        # Body = 0.00008
        # Range = 0.00010
        # Body = 80% -> NOT a Pin Bar
        make_candle(
            "2026-08-13 14:00",
            1.27100,
            1.27110,
            1.27100,
            1.27108,
            1,
        ),

        # Candle 2
        # Body = 0.00008
        # Range = 0.00010
        # Body = 80% -> NOT a Pin Bar
        make_candle(
            "2026-08-13 15:00",
            1.27108,
            1.27118,
            1.27108,
            1.27116,
            2,
        ),

        # Candle 3
        # Body = 0.00008
        # Range = 0.00010
        # Body = 80% -> NOT a Pin Bar
        make_candle(
            "2026-08-13 16:00",
            1.27116,
            1.27126,
            1.27116,
            1.27124,
            3,
        ),

        # Candle 4
        # Body = 0.00008
        # Range = 0.00010
        # Body = 80% -> NOT a Pin Bar
        make_candle(
            "2026-08-13 17:00",
            1.27124,
            1.27134,
            1.27124,
            1.27132,
            4,
        ),

        # Candle 5
        #
        # Valid Demand Pin Bar:
        # body = 0.00005
        # range = 0.00060
        # body ratio = 8.33%
        #
        # BUT candle 5 is outside the four-candle
        # entry opportunity window.
        make_candle(
            "2026-08-13 18:00",
            1.27103,
            1.27110,
            1.27050,
            1.27108,
            5,
        ),
    ]

    decision = engine.evaluate(
        zone=zone,
        candles=candles,
        zone_type=ZoneType.DEMAND,
    )

    assert decision.valid is False
    assert decision.pattern is None
    assert decision.entry_candle_time is None
    assert decision.trade_start_time is None
    assert decision.trade_start_price is None