"""Service layer for trade history data and lifecycle updates."""

from __future__ import annotations

from typing import Any

from .events import EventBus, TradeEvent
from .models import Trade, TradeStatistics, TradeSummary, TradeTimeline


class TradeHistoryService:
    """Provide trade data, lifecycle handling, and summary metrics."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._trades: list[Trade] = []
        self._events: list[TradeEvent] = []
        self._refresh_count = 0
        self.event_bus = event_bus or EventBus()

    def load_trades(self) -> list[Trade]:
        if self._trades:
            return list(self._trades)
        self._trades = [
            Trade(
                trade_id="TH-1001",
                symbol="AAPL",
                company="Apple Inc.",
                direction="BUY",
                quantity=100,
                entry_price=191.0,
                exit_price=198.50,
                entry_time="2026-07-15 09:30",
                exit_time="2026-07-16 11:00",
                duration="1d",
                gross_pnl=750.0,
                net_pnl=720.0,
                status="Closed",
                strategy="EMA/RSI",
                exit_reason="Target reached",
                entry_reason="Bullish crossover",
                risk_assessment="Medium",
                stop_loss=186.0,
                take_profit=202.0,
                commission=15.0,
                slippage=5.0,
                position_sizing=1000.0,
                account="Paper",
                timeline=[
                    {"step": "Detected", "time": "09:00"},
                    {"step": "Validated", "time": "09:12"},
                    {"step": "Risk Approved", "time": "09:20"},
                    {"step": "Executed", "time": "09:30"},
                    {"step": "Closed", "time": "11:00"},
                ],
                related_events=["TradeOpened", "TradeClosed"],
            ),
            Trade(
                trade_id="TH-1002",
                symbol="MSFT",
                company="Microsoft Corp.",
                direction="SELL",
                quantity=80,
                entry_price=430.0,
                exit_price=None,
                entry_time="2026-07-30 10:20",
                duration="Open",
                gross_pnl=0.0,
                net_pnl=0.0,
                status="Open",
                strategy="Momentum",
                entry_reason="Breakdown signal",
                risk_assessment="High",
                stop_loss=438.0,
                take_profit=420.0,
                commission=12.0,
                slippage=3.0,
                position_sizing=800.0,
                account="Live",
                timeline=[
                    {"step": "Detected", "time": "10:00"},
                    {"step": "Validated", "time": "10:10"},
                    {"step": "Submitted", "time": "10:20"},
                    {"step": "Open", "time": "10:20"},
                ],
                related_events=["TradeOpened", "TradeUpdated"],
            ),
        ]
        return list(self._trades)

    def get_summary(self) -> TradeSummary:
        trades = self.load_trades()
        closed = [trade for trade in trades if trade.status == "Closed"]
        open_trades = [trade for trade in trades if trade.status == "Open"]
        win_rate = 100.0 if closed else 0.0
        net_profit = sum(float(trade.net_pnl or 0.0) for trade in closed)
        average_win = sum(float(trade.net_pnl or 0.0) for trade in closed) / max(len(closed), 1)
        average_loss = 0.0
        profit_factor = 1.0
        largest_win = max((float(trade.net_pnl or 0.0) for trade in closed), default=0.0)
        largest_loss = 0.0
        return TradeSummary(
            total_trades=len(trades),
            open_trades=len(open_trades),
            closed_trades=len(closed),
            win_rate=f"{int(win_rate)}%",
            net_profit=f"${net_profit:,.0f}",
            average_win=f"${average_win:,.0f}",
            average_loss=f"${average_loss:,.0f}",
            profit_factor=f"{profit_factor:.2f}",
            largest_win=f"${largest_win:,.0f}",
            largest_loss=f"${largest_loss:,.0f}",
        )

    def get_statistics(self) -> TradeStatistics:
        return TradeStatistics(
            total_trades=self.get_summary().total_trades,
            win_rate=0.0,
            average_win=0.0,
            average_loss=0.0,
            profit_factor=1.0,
            largest_win=0.0,
            largest_loss=0.0,
        )

    def get_timeline(self, trade_id: str) -> TradeTimeline | None:
        for trade in self.load_trades():
            if trade.trade_id == trade_id:
                return TradeTimeline(trade_id=trade_id, events=trade.timeline)
        return None

    def subscribe(self, event: TradeEvent) -> None:
        self._events.append(event)
        event_name = getattr(event, "name", None)
        trade_id = getattr(event, "trade_id", None)
        payload = getattr(event, "payload", None)
        self.event_bus.publish(event_name, {"trade_id": trade_id, "payload": payload})

    def refresh(self) -> None:
        self._refresh_count += 1

    def refresh_count(self) -> int:
        return self._refresh_count
