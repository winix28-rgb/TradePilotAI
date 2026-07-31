"""Reusable UI widgets for the Live Trading workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import Card, DataTable, KPIChartCard


class LiveTradingKpiCard(KPIChartCard):
    """Display a KPI card for the live-trading workspace."""

    def __init__(self, title: str, value: str, subtitle: str | None = None) -> None:
        super().__init__(title=title, value=value, subtitle=subtitle)


class OrderTicketCard(Card):
    """Render the order-ticket form summary."""

    def __init__(self, request: dict[str, Any]) -> None:
        body = [
            f"Symbol: {request.get('symbol', 'N/A')}",
            f"Company: {request.get('company', 'N/A')}",
            f"Direction: {request.get('direction', 'N/A')}",
            f"Quantity: {request.get('quantity', 0)}",
            f"Type: {request.get('order_type', 'MARKET')}",
            f"Entry Price: {request.get('entry_price', 'N/A')}",
            f"Stop Loss: {request.get('stop_loss', 'N/A')}",
            f"Take Profit: {request.get('take_profit', 'N/A')}",
            f"Estimated Risk (£): {request.get('estimated_risk', 'N/A')}",
            f"Estimated Reward (£): {request.get('estimated_reward', 'N/A')}",
            f"Risk : Reward: {request.get('risk_reward', '1:2')}",
            f"Estimated Margin: {request.get('estimated_margin', 'N/A')}",
        ]
        super().__init__(title="Order Ticket", body=body)


class ValidationCard(Card):
    """Render pre-trade validation results."""

    def __init__(self, validations: dict[str, str]) -> None:
        body = [f"{name}: {value}" for name, value in validations.items()]
        super().__init__(title="Pre-Trade Validation", body=body)


class OrderTable(DataTable):
    """Render open orders using the shared table component."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        table_rows = [[item.get("order_id", "-"), item.get("symbol", "-"), item.get("order_type", "-"), item.get("quantity", "-"), item.get("status", "-"), item.get("submitted_time", "-")] for item in rows]
        super().__init__(headers=["Order ID", "Symbol", "Type", "Quantity", "Status", "Submitted Time"], rows=table_rows)


class PositionTable(DataTable):
    """Render open positions using the shared table component."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        table_rows = [[item.get("symbol", "-"), item.get("quantity", "-"), item.get("entry", "-"), item.get("current_price", "-"), item.get("unrealised_pnl", "-"), item.get("risk", "-"), item.get("stop", "-"), item.get("target", "-")] for item in rows]
        super().__init__(headers=["Symbol", "Quantity", "Entry", "Current Price", "Unrealised P&L", "Risk", "Stop", "Target"], rows=table_rows)


class TimelineCard(Card):
    """Render the order timeline."""

    def __init__(self, steps: list[str]) -> None:
        super().__init__(title="Order Timeline", body=steps)
