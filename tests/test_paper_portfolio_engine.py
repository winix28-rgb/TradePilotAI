from datetime import datetime, timezone

from dashboard.app import _ensure_dashboard_state
from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.orchestration.approval_queue import TradeApprovalQueue
from tradepilotai_os.paper_trading import IntegratedPaperBroker
from tradepilotai_os.paper_trading import PaperPortfolioEngine
from tradepilotai_os.paper_trading import PaperTradingDataProvider
from tradepilotai_os.paper_trading import PaperTradingPage
from tradepilotai_os.paper_trading import PaperTradingService
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk.risk_engine import RiskEngine


def _trade(symbol: str = "AAPL", direction: str = "BUY", entry_price: float = 100.0, stop_loss: float = 95.0) -> Trade:
    return Trade(
        ticker=symbol,
        direction=direction,
        entry_time=datetime.now(timezone.utc),
        entry_price=entry_price,
        stop_loss=stop_loss,
        quantity=1,
        take_profit=110.0,
    )


def _risk_assessment(engine: RiskEngine, trade: Trade):
    return engine.assess_trade(trade)


def test_create_portfolio_initialises_state() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)

    portfolio = engine.get_portfolio()
    summary = engine.get_summary()
    statistics = engine.get_statistics()

    assert portfolio.cash == 100000.0
    assert portfolio.buying_power == 100000.0
    assert portfolio.portfolio_value == 100000.0
    assert summary["portfolio_value"] == 100000.0
    assert summary["open_positions"] == 0
    assert summary["closed_trades"] == 0
    assert statistics.total_trades == 0
    assert statistics.current_exposure == 0.0


def test_open_position_updates_cash_buying_power_and_value() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    assessment = _risk_assessment(risk_engine, trade)

    position = engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=assessment,
    )

    summary = engine.get_summary()

    assert position is not None
    assert position.quantity == 200
    assert summary["cash"] == 80000.0
    assert summary["buying_power"] == 80000.0
    assert summary["portfolio_value"] == 100000.0
    assert summary["realised_pnl"] == 0.0
    assert summary["unrealised_pnl"] == 0.0
    assert summary["open_positions"] == 1


def test_update_market_price_updates_unrealised_pnl_and_statistics() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    assessment = _risk_assessment(risk_engine, trade)
    engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=assessment,
    )

    position = engine.update_market_price("AAPL", 105.0)
    summary = engine.get_summary()
    statistics = engine.get_statistics()

    assert position is not None
    assert position.current_price == 105.0
    assert position.unrealised_pnl == 1000.0
    assert summary["unrealised_pnl"] == 1000.0
    assert summary["portfolio_value"] == 101000.0
    assert statistics.current_exposure == 21000.0


def test_close_position_updates_realised_pnl_cash_and_statistics() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    assessment = _risk_assessment(risk_engine, trade)
    engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=assessment,
    )

    closed = engine.close_position("AAPL", exit_price=110.0, reason="Target Reached")
    summary = engine.get_summary()
    statistics = engine.get_statistics()

    assert closed is not None
    assert closed.gross_profit == 2000.0
    assert closed.net_profit == 2000.0
    assert summary["cash"] == 102000.0
    assert summary["buying_power"] == 102000.0
    assert summary["realised_pnl"] == 2000.0
    assert summary["open_positions"] == 0
    assert summary["closed_trades"] == 1
    assert statistics.total_trades == 1
    assert statistics.winning_trades == 1
    assert statistics.losing_trades == 0
    assert statistics.win_rate == 100.0
    assert statistics.average_winner == 2000.0


def test_update_all_prices_updates_multiple_positions() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    aapl_trade = _trade("AAPL")
    msft_trade = _trade("MSFT", entry_price=200.0, stop_loss=190.0)
    engine.open_position(
        trade=aapl_trade,
        strategy_id="strategy-a",
        strategy_name="Strategy A",
        decision_id="DEC-001",
        risk_assessment=_risk_assessment(risk_engine, aapl_trade),
    )
    engine.open_position(
        trade=msft_trade,
        strategy_id="strategy-b",
        strategy_name="Strategy B",
        decision_id="DEC-002",
        risk_assessment=_risk_assessment(risk_engine, msft_trade),
    )

    updated = engine.update_all_prices({"AAPL": 102.0, "MSFT": 210.0})

    assert len(updated) == 2
    assert engine.get_summary()["unrealised_pnl"] > 0
    assert engine.get_statistics().current_exposure == 102.0 * 200 + 210.0 * 100


def test_reset_portfolio_clears_state_and_creates_new_portfolio() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=_risk_assessment(risk_engine, trade),
    )
    portfolio_before_reset = engine.get_portfolio().portfolio_id

    engine.reset_portfolio()

    portfolio = engine.get_portfolio()
    summary = engine.get_summary()

    assert portfolio.portfolio_id != portfolio_before_reset
    assert portfolio.cash == 100000.0
    assert len(portfolio.open_positions) == 0
    assert len(portfolio.closed_trades) == 0
    assert summary["open_positions"] == 0
    assert summary["closed_trades"] == 0


