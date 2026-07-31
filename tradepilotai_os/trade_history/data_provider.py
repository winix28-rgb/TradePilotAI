"""Data provider for the Trade History workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.core.container import Container

from .service import TradeHistoryService


class TradeHistoryDataProvider:
    """Resolve trade history data from the app container and runtime state."""

    def __init__(self, container: Container | None = None, service: TradeHistoryService | None = None) -> None:
        self.container = container
        self.service = service

    def get_trade_history_data(self) -> dict[str, Any]:
        service = self.service
        if service is None and self.container is not None:
            service = self.container.resolve(TradeHistoryService)
        if service is None:
            service = TradeHistoryService()

        trades = service.load_trades()
        summary = service.get_summary()
        return {
            "summary": self._summarize(summary),
            "statistics": service.get_statistics(),
            "filters": {
                "date_range": "All",
                "symbol": "All",
                "strategy": "All",
                "direction": "All",
                "status": "All",
                "profit_loss": "All",
                "account": "All",
            },
            "trades": [self._trade_payload(trade) for trade in trades],
            "selected_trade": self._trade_payload(trades[0]) if trades else {},
            "events": [{"name": event.name, "trade_id": event.trade_id} for event in service._events],
        }

    def _summarize(self, summary: Any) -> dict[str, Any]:
        if isinstance(summary, dict):
            return summary
        return {
            "total_trades": getattr(summary, "total_trades", 0),
            "open_trades": getattr(summary, "open_trades", 0),
            "closed_trades": getattr(summary, "closed_trades", 0),
            "win_rate": getattr(summary, "win_rate", "0%"),
            "net_profit": getattr(summary, "net_profit", "$0"),
            "average_win": getattr(summary, "average_win", "$0"),
            "average_loss": getattr(summary, "average_loss", "$0"),
            "profit_factor": getattr(summary, "profit_factor", "0.00"),
            "largest_win": getattr(summary, "largest_win", "$0"),
            "largest_loss": getattr(summary, "largest_loss", "$0"),
        }

    def _trade_payload(self, trade: Any) -> dict[str, Any]:
        return {
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "company": trade.company,
            "direction": trade.direction,
            "quantity": trade.quantity,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "entry_time": trade.entry_time,
            "exit_time": trade.exit_time,
            "duration": trade.duration,
            "gross_pnl": trade.gross_pnl,
            "net_pnl": trade.net_pnl,
            "status": trade.status,
            "strategy": trade.strategy,
            "exit_reason": trade.exit_reason,
            "entry_reason": trade.entry_reason,
            "risk_assessment": trade.risk_assessment,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "commission": trade.commission,
            "slippage": trade.slippage,
            "position_sizing": trade.position_sizing,
            "notes": trade.notes,
            "account": trade.account,
            "timeline": [step.get("step") for step in trade.timeline],
            "strategy_explanation": "EMA crossover confirmed with supportive RSI momentum",
            "related_events": trade.related_events,
        }
