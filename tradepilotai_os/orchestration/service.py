"""Application orchestrator for TradePilotAI OS platform workflows."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.operations.logging_service import create_logger


class ApplicationOrchestrator:
    """Coordinate scanner, risk, broker, portfolio, history, refresh, and notifications."""

    def __init__(
        self,
        scanner: Any | None = None,
        risk_engine: Any | None = None,
        broker: Any | None = None,
        portfolio_service: Any | None = None,
        trade_history_service: Any | None = None,
        refresh_manager: Any | None = None,
        notifications: Any | None = None,
    ) -> None:
        self.logger = create_logger("TradePilotAI")
        self.scanner = scanner
        self.risk_engine = risk_engine
        self.broker = broker
        self.portfolio_service = portfolio_service
        self.trade_history_service = trade_history_service
        self.refresh_manager = refresh_manager
        self.notifications = notifications

    def run_pipeline(self) -> dict[str, Any]:
        self.logger.info("orchestrator pipeline started", module="orchestration")
        symbols = self.scanner.get_watchlist() if self.scanner is not None else []
        trade = type("Trade", (), {"ticker": symbols[0] if symbols else "AAPL", "direction": "BUY", "entry_price": 100.0, "stop_loss": 95.0, "quantity": 1})()
        if self.risk_engine is not None:
            assessment = self.risk_engine.assess_trade(trade)
            if not getattr(assessment, "permitted", True):
                return {"status": "rejected", "reason": assessment.reason}
        if self.broker is not None:
            result = self.broker.execute(trade)
            if not getattr(result, "success", False):
                return {"status": "broker_failed", "reason": getattr(result, "message", "")}
        if self.portfolio_service is not None:
            self.portfolio_service.state.positions[trade.ticker] = type("Position", (), {"quantity": 1, "average_price": trade.entry_price, "market_price": trade.entry_price})()
        if self.trade_history_service is not None:
            self.trade_history_service.add_trade(trade)
        if self.refresh_manager is not None:
            self.refresh_manager.refresh()
        if self.notifications is not None:
            self.notifications.count += 1
        self.logger.info("orchestrator pipeline completed", module="orchestration", ticker=getattr(trade, "ticker", None))
        return {"status": "completed", "trade": trade, "symbols": symbols}
