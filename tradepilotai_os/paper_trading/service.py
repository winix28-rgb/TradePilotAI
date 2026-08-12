"""Paper-trading service facade for the TradePilotAI OS."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from tradepilotai_os.broker.base import ExecutionResult
from tradepilotai_os.models.trade import Trade
from tradepilotai_os.risk.risk_engine import RiskAssessment

from .engine import PaperPortfolioEngine
from .exit_engine import ExitEngine
from .journal_service import JournalService
from .position_monitor import PositionMonitor


class PaperTradingService:
    """Thin facade over the paper portfolio engine."""

    def __init__(
        self,
        *,
        portfolio_engine: PaperPortfolioEngine | None = None,
        position_monitor: PositionMonitor | None = None,
        exit_engine: ExitEngine | None = None,
        journal_service: JournalService | None = None,
        initial_capital: float = 100000.0,
    ) -> None:
        self.portfolio_engine = portfolio_engine or PaperPortfolioEngine(initial_capital=initial_capital)
        self.position_monitor = position_monitor or PositionMonitor(portfolio_engine=self.portfolio_engine)
        self.exit_engine = exit_engine or ExitEngine(portfolio_engine=self.portfolio_engine)
        self.journal_service = journal_service or JournalService()

    def create_portfolio(self, initial_capital: float | None = None) -> Any:
        return self.portfolio_engine.create_portfolio(initial_capital=initial_capital)

    def get_portfolio(self) -> Any:
        return self.portfolio_engine.get_portfolio()

    def get_summary(self) -> dict[str, Any]:
        return self.portfolio_engine.get_summary()

    def get_open_positions(self) -> list[dict[str, Any]]:
        return [asdict(position) for position in self.portfolio_engine.get_open_positions()]

    def get_closed_trades(self) -> list[dict[str, Any]]:
        return [asdict(trade) for trade in self.portfolio_engine.get_closed_trades()]

    def get_statistics(self) -> dict[str, Any]:
        return asdict(self.portfolio_engine.get_statistics())

    def open_position(
        self,
        *,
        trade: Trade,
        strategy_id: str = "",
        strategy_name: str = "",
        decision_id: str = "",
        risk_assessment: RiskAssessment | None = None,
        execution_result: ExecutionResult | None = None,
        reason: str = "",
    ) -> Any:
        return self.portfolio_engine.open_position(
            trade=trade,
            strategy_id=strategy_id,
            strategy_name=strategy_name,
            decision_id=decision_id,
            risk_assessment=risk_assessment,
            execution_result=execution_result,
            reason=reason,
        )

    def close_position(self, position_id: str, exit_price: float, reason: str, *, costs: float = 0.0, exit_date: str | None = None) -> Any:
        _ = costs
        _ = exit_date
        return self.exit_engine.close_position(position_id, exit_price=exit_price, reason=reason)

    def update_market_price(self, symbol: str, current_price: float) -> Any:
        return self.portfolio_engine.update_market_price(symbol, current_price)

    def update_all_prices(self, prices: dict[str, float]) -> list[Any]:
        return self.portfolio_engine.update_all_prices(prices)

    def refresh_portfolio(self, strategy_context: dict[str, Any] | None = None) -> dict[str, Any]:
        refresh_result = self.position_monitor.refresh()
        closed_trades = self.exit_engine.process_exits(strategy_context=strategy_context)
        workspace = self.get_workspace_data()
        refresh_result["closed_trades"] = closed_trades
        workspace["refresh_result"] = refresh_result
        return workspace

    def evaluate_exits(self, strategy_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.exit_engine.process_exits(strategy_context=strategy_context)

    def manual_exit(self, position_id: str, reason: str = "MANUAL_EXIT", explanation: str = "") -> Any:
        return self.exit_engine.close_position(position_id, reason=reason, explanation=explanation)

    def reset_portfolio(self, initial_capital: float | None = None) -> Any:
        return self.portfolio_engine.reset_portfolio(initial_capital=initial_capital)

    def get_workspace_data(self) -> dict[str, Any]:
        summary = self.get_summary()
        portfolio = self.get_portfolio()
        statistics = self.get_statistics()
        audit_events = self.portfolio_engine.get_audit_events()
        self.journal_service.consume_events(audit_events)
        journal_entries = self.journal_service.get_entries()
        journal_summary = self.journal_service.get_summary(journal_entries)

        return {
            "summary": summary,
            "portfolio": asdict(portfolio),
            "open_positions": self.get_open_positions(),
            "closed_trades": self.get_closed_trades(),
            "statistics": statistics,
            "portfolio_statistics": statistics,
            "audit_events": audit_events,
            "trade_journal": {
                "entries": journal_entries,
                "summary": journal_summary,
            },
        }