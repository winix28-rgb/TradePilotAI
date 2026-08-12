from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tradepilotai_os.models.trade import Trade
from tradepilotai_os.paper_trading import ExitEngine
from tradepilotai_os.paper_trading import PaperPortfolioEngine
from tradepilotai_os.paper_trading import PaperTradingService
from tradepilotai_os.paper_trading import PositionMonitor
from tradepilotai_os.paper_trading.exit_engine import ExitDecision
from tradepilotai_os.risk.risk_engine import RiskEngine


class StubMarketDataProvider:
    def __init__(self, quotes: dict[str, object]) -> None:
        self.quotes = quotes

    def quote(self, symbol: str):
        value = self.quotes[symbol]
        if isinstance(value, Exception):
            raise value
        return value


class StubStrategy:
    def __init__(self, decision: ExitDecision | None = None, error: Exception | None = None) -> None:
        self.decision = decision
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def should_exit(self, position: Any, context: dict[str, Any] | None = None):
        self.calls.append({"position_id": getattr(position, "position_id", ""), "symbol": getattr(position, "symbol", "")})
        if self.error is not None:
            raise self.error
        return self.decision


class StubStrategyResolver:
    def __init__(self, strategies: dict[str, StubStrategy]) -> None:
        self.strategies = strategies

    def resolve(self, position: Any, context: dict[str, Any] | None = None):
        strategy_id = str(getattr(position, "strategy_id", "") or "")
        return self.strategies.get(strategy_id)


def _open_position(
    engine: PaperPortfolioEngine,
    symbol: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    *,
    direction: str = "BUY",
    strategy_id: str = "rsi_mean_reversion",
    strategy_name: str = "RSI Mean Reversion",
):
    trade = Trade(
        ticker=symbol,
        direction=direction,
        entry_time=datetime.now(timezone.utc),
        entry_price=entry_price,
        stop_loss=stop_loss,
        quantity=1,
        take_profit=take_profit,
    )
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    return engine.open_position(
        trade=trade,
        strategy_id=strategy_id,
        strategy_name=strategy_name,
        decision_id=f"DEC-{symbol}",
        risk_assessment=risk_engine.assess_trade(trade),
    )


def test_manual_exit_closes_by_position_id_and_updates_portfolio() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    position = _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    assert position is not None
    exit_engine = ExitEngine(portfolio_engine=engine)

    closed = exit_engine.close_position(position.position_id, exit_price=110.0, reason="MANUAL_EXIT", explanation="Manual close")

    assert closed is not None
    assert engine.get_summary()["open_positions"] == 0
    assert engine.get_summary()["closed_trades"] == 1
    assert engine.get_summary()["cash"] == 102000.0
    assert closed.net_profit == 2000.0
    assert closed.strategy_id == "rsi_mean_reversion"
    assert closed.strategy_name == "RSI Mean Reversion"


def test_stop_loss_exit_is_triggered() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    engine.update_market_price("AAPL", 94.0)
    exit_engine = ExitEngine(portfolio_engine=engine)

    closed = exit_engine.process_exits()

    assert len(closed) == 1
    assert closed[0]["exit_reason"] == "STOP_LOSS"
    assert any(event["event"] == "STOP_LOSS_TRIGGERED" for event in engine.get_audit_events())


def test_take_profit_exit_is_triggered() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", 100.0, 95.0, 110.0)
    engine.update_market_price("AAPL", 111.0)
    exit_engine = ExitEngine(portfolio_engine=engine)

    closed = exit_engine.process_exits()

    assert len(closed) == 1
    assert closed[0]["exit_reason"] == "TAKE_PROFIT"
    assert any(event["event"] == "TARGET_TRIGGERED" for event in engine.get_audit_events())


def test_strategy_exit_uses_should_exit_contract() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    engine.update_market_price("AAPL", 104.0)
    strategy = StubStrategy(
        decision=ExitDecision(
            should_exit=True,
            exit_reason="STRATEGY_EXIT",
            confidence=0.89,
            explanation="RSI reverted to strategy threshold.",
            exit_type="STRATEGY_EXIT",
        )
    )
    exit_engine = ExitEngine(portfolio_engine=engine, strategy_resolver=StubStrategyResolver({"rsi_mean_reversion": strategy}))

    closed = exit_engine.process_exits()

    assert len(closed) == 1
    assert closed[0]["exit_reason"] == "STRATEGY_EXIT"
    assert closed[0]["exit_explanation"] == "RSI reverted to strategy threshold."
    assert len(strategy.calls) == 1


def test_no_duplicate_close_for_same_position() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    position = _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    assert position is not None
    exit_engine = ExitEngine(portfolio_engine=engine)

    first = exit_engine.close_position(position.position_id, exit_price=108.0, reason="MANUAL_EXIT")
    second = exit_engine.close_position(position.position_id, exit_price=109.0, reason="MANUAL_EXIT")

    assert first is not None
    assert second is None
    assert engine.get_summary()["closed_trades"] == 1


