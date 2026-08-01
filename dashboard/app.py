"""Professional trading-workstation dashboard entry point."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from dashboard.layout import card, empty_state, section, spacer
from dashboard.shell import ApplicationShell
from dashboard.styles import apply_theme
from dashboard.theme import Theme
from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.orchestration.approval_queue import TradeApprovalQueue
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk.module.service import RiskDashboardService
from tradepilotai_os.risk.risk_engine import RiskEngine
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

    risk_engine = getattr(state, "risk_engine", None)
    if risk_engine is None:
        risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
        if isinstance(state, dict):
            state["risk_engine"] = risk_engine
        else:
            setattr(state, "risk_engine", risk_engine)

    risk_service = getattr(state, "risk_service", None)
    if risk_service is None:
        risk_service = RiskDashboardService(
            portfolio_manager=portfolio_manager,
            broker=broker,
            risk_engine=risk_engine,
        )
        if isinstance(state, dict):
            state["risk_service"] = risk_service
        else:
            setattr(state, "risk_service", risk_service)

    approval_queue = getattr(state, "approval_queue", None)
    if approval_queue is None:
        approval_queue = TradeApprovalQueue(
            portfolio_manager=portfolio_manager,
            broker=broker,
            risk_engine=risk_engine,
        )
        if isinstance(state, dict):
            state["approval_queue"] = approval_queue
        else:
            setattr(state, "approval_queue", approval_queue)

    if getattr(state, "approval_controller", None) is None:
        if isinstance(state, dict):
            state["approval_controller"] = approval_queue
            state["approval_service"] = approval_queue
        else:
            setattr(state, "approval_controller", approval_queue)
            setattr(state, "approval_service", approval_queue)

    return state


def _configure_streamlit_runtime() -> None:
    """Disable Streamlit's built-in sidebar page navigation before any UI is created."""
    try:
        st.set_option("client.showSidebarNavigation", False)
    except Exception:
        pass


def render_dashboard(state: Any) -> None:
    """Render the professional trading command centre without changing backend behavior."""
    state = _ensure_dashboard_state(state)

    st.set_page_config(layout="wide", page_title="TradePilotAI", page_icon="📈")
    _configure_streamlit_runtime()
    apply_theme()

    _render_header(state)
    spacer(1)
    _render_kpi_row(state)

    spacer(1)
    scanner_col, approval_col = st.columns([0.6, 0.4], gap="small")
    with scanner_col:
        _render_panel("FTSE Opportunity Scanner", lambda s: _render_scanner_panel(s), state)
    with approval_col:
        _render_panel("Trade Approval Queue", lambda s: _render_approval_panel(s), state)

    spacer(1)
    positions_col, allocation_col = st.columns([0.7, 0.3], gap="small")
    with positions_col:
        _render_panel("Open Positions", lambda s: _render_positions_panel(s), state)
    with allocation_col:
        _render_panel("Portfolio Allocation", lambda s: _render_allocation_panel(s), state)

    spacer(1)
    activity_col, summary_col = st.columns([0.55, 0.45], gap="small")
    with activity_col:
        _render_panel("Recent Activity", lambda s: _render_activity_panel(s), state)
    with summary_col:
        _render_panel("AI Market Summary", lambda s: _render_ai_summary_panel(s), state)


def _render_header(state: Any) -> None:
    """Render the trading-terminal header with the requested status summary."""
    header_col, status_col = st.columns([0.72, 0.28], gap="small")

    with header_col:
        st.markdown(
            "<h1 class='tp-page-title'>TradePilotAI Professional Trading Platform</h1>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='tp-page-caption'>Operational view of the current trading environment</div>", unsafe_allow_html=True)

    with status_col:
        with card():
            st.markdown("<div class='tp-status-badge'>● LIVE</div>", unsafe_allow_html=True)
            st.caption("Connection")
            st.write(f"**{_connection_status(state)}**")


