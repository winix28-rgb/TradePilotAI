"""Professional trading-workstation dashboard entry point."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from dashboard.layout import card, section, spacer
from dashboard.styles import apply_theme
from dashboard.theme import Theme
from dashboard.views.activity_view import render_activity
from dashboard.views.approval_view import render_approval_queue
from dashboard.views.performance_view import render_performance
from dashboard.views.scanner_view import render_scanner
from dashboard.views.strategy_view import render_strategy
from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.scanner import ScannerService


def _ensure_dashboard_state(state: Any) -> Any:
    """Attach runtime services that the dashboard views expect on startup."""
    if state is None:
        return state

    scanner_service = getattr(state, "market_scanner_service", None)
    if scanner_service is None:
        scanner_service = ScannerService()
        if isinstance(state, dict):
            state["market_scanner_service"] = scanner_service
        else:
            setattr(state, "market_scanner_service", scanner_service)

    portfolio_manager = getattr(state, "portfolio_manager", None)
    if portfolio_manager is None:
        portfolio_manager = PortfolioManager(initial_cash=100000.0)
        if isinstance(state, dict):
            state["portfolio_manager"] = portfolio_manager
        else:
            setattr(state, "portfolio_manager", portfolio_manager)

    portfolio_service = getattr(state, "portfolio_service", None)
    if portfolio_service is None:
        portfolio_service = portfolio_manager
        if isinstance(state, dict):
            state["portfolio_service"] = portfolio_service
        else:
            setattr(state, "portfolio_service", portfolio_service)

    broker = getattr(state, "broker", None)
    if broker is None:
        broker = PaperBroker(initial_cash=100000.0)
        if isinstance(state, dict):
            state["broker"] = broker
        else:
            setattr(state, "broker", broker)

    return state


def render_dashboard(state: Any) -> None:
    """Render the trading workstation layout without changing backend behavior."""
    state = _ensure_dashboard_state(state)

    st.set_page_config(layout="wide", page_title="TradePilotAI", page_icon="📈")
    apply_theme()

    _render_header(state)
    spacer(1)
    _render_kpi_row(state)

    spacer(1)
    row1_left, row1_right = st.columns([0.7, 0.3], gap="large")
    with row1_left:
        _render_panel("Live Strategy", render_strategy, state)
    with row1_right:
        _render_panel("System Status", render_system_status, state)

    spacer(1)
    row2_left, row2_right = st.columns([0.7, 0.3], gap="large")
    with row2_left:
        _render_panel("FTSE Opportunity Scanner", render_scanner, state)
    with row2_right:
        _render_panel("Recent Activity", render_activity, state)

    spacer(1)
    row3_left, row3_right = st.columns([0.7, 0.3], gap="large")
    with row3_left:
        _render_panel("Trade Approval Queue", render_approval_queue, state)
    with row3_right:
        _render_panel("Performance Summary", render_performance, state)


def _render_header(state: Any) -> None:
    """Render the trading-terminal header with the requested status summary."""
    header_col, status_col = st.columns([0.72, 0.28], gap="large")

    with header_col:
        st.markdown(
            "<h1 style='margin-bottom:0.2rem;'>TradePilotAI Professional Trading Platform</h1>",
            unsafe_allow_html=True,
        )
        st.caption("Operational view of the current trading environment")

    with status_col:
        with card():
            status_items = [
                ("Mode", _mode_value(state)),
                ("IG", _connection_status(state)),
                ("Time", datetime.now().strftime("%H:%M:%S")),
                ("Version", Theme.VERSION),
            ]
            columns = st.columns(4, gap="small")
            for column, (label, value) in zip(columns, status_items):
                with column:
                    st.caption(label)
                    st.write(f"**{value}**")


def _render_kpi_row(state: Any) -> None:
    """Render the top KPI row with the requested metrics."""
    portfolio = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio, "state", None)
    broker = getattr(state, "broker", None)
    performance = getattr(state, "performance", None)

    portfolio_value = _portfolio_value(portfolio_state, broker)
    today_pnl = _portfolio_metric(portfolio_state, "today_pnl", getattr(broker, "portfolio", None), "realised_pnl")
    open_positions = _position_count(portfolio_state, broker)
    win_rate = _safe_value(performance, "win_rate")
    exposure = _portfolio_metric(portfolio_state, "exposure", getattr(broker, "portfolio", None), "exposure")

    kpi_items = [
        ("Portfolio Value", portfolio_value),
        ("Today's Profit/Loss", today_pnl),
        ("Open Positions", open_positions),
        ("Win Rate", win_rate),
        ("Risk Exposure", exposure),
    ]

    cols = st.columns(5, gap="large")
    for column, (label, value) in zip(cols, kpi_items):
        with column:
            with card():
                st.caption(label)
                st.markdown(f"<div class='tp-pill' style='font-size:1rem;'>{value}</div>", unsafe_allow_html=True)


def _render_panel(title: str, renderer: Any, state: Any) -> None:
    """Render a bordered content panel for each dashboard section."""
    with st.container():
        section(title)
        with card():
            renderer(state)


def render_system_status(state: Any) -> None:
    """Render the system status section using the existing state structure."""
    controller = getattr(state, "controller", None)
    live_service = getattr(state, "live_strategy_service", None)
    demo_service = getattr(state, "demo_signal_service", None)
    scanner_service = getattr(state, "market_scanner_service", None)
    broker = getattr(state, "broker", None)
    performance = getattr(state, "performance", None)

    status_items = [
        ("Trading Engine", _service_name(controller)),
        ("Broker Connection", _connection_status(state)),
        ("Trading Mode", _mode_value(state)),
        ("Broker", _service_name(broker) or _service_name(live_service)),
        ("Diagnostics", _diagnostic_value(performance)),
    ]

    for label, value in status_items:
        st.write(f"**{label}**")
        st.write(value)
        st.write("")


def _service_name(obj: Any) -> str:
    if obj is None:
        return "N/A"
    return type(obj).__name__


def _mode_value(state: Any) -> str:
    mode = getattr(state, "trading_mode", None)
    if mode is None:
        mode = getattr(state, "mode", None)
    if mode is None:
        if getattr(state, "live_strategy_service", None) is not None:
            return "Live"
        if getattr(state, "demo_signal_service", None) is not None:
            return "Demo"
        return "N/A"
    return str(mode)


def _connection_status(state: Any) -> str:
    for candidate in [
        getattr(state, "connection_status", None),
        getattr(state, "broker_status", None),
        getattr(state, "ig_connection_status", None),
        getattr(getattr(state, "live_strategy_service", None), "status", None),
        getattr(getattr(state, "controller", None), "status", None),
        getattr(getattr(state, "broker", None), "status", None),
    ]:
        if candidate is not None:
            return str(candidate)
    return "Connected" if getattr(state, "live_strategy_service", None) is not None else "N/A"


def _diagnostic_value(performance: Any) -> str:
    if performance is None:
        return "N/A"
    diagnostic = getattr(performance, "diagnostics", None)
    if diagnostic is None:
        return "N/A"
    return str(diagnostic)


def _safe_value(obj: Any, attribute: str) -> str:
    if obj is None:
        return "N/A"
    value = getattr(obj, attribute, None)
    if value is None:
        return "N/A"
    return str(value)


def _portfolio_value(portfolio_state: Any, broker: Any) -> str:
    if portfolio_state is not None:
        cash = getattr(portfolio_state, "cash", 0.0) or 0.0
        unrealised = getattr(portfolio_state, "unrealised_pnl", 0.0) or 0.0
        return f"${cash + unrealised:,.2f}"

    if broker is not None and getattr(broker, "portfolio", None) is not None:
        portfolio = broker.portfolio
        cash = getattr(portfolio, "cash", 0.0) or 0.0
        unrealised = getattr(portfolio, "unrealised_pnl", 0.0) or 0.0
        return f"${cash + unrealised:,.2f}"

    return "N/A"


def _portfolio_metric(portfolio_state: Any, state_attr: str, broker_portfolio: Any, broker_attr: str) -> str:
    if portfolio_state is not None:
        value = getattr(portfolio_state, state_attr, None)
        if value is not None:
            return f"${float(value):,.2f}"

    if broker_portfolio is not None:
        value = getattr(broker_portfolio, broker_attr, None)
        if value is not None:
            return f"${float(value):,.2f}"

    return "N/A"


def _position_count(portfolio_state: Any, broker: Any) -> str:
    if portfolio_state is not None:
        positions = getattr(portfolio_state, "positions", None) or {}
        if positions is not None:
            return str(len(positions))

    if broker is not None and getattr(broker, "portfolio", None) is not None:
        portfolio = broker.portfolio
        positions = getattr(portfolio, "positions", None) or {}
        return str(len(positions))

    return "N/A"


def main(state: Any) -> None:
    """Render the dashboard page using the requested layout."""
    render_dashboard(state)


if __name__ == "__main__":
    main(_ensure_dashboard_state(st.session_state))
