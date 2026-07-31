"""Dashboard page view rendering helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.components.metric_card import MetricCard
from dashboard.layout import card, page_header, section, spacer, two_columns
from dashboard.styles import apply_theme
from dashboard.views.strategy_view import render_demo_trading, render_strategy


def render_dashboard(state: Any) -> None:
    """Render the dashboard shell and top-level sections."""
    apply_theme()

    page_header(
        "TradePilotAI Professional Trading Platform",
        "Operational view of the current trading environment",
    )

    spacer(1)

    top_metrics = [
        MetricCard(
            title="Engine Status",
            value=_safe_status(getattr(state, "demo_signal_service", None), "engine"),
            delta="",
            help_text="Live engine health",
        ),
        MetricCard(
            title="Connection Status",
            value=_safe_status(getattr(state, "live_strategy_service", None), "connection"),
            delta="",
            help_text="Broker and data feed connection",
        ),
        MetricCard(
            title="Mode",
            value=_safe_status(getattr(state, "market_scanner_service", None), "mode"),
            delta="",
            help_text="Current operating mode",
        ),
        MetricCard(
            title="Profit Factor",
            value=_safe_value(getattr(state, "performance", None), "profit_factor"),
            delta="",
            help_text="Strategy performance metric",
        ),
    ]

    cols = st.columns(4, gap="large")
    for col, metric in zip(cols, top_metrics):
        with col:
            metric.render()

    spacer(2)

    left_col, right_col = two_columns(2, 1)

    with left_col:
        with st.container():
            section("Live Strategy")
            with card():
                render_strategy(state)

        spacer(1)

        with st.container():
            section("Demo Trading")
            with card():
                render_demo_trading(state)

        spacer(1)

        with st.container():
            section("FTSE Opportunity Scanner")
            with card():
                from dashboard.views.scanner_view import render_scanner

                render_scanner(state)

    with right_col:
        with st.container():
            section("System Status")
            with card():
                render_system_status(state)

        spacer(1)

        with st.container():
            section("Recent Activity")
            with card():
                from dashboard.views.activity_view import render_activity

                render_activity(state)

        spacer(1)

        with st.container():
            section("Performance Summary")
            with card():
                from dashboard.views.performance_view import render_performance

                render_performance(state)

        spacer(1)

        with st.container():
            section("Trade Approval Queue")
            with card():
                from dashboard.views.approval_view import render_approval_queue

                render_approval_queue(state)


def render_system_status(state: Any) -> None:
    """Render the system status summary."""
    controller = getattr(state, "controller", None)
    live_service = getattr(state, "live_strategy_service", None)
    demo_service = getattr(state, "demo_signal_service", None)
    scanner_service = getattr(state, "market_scanner_service", None)

    status_items = [
        ("Controller", type(controller).__name__ if controller is not None else "Unavailable"),
        ("Live Strategy", type(live_service).__name__ if live_service is not None else "Unavailable"),
        ("Demo Signals", type(demo_service).__name__ if demo_service is not None else "Unavailable"),
        ("Scanner", type(scanner_service).__name__ if scanner_service is not None else "Unavailable"),
    ]

    for label, value in status_items:
        st.write(f"{label}: {value}")


def _safe_status(obj: Any, attribute: str) -> str:
    if obj is None:
        return "Unavailable"
    value = getattr(obj, attribute, None)
    if value is None:
        return "Unavailable"
    return str(value)


def _safe_value(obj: Any, attribute: str) -> str:
    if obj is None:
        return "N/A"
    value = getattr(obj, attribute, None)
    if value is None:
        return "N/A"
    return str(value)
