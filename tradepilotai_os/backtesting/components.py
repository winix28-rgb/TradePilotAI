"""Reusable backtesting dashboard widgets."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import Card, ChartCard, DataTable, KPIChartCard, SectionHeader


class BacktestKpiCard(KPIChartCard):
    """Specialized KPI card for backtest metrics."""

    def __init__(self, title: str, value: str, subtitle: str | None = None) -> None:
        super().__init__(title=title, value=value, subtitle=subtitle)


class BacktestChartCard(ChartCard):
    """Chart card with a backtest-specific title prefix."""

    def __init__(self, title: str, points: list[tuple[str, str]] | None = None) -> None:
        super().__init__(title=title, points=points)


class BacktestStatsTable(DataTable):
    """Simple summary table for backtest statistic rows."""

    def __init__(self, headers: list[str], rows: list[list[Any]]) -> None:
        super().__init__(headers=headers, rows=rows)


class BacktestTradeList(DataTable):
    """Trade list table for sortable-like display."""

    def __init__(self, rows: list[list[Any]]) -> None:
        super().__init__(headers=["Symbol", "Side", "Entry", "Exit", "PnL"], rows=rows)


class BacktestSummarySection(Card):
    """Section card for backtest summary details."""

    def __init__(self, title: str, body: list[str]) -> None:
        super().__init__(title=title, body=body)
