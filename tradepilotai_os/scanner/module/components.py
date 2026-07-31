"""Reusable scanner dashboard widgets."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import Card, DataTable, SectionHeader


class ScannerSummaryCard(Card):
    """Display the top summary statistics for the scanner workspace."""

    def __init__(self, summary: dict[str, Any]) -> None:
        body = [
            f"Universe: {summary.get('universe', 'N/A')}",
            f"Symbols Scanned: {summary.get('symbols_scanned', '0')}",
            f"Scan Duration: {summary.get('scan_duration', 'N/A')}",
            f"Signals Found: {summary.get('signals_found', '0')}",
            f"Buy Signals: {summary.get('buy_signals', '0')}",
            f"Sell Signals: {summary.get('sell_signals', '0')}",
            f"Watch List Count: {summary.get('watch_list_count', '0')}",
            f"Last Scan Time: {summary.get('last_scan_time', 'N/A')}",
        ]
        super().__init__(title="Top Summary", body=body)


class ScannerPipelineStatus(Card):
    """Display pipeline stage status using the shared card component."""

    def __init__(self, pipeline: dict[str, Any]) -> None:
        body = [
            f"Market Data: {pipeline.get('market_data', 'Waiting')}",
            f"Indicators: {pipeline.get('indicators', 'Waiting')}",
            f"Strategy: {pipeline.get('strategy', 'Waiting')}",
            f"Risk: {pipeline.get('risk', 'Waiting')}",
            f"Complete: {pipeline.get('complete', 'Waiting')}",
        ]
        super().__init__(title="Pipeline Status", body=body)


class ScannerBuyCandidatesTable(DataTable):
    """Render scanner candidates in a shared table component."""

    def __init__(self, rows: list[dict[str, Any]], title: str = "Buy Candidates") -> None:
        table_rows = [
            [item.get("symbol", "-"), item.get("company", "-"), item.get("price", "-"), item.get("rsi", "-"), item.get("ema_trend", "-"), item.get("signal", "-"), item.get("confidence", "-"), item.get("risk_rating", "-")] for item in rows
        ]
        super().__init__(headers=["Symbol", "Company", "Price", "RSI", "EMA Trend", "Signal", "Confidence", "Risk"], rows=table_rows)
        self.title = title

    def render(self) -> str:
        return f"[{self.title}]\n{super().render()}"


class ScannerWatchListTable(DataTable):
    """Render watch-list rows using the shared table component."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        table_rows = [[item.get("symbol", "-"), item.get("reason", "-"), item.get("last_signal", "-"), item.get("status", "-")] for item in rows]
        super().__init__(headers=["Symbol", "Reason", "Last Signal", "Status"], rows=table_rows)


class ScannerSignalDetail(Card):
    """Display a detailed signal view using the shared card component."""

    def __init__(self, detail: dict[str, Any]) -> None:
        body = [
            f"Symbol: {detail.get('symbol', 'N/A')}",
            f"Company Name: {detail.get('company_name', 'N/A')}",
            f"Latest Price: {detail.get('latest_price', 'N/A')}",
            f"RSI: {detail.get('rsi', 'N/A')}",
            f"EMA12: {detail.get('ema12', 'N/A')}",
            f"EMA26: {detail.get('ema26', 'N/A')}",
            f"Strategy Reason: {detail.get('strategy_reason', 'N/A')}",
            f"Risk Summary: {detail.get('risk_summary', 'N/A')}",
            f"Confidence Score: {detail.get('confidence_score', '0')}",
            f"Suggested Stop Loss: {detail.get('suggested_stop_loss', 'N/A')}",
            f"Suggested Take Profit: {detail.get('suggested_take_profit', 'N/A')}",
        ]
        super().__init__(title="Signal Detail", body=body)
