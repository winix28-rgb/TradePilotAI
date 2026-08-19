import pytest

from tradepilotai_os.trading.trade_lifecycle import (
    TradeCandle,
    TradeLifecycleEngine,
)


def make_engine():
    return TradeLifecycleEngine()


def test_buy_trade_opens_correctly():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="BUY",
        entry_time="2026-08-14 10:00",
        entry_price=1.27100,
        stop_loss=1.27040,
        take_profit=1.27220,
        risk_value=100.0,
    )

    assert trade.status == "OPEN"
    assert trade.direction == "BUY"
    assert trade.entry_price == 1.27100
    assert trade.risk_value == 100.0


def test_sell_trade_opens_correctly():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="SELL",
        entry_time="2026-08-14 10:00",
        entry_price=1.27470,
        stop_loss=1.27560,
        take_profit=1.27290,
        risk_value=100.0,
    )

    assert trade.status == "OPEN"
    assert trade.direction == "SELL"


def test_buy_trade_closes_at_stop_loss():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="BUY",
        entry_time="2026-08-14 10:00",
        entry_price=1.27100,
        stop_loss=1.27040,
        take_profit=1.27220,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27090,
        high=1.27110,
        low=1.27035,
        close=1.27060,
    )

    engine.process_candle(trade, candle)

    assert trade.status == "CLOSED"
    assert trade.exit_reason == "STOP_LOSS"
    assert trade.exit_price == pytest.approx(1.27040)
    assert trade.result == "LOSS"


def test_buy_trade_closes_at_take_profit():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="BUY",
        entry_time="2026-08-14 10:00",
        entry_price=1.27100,
        stop_loss=1.27040,
        take_profit=1.27220,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27230,
        low=1.27100,
        close=1.27210,
    )

    engine.process_candle(trade, candle)

    assert trade.status == "CLOSED"
    assert trade.exit_reason == "TAKE_PROFIT"
    assert trade.exit_price == pytest.approx(1.27220)
    assert trade.result == "WIN"


def test_sell_trade_closes_at_stop_loss():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="SELL",
        entry_time="2026-08-14 10:00",
        entry_price=1.27470,
        stop_loss=1.27560,
        take_profit=1.27290,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27480,
        high=1.27570,
        low=1.27420,
        close=1.27530,
    )

    engine.process_candle(trade, candle)

    assert trade.status == "CLOSED"
    assert trade.exit_reason == "STOP_LOSS"
    assert trade.result == "LOSS"


def test_sell_trade_closes_at_take_profit():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="SELL",
        entry_time="2026-08-14 10:00",
        entry_price=1.27470,
        stop_loss=1.27560,
        take_profit=1.27290,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27460,
        high=1.27480,
        low=1.27280,
        close=1.27300,
    )

    engine.process_candle(trade, candle)

    assert trade.status == "CLOSED"
    assert trade.exit_reason == "TAKE_PROFIT"
    assert trade.result == "WIN"


def test_open_trade_remains_open_when_levels_are_not_hit():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="BUY",
        entry_time="2026-08-14 10:00",
        entry_price=1.27100,
        stop_loss=1.27040,
        take_profit=1.27220,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27100,
        high=1.27150,
        low=1.27080,
        close=1.27130,
    )

    engine.process_candle(trade, candle)

    assert trade.status == "OPEN"
    assert trade.exit_time is None
    assert trade.result is None


def test_buy_return_is_calculated():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="BUY",
        entry_time="2026-08-14 10:00",
        entry_price=1.27100,
        stop_loss=1.27040,
        take_profit=1.27220,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27110,
        high=1.27230,
        low=1.27100,
        close=1.27210,
    )

    engine.process_candle(trade, candle)

    expected_return = 1.27220 - 1.27100

    assert trade.return_value == pytest.approx(
        expected_return
    )

    assert trade.return_percent == pytest.approx(
        expected_return
        / 1.27100
        * 100.0
    )


def test_sell_return_is_calculated():
    engine = make_engine()

    trade = engine.open_trade(
        ticker="GBP/USD",
        direction="SELL",
        entry_time="2026-08-14 10:00",
        entry_price=1.27470,
        stop_loss=1.27560,
        take_profit=1.27290,
        risk_value=100.0,
    )

    candle = TradeCandle(
        timestamp="2026-08-14 11:00",
        open=1.27460,
        high=1.27480,
        low=1.27280,
        close=1.27300,
    )

    engine.process_candle(trade, candle)

    expected_return = 1.27470 - 1.27290

    assert trade.return_value == pytest.approx(
        expected_return
    )

    assert trade.return_percent == pytest.approx(
        expected_return
        / 1.27470
        * 100.0
    )


def test_trade_cannot_be_reopened_as_invalid_direction():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.open_trade(
            ticker="GBP/USD",
            direction="SIDEWAYS",
            entry_time="2026-08-14 10:00",
            entry_price=1.27100,
            stop_loss=1.27040,
            take_profit=1.27220,
            risk_value=100.0,
        )


def test_buy_trade_rejects_invalid_stop():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.open_trade(
            ticker="GBP/USD",
            direction="BUY",
            entry_time="2026-08-14 10:00",
            entry_price=1.27100,
            stop_loss=1.27200,
            take_profit=1.27300,
            risk_value=100.0,
        )


def test_sell_trade_rejects_invalid_stop():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.open_trade(
            ticker="GBP/USD",
            direction="SELL",
            entry_time="2026-08-14 10:00",
            entry_price=1.27470,
            stop_loss=1.27300,
            take_profit=1.27200,
            risk_value=100.0,
        )