def test_portfolio_persists_for_application_lifetime() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    service_one = PaperTradingService(portfolio_engine=engine)
    service_two = PaperTradingService(portfolio_engine=engine)
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)

    service_one.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=_risk_assessment(risk_engine, trade),
    )

    payload = service_two.get_workspace_data()

    assert payload["summary"]["open_positions"] == 1
    assert payload["summary"]["cash"] == 80000.0
    assert len(payload["open_positions"]) == 1


def test_workspace_and_dashboard_use_shared_engine_state() -> None:
    state = _ensure_dashboard_state({})

    assert isinstance(state["paper_portfolio_engine"], PaperPortfolioEngine)
    assert isinstance(state["paper_trading_service"], PaperTradingService)
    assert isinstance(state["paper_execution_broker"], IntegratedPaperBroker)
    assert state["approval_queue"].broker is state["paper_execution_broker"]


def test_approved_trade_creates_open_position_through_queue_and_broker() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    broker = IntegratedPaperBroker(PaperBroker(initial_cash=100000.0), engine)
    portfolio_manager = PortfolioManager(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    queue = TradeApprovalQueue(portfolio_manager=portfolio_manager, broker=broker, risk_engine=risk_engine)
    signal = __import__("tradepilotai_os.models.trade_signal", fromlist=["TradeSignal"]).TradeSignal(
        symbol="AAPL",
        signal="BUY",
        confidence=88,
        price=100.0,
        rsi=28.0,
        ema12=102.0,
        ema26=98.0,
        stop_loss=95.0,
        target=110.0,
        reasons=["Bullish setup"],
    )

    queue.load_from_scan_results({"results": [{"ticker": "AAPL", "raw": signal}]})
    broker.prepare_execution(
        strategy_name="TradePilotAI RSI Mean Reversion",
        decision="EXECUTE",
        reason="Approved by trade queue",
        risk_assessment=risk_engine.assess_trade(queue._build_trade(signal)),
    )

    outcome = queue.approve_trade(signal)
    snapshot = engine.snapshot()

    assert outcome["approved"] is True
    assert snapshot["summary"]["open_positions"] == 1
    assert snapshot["summary"]["cash"] == 80000.0
    assert snapshot["open_positions"][0]["symbol"] == "AAPL"
    assert snapshot["open_positions"][0]["strategy_name"] == "TradePilotAI RSI Mean Reversion"


def test_approval_queue_rejects_trade_without_portfolio_mutation() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    broker = IntegratedPaperBroker(PaperBroker(initial_cash=100000.0), engine)
    portfolio_manager = PortfolioManager(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    queue = TradeApprovalQueue(portfolio_manager=portfolio_manager, broker=broker, risk_engine=risk_engine)
    signal = TradeSignal(
        symbol="AAPL",
        signal="BUY",
        confidence=88,
        price=100.0,
        rsi=28.0,
        ema12=102.0,
        ema26=98.0,
        stop_loss=100.0,
        target=110.0,
        reasons=["Invalid stop loss"],
    )

    queue.load_from_scan_results({"results": [{"ticker": "AAPL", "raw": signal}]})

    outcome = queue.approve_trade(signal)

    assert outcome["approved"] is False
    assert engine.get_summary()["open_positions"] == 0
    assert len(engine.get_audit_events()) == 1


def test_failed_execution_does_not_mutate_portfolio() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    broker = IntegratedPaperBroker(PaperBroker(initial_cash=1.0), engine)
    portfolio_manager = PortfolioManager(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    queue = TradeApprovalQueue(portfolio_manager=portfolio_manager, broker=broker, risk_engine=risk_engine)
    signal = TradeSignal(
        symbol="AAPL",
        signal="BUY",
        confidence=88,
        price=100.0,
        rsi=28.0,
        ema12=102.0,
        ema26=98.0,
        stop_loss=95.0,
        target=110.0,
        reasons=["Bullish setup"],
    )

    queue.load_from_scan_results({"results": [{"ticker": "AAPL", "raw": signal}]})

    outcome = queue.approve_trade(signal)

    assert outcome["approved"] is False
    assert "insufficient cash" in outcome["reason"].lower()
    assert engine.get_summary()["open_positions"] == 0
    assert engine.get_summary()["cash"] == 100000.0
    assert len(engine.get_audit_events()) == 1


def test_workspace_refreshes_from_shared_engine_state() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    service = PaperTradingService(portfolio_engine=engine)
    provider = PaperTradingDataProvider(service=service)
    page = PaperTradingPage(data_provider=provider)

    initial_render = page.render()
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=_risk_assessment(risk_engine, trade),
    )

    refreshed = page.render()

    assert "PAPER TRADING WORKSPACE" in initial_render
    assert "PAPER TRADING WORKSPACE" in refreshed
    assert page.data["summary"]["open_positions"] == 1
    assert page.data["summary"]["cash"] == 80000.0
    assert len(page.data["open_positions"]) == 1


def test_audit_events_are_recorded_for_successful_mutations() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    trade = _trade()
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)

    engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id="DEC-001",
        risk_assessment=_risk_assessment(risk_engine, trade),
    )
    engine.update_market_price("AAPL", 105.0)
    engine.close_position("AAPL", exit_price=110.0, reason="Target Reached")

    events = engine.get_audit_events()

    assert any(event["event"] == "Position Opened" for event in events)
    assert any(event["event"] == "Price Updated" for event in events)
    assert any(event["event"] == "Position Closed" for event in events)
    assert any(event["event"] == "Portfolio Statistics Updated" for event in events)
