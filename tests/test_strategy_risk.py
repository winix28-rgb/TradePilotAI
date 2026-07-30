from tradepilotai_os.models.signal import Signal
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.models.strategy_state import StrategyState
from tradepilotai_os.risk.risk_engine import RiskEngine
from tradepilotai_os.strategy.strategy_engine import StrategyEngine


def test_buy_signal_generates_buy_decision_and_levels():
    strategy = StrategyEngine()
    signal = Signal(
        ticker="AAPL",
        signal_type="BUY",
        entry_price=100.0,
        stop_loss=95.0,
        rsi=62.0,
        ema12=30.0,
        ema26=25.0,
    )

    state, trades = strategy.evaluate_signal("AAPL", signal)

    assert state.state == StrategyState.LONG
    assert len(trades) == 1
    assert trades[0].direction == "BUY"
    assert trades[0].stop_loss == 95.0
    assert trades[0].take_profit == 110.0


def test_sell_signal_generates_sell_decision_and_levels():
    strategy = StrategyEngine()
    signal = Signal(
        ticker="AAPL",
        signal_type="SELL",
        entry_price=100.0,
        stop_loss=105.0,
        rsi=38.0,
        ema12=20.0,
        ema26=25.0,
    )

    state, trades = strategy.evaluate_signal("AAPL", signal)

    assert state.state == StrategyState.SHORT
    assert len(trades) == 1
    assert trades[0].direction == "SELL"
    assert trades[0].stop_loss == 105.0
    assert trades[0].take_profit == 90.0


def test_hold_signal_returns_no_trade():
    strategy = StrategyEngine()
    signal = Signal(
        ticker="AAPL",
        signal_type="HOLD",
        entry_price=100.0,
        stop_loss=95.0,
        rsi=50.0,
        ema12=25.0,
        ema26=25.0,
    )

    state, trades = strategy.evaluate_signal("AAPL", signal)

    assert state.state == StrategyState.IDLE
    assert trades == []


def test_invalid_signal_returns_no_trade():
    strategy = StrategyEngine()
    signal = Signal(
        ticker="AAPL",
        signal_type="INVALID",
        entry_price=100.0,
        stop_loss=95.0,
        rsi=60.0,
        ema12=30.0,
        ema26=25.0,
    )

    state, trades = strategy.evaluate_signal("AAPL", signal)

    assert state.state == StrategyState.IDLE
    assert trades == []


def test_position_sizing_uses_account_risk():
    trade = Trade(
        ticker="AAPL",
        direction="BUY",
        entry_time=None,
        entry_price=100.0,
        stop_loss=95.0,
        quantity=1,
    )

    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=500.0)
    assessment = risk_engine.assess_trade(trade)

    assert assessment.permitted is True
    assert assessment.position_size == 200.0
    assert trade.quantity == 200


def test_risk_rejection_when_stop_loss_is_invalid():
    trade = Trade(
        ticker="AAPL",
        direction="BUY",
        entry_time=None,
        entry_price=100.0,
        stop_loss=100.0,
        quantity=1,
    )

    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01)
    assessment = risk_engine.assess_trade(trade)

    assert assessment.permitted is False
    assert "Stop-loss" in assessment.reason