def _strip_workspace_navigation_markup(content: str) -> str:
    """Remove duplicated workspace navigation chrome from rendered page content."""
    lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("=") or stripped.startswith("["):
            continue
        if stripped.startswith("Dashboard /") or stripped.startswith("Home /"):
            continue
        if stripped.startswith("Scanner") and stripped.endswith("[live]"):
            continue
        if stripped.startswith("Portfolio") and stripped.endswith("[balanced]"):
            continue
        if stripped.startswith("Risk") and stripped.endswith("[live]"):
            continue
        if stripped.startswith("Trade History") and stripped.endswith("[live]"):
            continue
        if stripped.startswith("Live Trading") and stripped.endswith("[live]"):
            continue
        if stripped.startswith("Strategy") and stripped.endswith("[active]"):
            continue
        if stripped.startswith("Scanner Controls"):
            continue
        if stripped.startswith("Portfolio Controls"):
            continue
        if stripped.startswith("Risk Controls"):
            continue
        if stripped.startswith("Trade History Controls"):
            continue
        if stripped.startswith("Trading Controls"):
            continue
        if stripped.startswith("Strategy Controls"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _render_kpi_row(state: Any) -> None:
    """Render the top KPI row with the requested metrics."""
    portfolio = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio, "state", None)
    broker = getattr(state, "broker", None)
    performance = getattr(state, "performance", None)
    risk_service = getattr(state, "risk_service", None) or getattr(state, "risk_dashboard_service", None)

    if risk_service is not None and hasattr(risk_service, "get_snapshot"):
        try:
            snapshot = risk_service.get_snapshot()
            assessment = getattr(snapshot, "assessment", None)
            if assessment is not None:
                risk_value = f"{float(getattr(assessment, 'total_exposure', 0.0) or 0.0):,.2f}"
                buying_power = f"{float(getattr(assessment, 'buying_power', 0.0) or 0.0):,.2f}"
                open_risk = f"{float(getattr(assessment, 'total_exposure', 0.0) or 0.0):,.2f}"
                win_rate = f"{float(getattr(performance, 'win_rate', 0.0) or 0.0):.1f}%" if performance is not None else "N/A"
            else:
                risk_value = _portfolio_metric(portfolio_state, "exposure", getattr(broker, "portfolio", None), "exposure")
                buying_power = _portfolio_metric(portfolio_state, "cash", getattr(broker, "portfolio", None), "cash")
                open_risk = risk_value
                win_rate = _safe_value(performance, "win_rate")
        except Exception:
            risk_value = _portfolio_metric(portfolio_state, "exposure", getattr(broker, "portfolio", None), "exposure")
            buying_power = _portfolio_metric(portfolio_state, "cash", getattr(broker, "portfolio", None), "cash")
            open_risk = risk_value
            win_rate = _safe_value(performance, "win_rate")
    else:
        risk_value = _portfolio_metric(portfolio_state, "exposure", getattr(broker, "portfolio", None), "exposure")
        buying_power = _portfolio_metric(portfolio_state, "cash", getattr(broker, "portfolio", None), "cash")
        open_risk = risk_value
        win_rate = _safe_value(performance, "win_rate")

    portfolio_value = _portfolio_value(portfolio_state, broker)
    today_pnl = _portfolio_metric(portfolio_state, "today_pnl", getattr(broker, "portfolio", None), "realised_pnl")
    open_positions = _position_count(portfolio_state, broker)
    open_trades = _pending_trade_count(state)

    kpi_items = [
        ("Account Value", portfolio_value, "Portfolio value"),
        ("Buying Power", buying_power, "Cash available"),
        ("Today's P&L", today_pnl, "Daily performance"),
        ("Open Risk", open_risk, "Current exposure"),
        ("Win Rate", win_rate, "Execution quality"),
        ("Open Trades", open_trades, "Active positions"),
    ]

    cols = st.columns(6, gap="small")
    for column, (label, value, caption) in zip(cols, kpi_items):
        with column:
            with card():
                st.markdown(f"<div class='tp-kpi-title'>{label}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='tp-kpi-value'>{value}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='tp-kpi-caption'>{caption}</div>", unsafe_allow_html=True)