def test_partial_update_failure_does_not_block_other_exits() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", 100.0, 95.0, 130.0, strategy_id="strategy-error", strategy_name="Error Strategy")
    _open_position(engine, "MSFT", 200.0, 190.0, 220.0)
    engine.update_market_price("MSFT", 221.0)

    exit_engine = ExitEngine(
        portfolio_engine=engine,
        strategy_resolver=StubStrategyResolver(
            {
                "strategy-error": StubStrategy(error=RuntimeError("strategy exploded")),
            }
        ),
    )

    closed = exit_engine.process_exits()

    assert len(closed) == 1
    assert closed[0]["symbol"] == "MSFT"
    assert any(event["event"] == "EXIT_EVALUATION_FAILED" for event in engine.get_audit_events())


def test_refresh_portfolio_runs_monitor_then_exit_engine() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", 100.0, 95.0, 110.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider({"AAPL": {"symbol": "AAPL", "price": 112.0, "open": 110.0}}),
    )
    service = PaperTradingService(portfolio_engine=engine, position_monitor=monitor)

    payload = service.refresh_portfolio()

    assert payload["summary"]["open_positions"] == 0
    assert payload["summary"]["closed_trades"] == 1
    assert len(payload["refresh_result"]["closed_trades"]) == 1


def test_closed_trade_contains_full_contract_fields() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    position = _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    assert position is not None
    exit_engine = ExitEngine(portfolio_engine=engine)

    closed = exit_engine.close_position(
        position.position_id,
        exit_price=108.0,
        reason="MANUAL_EXIT",
        explanation="Operator closed position.",
    )

    assert closed is not None
    assert closed.trade_id
    assert closed.position_id
    assert closed.decision_id == "DEC-AAPL"
    assert closed.strategy_id == "rsi_mean_reversion"
    assert closed.strategy_name == "RSI Mean Reversion"
    assert closed.symbol == "AAPL"
    assert closed.entry_date
    assert closed.exit_date
    assert closed.holding_period
    assert closed.entry_price == 100.0
    assert closed.exit_price == 108.0
    assert closed.gross_profit == 1600.0
    assert closed.commission == 0.0
    assert closed.spread_cost == 0.0
    assert closed.slippage_cost == 0.0
    assert closed.net_profit == 1600.0
    assert closed.exit_reason == "MANUAL_EXIT"
    assert closed.exit_explanation == "Operator closed position."


def test_portfolio_statistics_and_buying_power_update_after_close() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    position = _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    assert position is not None
    exit_engine = ExitEngine(portfolio_engine=engine)

    exit_engine.close_position(position.position_id, exit_price=110.0, reason="MANUAL_EXIT")
    stats = engine.get_statistics()
    summary = engine.get_summary()

    assert summary["cash"] == 102000.0
    assert summary["buying_power"] == 102000.0
    assert summary["portfolio_value"] == 102000.0
    assert stats.total_trades == 1
    assert stats.winning_trades == 1
    assert stats.losing_trades == 0
    assert stats.win_rate == 100.0
    assert stats.average_winner == 2000.0


def test_audit_events_include_required_portfolio_transition_fields() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    position = _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    assert position is not None
    exit_engine = ExitEngine(portfolio_engine=engine)

    exit_engine.close_position(position.position_id, exit_price=109.0, reason="MANUAL_EXIT")
    events = engine.get_audit_events()

    closed_events = [event for event in events if event["event"] == "POSITION_CLOSED"]
    assert closed_events
    details = closed_events[-1]["details"]
    assert details["position_id"] == position.position_id
    assert details["trade_id"]
    assert details["decision_id"] == position.decision_id
    assert "old_portfolio_value" in details
    assert "new_portfolio_value" in details


def test_journal_and_performance_events_are_emitted() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    position = _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    assert position is not None
    exit_engine = ExitEngine(portfolio_engine=engine)

    exit_engine.close_position(position.position_id, exit_price=107.0, reason="MANUAL_EXIT")
    events = engine.get_audit_events()

    assert any(event["event"] == "TRADE_JOURNAL_EVENT" for event in events)
    assert any(event["event"] == "PERFORMANCE_EVENT" for event in events)


def test_failed_price_lookup_does_not_stop_exit_processing() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", 100.0, 95.0, 130.0)
    _open_position(engine, "MSFT", 200.0, 190.0, 205.0)
    engine.update_market_price("AAPL", 94.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider(
            {
                "AAPL": RuntimeError("lookup failed"),
                "MSFT": {"symbol": "MSFT", "price": 206.0, "open": 201.0},
            }
        ),
    )
    service = PaperTradingService(portfolio_engine=engine, position_monitor=monitor)

    payload = service.refresh_portfolio()

    assert payload["summary"]["closed_trades"] >= 1
    assert payload["summary"]["open_positions"] <= 1
    assert len(payload["refresh_result"]["failed_symbols"]) == 1
