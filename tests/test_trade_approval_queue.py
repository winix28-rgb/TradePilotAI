from __future__ import annotations

from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.orchestration.approval_queue import TradeApprovalQueue
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk.risk_engine import RiskEngine


def test_queue_enqueues_trade_signals_from_scan_results() -> None:
    broker = PaperBroker(initial_cash=100000.0)
    portfolio = PortfolioManager(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    queue = TradeApprovalQueue(
        portfolio_manager=portfolio,
        broker=broker,
        risk_engine=risk_engine,
    )

    signal = TradeSignal(
        symbol="AAPL",
        signal="BUY",
        confidence=85,
        price=100.0,
        rsi=25.0,
        ema12=102.0,
        ema26=98.0,
        stop_loss=95.0,
        target=106.0,
        reasons=["Bullish setup"],
    )

    queue.load_from_scan_results({"results": [{"ticker": "AAPL", "raw": signal}]})

    assert len(queue.pending_trades) == 1
    assert queue.pending_trades[0] is signal


def test_queue_rejects_duplicate_position_and_keeps_signal_pending() -> None:
    broker = PaperBroker(initial_cash=100000.0)
    portfolio = PortfolioManager(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    queue = TradeApprovalQueue(
        portfolio_manager=portfolio,
        broker=broker,
        risk_engine=risk_engine,
    )

    signal = TradeSignal(
        symbol="TSLA",
        signal="BUY",
        confidence=80,
        price=200.0,
        rsi=20.0,
        ema12=205.0,
        ema26=195.0,
        stop_loss=190.0,
        target=212.0,
        reasons=["Bullish setup"],
    )

    queue.load_from_scan_results({"results": [{"ticker": "TSLA", "raw": signal}]})

    portfolio.state.positions["TSLA"] = type("Position", (), {"quantity": 1, "average_price": 200.0, "market_price": 200.0})()
    outcome = queue.approve_trade(signal)

    assert outcome["approved"] is False
    assert "duplicate" in outcome["reason"].lower()
    assert len(queue.pending_trades) == 1


def test_queue_approves_trade_and_executes_via_broker() -> None:
    broker = PaperBroker(initial_cash=100000.0)
    portfolio = PortfolioManager(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    queue = TradeApprovalQueue(
        portfolio_manager=portfolio,
        broker=broker,
        risk_engine=risk_engine,
    )

    signal = TradeSignal(
        symbol="NVDA",
        signal="BUY",
        confidence=90,
        price=120.0,
        rsi=28.0,
        ema12=123.0,
        ema26=118.0,
        stop_loss=114.0,
        target=127.0,
        reasons=["Bullish setup"],
    )

    queue.load_from_scan_results({"results": [{"ticker": "NVDA", "raw": signal}]})

    outcome = queue.approve_trade(signal)

    assert outcome["approved"] is True
    assert broker.executed_trades
    assert queue.approved_trades[-1].symbol == "NVDA"