def _render_panel(title: str, renderer: Any, state: Any) -> None:
    """Render a bordered content panel for each dashboard section."""
    with st.container():
        section(title)
        with card():
            renderer(state)


def _render_scanner_panel(state: Any) -> None:
    """Render a compact scanner panel with only the top five opportunities."""
    scanner_service = getattr(state, "market_scanner_service", None)
    if scanner_service is None:
        empty_state("Scanner service unavailable.")
        return

    if not hasattr(st.session_state, "scanner_results") or st.session_state.get("scanner_results") is None:
        try:
            watchlist = []
            if hasattr(scanner_service, "market_scanner") and hasattr(scanner_service.market_scanner, "get_watchlist"):
                watchlist = scanner_service.market_scanner.get_watchlist() or []
            st.session_state.scanner_results = scanner_service.scan(watchlist)
        except Exception:
            st.session_state.scanner_results = None

    if st.session_state.get("scanner_results") is None:
        empty_state("Scanner unavailable.")
        return

    rows = []
    for row in st.session_state.scanner_results.get("results", [])[:5]:
        rows.append(
            {
                "Symbol": row.get("ticker") or row.get("symbol", "-"),
                "Signal": str(row.get("signal", "HOLD")).upper(),
                "Strategy": "RSI Mean Reversion",
                "Confidence": f"{int(row.get('confidence', 0))}%",
                "Review": "View",
            }
        )

    if not rows:
        empty_state("No opportunities available.")
        return

    st.table(rows)
    if st.button("View Scanner", use_container_width=True):
        st.session_state.current_page = "scanner"
        st.rerun()


def _render_approval_panel(state: Any) -> None:
    """Render a compact approval queue panel with up to five pending approvals."""
    queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)
    if queue is None:
        empty_state("Approval queue unavailable.")
        return

    pending = []
    for item in getattr(queue, "pending_trades", [])[:5]:
        pending.append(
            {
                "Ticker": getattr(item, "symbol", "-"),
                "Direction": str(getattr(item, "signal", "") or "").upper(),
                "Confidence": f"{int(getattr(item, 'confidence', 0))}%",
                "Approve": "✓",
                "Reject": "✕",
            }
        )

    if not pending:
        empty_state("No pending approvals.")
        return

    st.table(pending)


def _render_positions_panel(state: Any) -> None:
    """Render the open positions table in a compact professional format."""
    portfolio = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio, "state", None)
    if portfolio_state is None:
        empty_state("No open positions")
        return

    positions = [position for position in getattr(portfolio_state, "positions", {}).values() if getattr(position, "quantity", 0) > 0]
    if not positions:
        empty_state("No open positions")
        return

    rows = []
    for position in positions:
        rows.append(
            {
                "Ticker": getattr(position, "symbol", "-"),
                "Qty": getattr(position, "quantity", 0),
                "Entry": f"{float(getattr(position, 'average_price', 0.0) or 0.0):,.2f}",
                "Current": f"{float(getattr(position, 'market_price', 0.0) or 0.0):,.2f}",
                "P/L": f"{float(getattr(position, 'market_price', 0.0) or 0.0) - float(getattr(position, 'average_price', 0.0) or 0.0):,.2f}",
                "Risk": f"{float(getattr(position, 'exposure', 0.0) or 0.0):,.2f}",
            }
        )
    st.table(rows)


def _render_allocation_panel(state: Any) -> None:
    """Render the portfolio allocation summary."""
    portfolio = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio, "state", None)
    if portfolio_state is None or not getattr(portfolio_state, "positions", {}):
        empty_state("No portfolio positions")
        return

    positions = [position for position in getattr(portfolio_state, "positions", {}).values() if getattr(position, "quantity", 0) > 0]
    if not positions:
        empty_state("No portfolio positions")
        return

    largest = max(positions, key=lambda item: getattr(item, "exposure", 0.0) or 0.0)
    cash_pct = 0.0
    equity_pct = 100.0
    if getattr(portfolio_state, "exposure", 0.0) > 0:
        equity_pct = min(100.0, (sum(getattr(item, "exposure", 0.0) or 0.0 for item in positions) / max(getattr(portfolio_state, "exposure", 1.0), 1.0)) * 100.0)
        cash_pct = max(0.0, 100.0 - equity_pct)

    st.write(f"Cash %: {cash_pct:.1f}")
    st.write(f"Equity %: {equity_pct:.1f}")
    st.write(f"Largest Holding: {getattr(largest, 'symbol', '-')}")
    st.write("Sector Allocation: N/A")


