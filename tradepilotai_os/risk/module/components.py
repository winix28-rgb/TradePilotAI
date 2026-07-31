"""Reusable UI widgets for the Risk Dashboard workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import Card, DataTable, KPIChartCard


class RiskKpiCard(KPIChartCard):
    """Display a KPI card for the risk dashboard."""

    def __init__(self, title: str, value: str, subtitle: str | None = None) -> None:
        super().__init__(title=title, value=value, subtitle=subtitle)


class ExposureCard(Card):
    """Render exposure data grouped by category."""

    def __init__(self, exposures: list[dict[str, Any]]) -> None:
        body = [f"{item.get('label', '-')} ({item.get('category', '-')}) : {item.get('value', 0)}" for item in exposures]
        super().__init__(title="Portfolio Exposure", body=body)


class PositionRiskTable(DataTable):
    """Render position-risk rows using the shared table component."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        table_rows = [
            [item.get("symbol", "-"), item.get("position_size", "-"), item.get("risk_percent", "-"), item.get("stop_distance", "-"), item.get("unrealised_pnl", "-"), item.get("exposure_percent", "-"), item.get("risk_rating", "-")] for item in rows
        ]
        super().__init__(headers=["Symbol", "Position Size", "Risk %", "Stop Distance", "Unrealised P&L", "Exposure %", "Risk Rating"], rows=table_rows)


class RiskRulesCard(Card):
    """Render configured risk rules and their status."""

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        body = [f"{item.get('name', '-')} -> Current: {item.get('current_value', '-')} / Limit: {item.get('configured_limit', '-')} [{item.get('status', 'OK')}]" for item in rules]
        super().__init__(title="Risk Rules", body=body)


class RiskTimelineCard(Card):
    """Render recent risk timeline events."""

    def __init__(self, events: list[dict[str, Any]]) -> None:
        body = [f"{item.get('event', '-')} @ {item.get('time', '-')}" for item in events]
        super().__init__(title="Risk Timeline", body=body)
