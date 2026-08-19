from tradepilotai_os.strategy.supply_demand.models import ZoneStatus, ZoneType
from tradepilotai_os.strategy.supply_demand.zone_detector import (
    SupplyDemandZoneDetector,
    ZoneDetectionInput,
)


def test_demand_zone_uses_full_structure_start_candle():
    detector = SupplyDemandZoneDetector()

    setup = ZoneDetectionInput(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_open=1.27098,
        structure_start_high=1.27104,
        structure_start_low=1.27090,
        structure_start_close=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_open=1.27110,
        breakout_high=1.27150,
        breakout_low=1.27108,
        breakout_close=1.27140,
        bullish_breakout=True,
    )

    zone = detector.detect(setup)

    assert zone.zone_type == ZoneType.DEMAND
    assert zone.top == 1.27104
    assert zone.bottom == 1.27090
    assert zone.status == ZoneStatus.ACTIVE


def test_supply_zone_uses_full_structure_start_candle():
    detector = SupplyDemandZoneDetector()

    setup = ZoneDetectionInput(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_open=1.27500,
        structure_start_high=1.27510,
        structure_start_low=1.27490,
        structure_start_close=1.27505,
        breakout_time="2026-08-13 10:00",
        breakout_open=1.27480,
        breakout_high=1.27482,
        breakout_low=1.27430,
        breakout_close=1.27440,
        bullish_breakout=False,
    )

    zone = detector.detect(setup)

    assert zone.zone_type == ZoneType.SUPPLY
    assert zone.top == 1.27510
    assert zone.bottom == 1.27490
    assert zone.status == ZoneStatus.ACTIVE


def test_zone_includes_wicks():
    detector = SupplyDemandZoneDetector()

    setup = ZoneDetectionInput(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_open=1.27098,
        structure_start_high=1.27120,
        structure_start_low=1.27070,
        structure_start_close=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_open=1.27130,
        breakout_high=1.27170,
        breakout_low=1.27125,
        breakout_close=1.27160,
        bullish_breakout=True,
    )

    zone = detector.detect(setup)

    assert zone.top == 1.27120
    assert zone.bottom == 1.27070


def test_breakout_gap_does_not_mitigate_zone():
    detector = SupplyDemandZoneDetector()

    setup = ZoneDetectionInput(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_open=1.27098,
        structure_start_high=1.27104,
        structure_start_low=1.27090,
        structure_start_close=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_open=1.27120,
        breakout_high=1.27160,
        breakout_low=1.27118,
        breakout_close=1.27150,
        bullish_breakout=True,
    )

    zone = detector.detect(setup)

    assert zone.status == ZoneStatus.ACTIVE
    assert zone.mitigation_time is None
    assert zone.mitigation_reason is None


def test_invalid_bullish_breakout_is_rejected():
    detector = SupplyDemandZoneDetector()

    setup = ZoneDetectionInput(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_open=1.27098,
        structure_start_high=1.27104,
        structure_start_low=1.27090,
        structure_start_close=1.27095,
        breakout_time="2026-08-13 10:00",
        breakout_open=1.27100,
        breakout_high=1.27110,
        breakout_low=1.27095,
        breakout_close=1.27102,
        bullish_breakout=True,
    )

    try:
        detector.detect(setup)
    except ValueError as exc:
        assert "Bullish breakout" in str(exc)
    else:
        raise AssertionError(
            "Invalid bullish breakout should have been rejected."
        )


def test_invalid_bearish_breakout_is_rejected():
    detector = SupplyDemandZoneDetector()

    setup = ZoneDetectionInput(
        symbol="GBP/USD",
        structure_start_time="2026-08-13 08:00",
        structure_start_open=1.27500,
        structure_start_high=1.27510,
        structure_start_low=1.27490,
        structure_start_close=1.27505,
        breakout_time="2026-08-13 10:00",
        breakout_open=1.27495,
        breakout_high=1.27500,
        breakout_low=1.27480,
        breakout_close=1.27495,
        bullish_breakout=False,
    )

    try:
        detector.detect(setup)
    except ValueError as exc:
        assert "Bearish breakout" in str(exc)
    else:
        raise AssertionError(
            "Invalid bearish breakout should have been rejected."
        )