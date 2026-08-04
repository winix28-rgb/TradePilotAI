"""Portfolio workspace presentation using shared dashboard components."""

from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.layout import (
    empty_state,
    render_desktop_layout,
    render_information_banner,
    render_kpi_card,
    render_section,
    spacer,
    render_panel_header,
    render_table,
)
from tradepilotai_os.portfolio.page import PortfolioPage


def _portfolio_page(state: Any) -> PortfolioPage:
    portfolio_service = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    return PortfolioPage(portfolio_service=portfolio_service)


def _render_kpi_row(summary: dict[str, str]) -> None:
    items = [
        ("Portfolio Value", summary.get("portfolio_value", "$0.00")),
        ("Cash", summary.get("cash", "$0.00")),
        ("Buying Power", summary.get("buying_power", "$0.00")),
        ("Today's Profit/Loss", summary.get("today_pnl", "$0.00")),
        ("Total Return", summary.get("total_return", "0.00%")),
    ]

    cols = st.columns(5, gap="small")
    for col, (title, value) in zip(cols, items):
        with col:
            render_kpi_card(
                title=title,
                value=value,
                footer_label="",
                footer_value="",
                show_footer=False,
            )


def _render_positions_table(positions: list[list[Any]]) -> None:
    if not positions:
        empty_state("No open positions")
        return

    rows = []
    for row in positions:
        rows.append(
            {
                "Symbol": row[0],
                "Qty": row[1],
                "Entry": row[2],
                "Current": row[3],
            }
        )

    render_table(
        rows=rows,
        columns=["Symbol", "Qty", "Entry", "Current"],
        numeric_columns=["Qty", "Entry", "Current"],
    )


def _render_summary_table(summary: dict[str, str]) -> None:
    rows = [
        {"Metric": "Portfolio Value", "Value": summary.get("portfolio_value", "$0.00")},
        {"Metric": "Cash", "Value": summary.get("cash", "$0.00")},
        {"Metric": "Buying Power", "Value": summary.get("buying_power", "$0.00")},
        {"Metric": "Today's Profit/Loss", "Value": summary.get("today_pnl", "$0.00")},
        {"Metric": "Total Return", "Value": summary.get("total_return", "0.00%")},
        {"Metric": "Unrealised Profit/Loss", "Value": summary.get("unrealised_pnl", "$0.00")},
        {"Metric": "Realised Profit/Loss", "Value": summary.get("realised_pnl", "$0.00")},
    ]

    render_table(rows=rows, columns=["Metric", "Value"])


def _render_allocation_overview() -> None:
    st.write("Portfolio Allocation")
    st.write("Sector Allocation")
    st.write("Portfolio Growth")
    st.write("Monthly Returns")


def _render_pnl_table(summary: dict[str, str]) -> None:
    rows = [
        {"Metric": "Unrealised Profit/Loss", "Value": summary.get("unrealised_pnl", "$0.00")},
        {"Metric": "Realised Profit/Loss", "Value": summary.get("realised_pnl", "$0.00")},
    ]
    render_table(rows=rows, columns=["Metric", "Value"])


def render_portfolio(state: Any) -> None:
    """Render Portfolio workspace with shared dashboard presentation components."""
    render_desktop_layout()

    page = _portfolio_page(state)
    summary = page._build_summary()
    positions = page._build_positions()

    render_panel_header("Portfolio Overview")
    st.write("Shared component layout")

    spacer(1)
    _render_kpi_row(summary)

    spacer(1)
    main_left, main_right = st.columns([0.65, 0.35], gap="small")
    with main_left:
        render_section("Open Positions", lambda: _render_positions_table(positions))
    with main_right:
        render_section("Summary", lambda: _render_summary_table(summary))

    spacer(1)
    bottom_left, bottom_right = st.columns([0.5, 0.5], gap="small")
    with bottom_left:
        render_section("Allocation Overview", _render_allocation_overview)
    with bottom_right:
        render_section("Profit/Loss", lambda: _render_pnl_table(summary))

    spacer(1)
    render_information_banner("Status", page.build_status_bar(container=page._resolve_container()))