def _render_activity_panel(state: Any) -> None:
    """Render the recent activity list."""
    journal = getattr(state, "journal", None)
    if journal is None:
        empty_state("No recent activity")
        return

    if hasattr(journal, "entries"):
        entries = list(getattr(journal, "entries"))
        if not entries:
            empty_state("No recent activity")
            return
        for entry in entries[:5]:
            st.write(f"• {entry}")
    else:
        st.write(f"• {journal}")


def _render_ai_summary_panel(state: Any) -> None:
    """Render the reserved AI summary panel."""
    risk_service = getattr(state, "risk_service", None) or getattr(state, "risk_dashboard_service", None)
    if risk_service is None or not hasattr(risk_service, "get_snapshot"):
        empty_state("AI summary not available")
        return

    try:
        snapshot = risk_service.get_snapshot()
    except Exception:
        empty_state("AI summary not available")
        return

    assessment = getattr(snapshot, "assessment", None)
    if assessment is None:
        empty_state("AI summary not available")
        return

    st.write(f"Market Sentiment: {getattr(assessment, 'summary', 'Neutral')}")
    st.write("Top Opportunities: Review scanner results")
    st.write("Risk Alerts: Monitor open exposure")


def _pending_trade_count(state: Any) -> str:
    """Count pending approvals from the existing queue service."""
    queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)
    if queue is None:
        return "0"
    pending = getattr(queue, "pending_trades", None)
    if pending is None:
        return "0"
    return str(len(pending))


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


def _resolve_renderer_key(page_key: str) -> str:
    """Normalize sidebar route keys to the renderer keys used by the dashboard app."""
    aliases = {
        "positions": "orders",
        "orders": "orders",
        "trades": "trade_history",
        "strategies": "strategy",
        "holdings": "portfolio",
        "reports": "performance",
        "settings": "settings",
    }
    return aliases.get(page_key, page_key)


def _dispatch_page(page_key: str, state: Any) -> None:
    """Dispatch the selected shell page to the appropriate workspace renderer."""
    renderer_key = _resolve_renderer_key(page_key)

    from dashboard.workspaces import (
        render_backtesting_workspace,
        render_dashboard_workspace,
        render_live_trading_workspace,
        render_portfolio_workspace,
        render_reports_workspace,
        render_risk_workspace,
        render_scanner_workspace,
        render_settings_workspace,
        render_strategy_workspace,
        render_trade_history_workspace,
    )

    dispatch_map = {
        "dashboard": lambda: render_dashboard_workspace(state),
        "scanner": lambda: render_scanner_workspace(state),
        "portfolio": lambda: render_portfolio_workspace(state),
        "orders": lambda: render_live_trading_workspace(state),
        "trade_history": lambda: render_trade_history_workspace(state),
        "performance": lambda: render_reports_workspace(state),
        "backtesting": lambda: render_backtesting_workspace(state),
        "strategy": lambda: render_strategy_workspace(state),
        "risk": lambda: render_risk_workspace(state),
        "settings": lambda: render_settings_workspace(state),
    }

    handler = dispatch_map.get(renderer_key)
    if handler is None:
        render_dashboard_workspace(state)
        return

    handler()


def main(state: Any) -> None:
    """Render the dashboard page using the requested layout."""
    state = _ensure_dashboard_state(state)
    shell = ApplicationShell()
    page_key = shell.render()
    _dispatch_page(page_key, state)


if __name__ == "__main__":
    main(_ensure_dashboard_state(st.session_state))
