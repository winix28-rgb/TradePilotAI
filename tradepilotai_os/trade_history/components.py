"""Reusable UI widgets for the Trade History workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import Card, DataTable, KPIChartCard


class TradeHistoryKpiCard(KPIChartCard):
    """Render a KPI card for the trade history summary."""

    def __init__(self, title: str, value: str, subtitle: str | None = None) -> None:
        super().__init__(title=title, value=value, subtitle=subtitle)


class TradeFiltersCard(Card):
    """Display a compact set of filter state values."""

    def __init__(self, filters: dict[str, Any]) -> None:
        body = [
            f"Date Range: {filters.get('date_range', 'All')}",
            f"Symbol: {filters.get('symbol', 'All')}",
            f"Strategy: {filters.get('strategy', 'All')}",
            f"Direction: {filters.get('direction', 'All')}",
            f"Status: {filters.get('status', 'All')}",
            f"P/L: {filters.get('profit_loss', 'All')}",
            f"Account: {filters.get('account', 'All')}",
        ]
        super().__init__(title="Filters", body=body)


class TradeHistoryTable(DataTable):
    """Render the trade journal table."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        table_rows = [
            [
                item.get("trade_id", "-"),
                item.get("symbol", "-"),
                item.get("company", "-"),
                item.get("direction", "-"),
                item.get("quantity", "-"),
                item.get("entry_price", "-"),
                item.get("exit_price", "-"),
                item.get("entry_time", "-"),
                item.get("exit_time", "-"),
                item.get("duration", "-"),
                item.get("gross_pnl", "-"),
                item.get("net_pnl", "-"),
                item.get("status", "-"),
                item.get("strategy", "-"),
                item.get("exit_reason", "-"),
            ]
            for item in rows
        ]
        super().__init__(
            headers=[
                "Trade ID",
                "Symbol",
                "Company",
                "Direction",
                "Quantity",
                "Entry Price",
                "Exit Price",
                "Entry Time",
                "Exit Time",
                "Duration",
                "Gross P&L",
                "Net P&L",
                "Status",
                "Strategy",
                "Exit Reason",
            ],
            rows=table_rows,
        )


class TradeDetailCard(Card):
    """Render the selected trade's detailed information."""

    def __init__(self, trade: dict[str, Any]) -> None:
        body = [
            f"Trade ID: {trade.get('trade_id', 'N/A')}",
            f"Timeline: {', '.join(trade.get('timeline', []))}",
            f"Entry Reason: {trade.get('entry_reason', 'N/A')}",
            f"Exit Reason: {trade.get('exit_reason', 'N/A')}",
            f"Strategy Explanation: {trade.get('strategy_explanation', 'N/A')}",
            f"Risk Assessment: {trade.get('risk_assessment', 'N/A')}",
            f"Stop Loss: {trade.get('stop_loss', 'N/A')}",
            f"Take Profit: {trade.get('take_profit', 'N/A')}",
            f"Commission: {trade.get('commission', 'N/A')}",
            f"Slippage: {trade.get('slippage', 'N/A')}",
            f"Position Sizing: {trade.get('position_sizing', 'N/A')}",
            f"Notes: {trade.get('notes', 'Placeholder')}",
            f"Related Events: {', '.join(trade.get('related_events', []))}",
        ]
        super().__init__(title="Trade Detail", body=body)
