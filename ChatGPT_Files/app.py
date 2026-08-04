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
    scanner_col, approval_col, summary_col = st.columns([0.4, 0.3, 0.3], gap="small")
    with scanner_col:
        _render_panel("Top Opportunities", lambda s: _render_scanner_panel(s), state)
    with approval_col:
        _render_panel("Portfolio Status", lambda s: _render_approval_panel(s), state)
    with summary_col:
        _render_panel("Market Intelligence", lambda s: _render_ai_summary_panel(s), state)

    spacer(1)
    positions_col, allocation_col = st.columns([0.7, 0.3], gap="small")
    with positions_col:
        _render_panel("Open Positions", lambda s: _render_positions_panel(s), state)
    with allocation_col:
        _render_panel("Portfolio Allocation", lambda s: _render_allocation_panel(s), state)

    spacer(1)
    with st.container():
        _render_panel("Recent Activity", lambda s: _render_activity_panel(s), state)


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
    """Render the top KPI row using the approved five dashboard metrics."""
    scanner_results = _get_scanner_results(state)
    top_result = _top_scanner_result(scanner_results)
    risk_snapshot = _risk_snapshot(state)

    kpi_items = [
        ("Market Regime", _market_regime(scanner_results), _market_regime_caption(scanner_results)),
        ("Recommended Strategy", _recommended_strategy(top_result), _strategy_caption(top_result)),
        ("Best Opportunity", _best_opportunity_value(top_result), _best_opportunity_caption(top_result)),
        ("Risk Status", _risk_status(risk_snapshot), _risk_status_caption(risk_snapshot)),
        ("Decision", _decision_value(state, top_result, risk_snapshot), _decision_caption(state, top_result)),
    ]

    cols = st.columns(5, gap="small")
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
    scanner_results = _get_scanner_results(state)
    if scanner_results is None:
        empty_state("Scanner unavailable.")
        return

    rows = []
    for row in scanner_results.get("results", [])[:5]:
        rows.append(
            {
                "Symbol": row.get("ticker") or row.get("symbol", "-"),
                "Signal": str(row.get("signal", "HOLD")).upper(),
                "Strategy": _recommended_strategy(row),
                "Confidence": f"{int(row.get('confidence', 0))}%",
                "Trend": row.get("trend", "Neutral"),
                "Risk": row.get("risk", "Medium"),
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

    _load_pending_approvals(state)

    pending = []
    for item in getattr(queue, "pending_trades", [])[:5]:
        pending.append(
            {
                "Ticker": getattr(item, "symbol", "-"),
                "Direction": str(getattr(item, "signal", "") or "").upper(),
                "Confidence": f"{int(getattr(item, 'confidence', 0))}%",
                "Entry": _format_currency(getattr(item, "price", 0.0) or 0.0),
                "Target": _format_currency(getattr(item, "target", 0.0) or 0.0),
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
        quantity = float(getattr(position, "quantity", 0) or 0)
        average_price = float(getattr(position, "average_price", 0.0) or 0.0)
        market_price = float(getattr(position, "market_price", 0.0) or 0.0)
        rows.append(
            {
                "Ticker": getattr(position, "symbol", "-"),
                "Qty": int(quantity) if quantity.is_integer() else quantity,
                "Entry": _format_currency(average_price),
                "Current": _format_currency(market_price),
                "P/L": _format_currency((market_price - average_price) * quantity),
                "Risk": _format_currency(float(getattr(position, 'exposure', 0.0) or 0.0)),
            }
        )
    st.table(rows)


def _render_allocation_panel(state: Any) -> None:
    """Render the portfolio allocation summary."""
    portfolio = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio, "state", None)
    positions = []
    cash_value = 0.0
    if portfolio_state is not None:
        positions = [position for position in getattr(portfolio_state, "positions", {}).values() if getattr(position, "quantity", 0) > 0]
        cash_value = float(getattr(portfolio_state, "cash", 0.0) or 0.0)

    holding_value = sum(float(getattr(item, "exposure", 0.0) or 0.0) for item in positions)
    total_value = cash_value + holding_value
    if total_value <= 0:
        total_value = 1.0

    rows = []
    if cash_value > 0 or not positions:
        rows.append({"Holding": "Cash", "Allocation": f"{(cash_value / total_value) * 100.0:.1f}%", "Value": _format_currency(cash_value)})

    for position in sorted(positions, key=lambda item: float(getattr(item, "exposure", 0.0) or 0.0), reverse=True):
        exposure = float(getattr(position, "exposure", 0.0) or 0.0)
        rows.append(
            {
                "Holding": getattr(position, "symbol", "-"),
                "Allocation": f"{(exposure / total_value) * 100.0:.1f}%",
                "Value": _format_currency(exposure),
            }
        )

    st.table(rows)


def _render_activity_panel(state: Any) -> None:
    """Render the recent activity list."""
    for entry in _recent_activity_items(state):
        st.write(f"• {entry}")


def _render_ai_summary_panel(state: Any) -> None:
    """Render the reserved AI summary panel."""
    scanner_results = _get_scanner_results(state)
    top_result = _top_scanner_result(scanner_results)
    snapshot = _risk_snapshot(state)
    assessment = getattr(snapshot, "assessment", None) if snapshot is not None else None

    st.write(f"Market sentiment: {_market_regime(scanner_results)}")
    st.write(f"Best opportunity: {_best_opportunity_summary(top_result)}")
    st.write(f"Portfolio risk summary: {_portfolio_risk_summary(assessment)}")
    st.write(f"Recommended next action: {_recommended_next_action(state, top_result, assessment)}")


def _get_scanner_results(state: Any) -> dict[str, Any] | None:
    """Return cached scanner output, scanning once when the dashboard first loads."""
    cached = st.session_state.get("scanner_results")
    if cached is not None:
        _load_pending_approvals(state, cached)
        return cached

    scanner_service = getattr(state, "market_scanner_service", None)
    if scanner_service is None:
        return None

    try:
        watchlist = []
        if hasattr(scanner_service, "market_scanner") and hasattr(scanner_service.market_scanner, "get_watchlist"):
            watchlist = scanner_service.market_scanner.get_watchlist() or []
        cached = scanner_service.scan(watchlist)
    except Exception:
        cached = None

    st.session_state.scanner_results = cached
    _load_pending_approvals(state, cached)
    return cached


def _load_pending_approvals(state: Any, scanner_results: dict[str, Any] | None = None) -> None:
    queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)
    if queue is None or not hasattr(queue, "load_from_scan_results"):
        return
    queue.load_from_scan_results(scanner_results or st.session_state.get("scanner_results"))


def _top_scanner_result(scanner_results: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(scanner_results, dict):
        return None
    results = scanner_results.get("results", [])
    if not results:
        return None
    return results[0]


def _market_regime(scanner_results: dict[str, Any] | None) -> str:
    if not isinstance(scanner_results, dict):
        return "Neutral"

    results = scanner_results.get("results", [])
    if not results:
        return "Neutral"

    bullish = sum(1 for row in results if str(row.get("trend", "")).lower() == "bullish" or str(row.get("signal", "")).upper() == "BUY")
    bearish = sum(1 for row in results if str(row.get("trend", "")).lower() == "bearish" or str(row.get("signal", "")).upper() == "SELL")
    if bullish > bearish:
        return "Bullish"
    if bearish > bullish:
        return "Bearish"
    return "Neutral"


def _market_regime_caption(scanner_results: dict[str, Any] | None) -> str:
    if not isinstance(scanner_results, dict):
        return "No live scanner signal mix"
    summary = scanner_results.get("summary", {})
    return f"{int(summary.get('buy_signals', 0) or 0)} buy | {int(summary.get('sell_signals', 0) or 0)} sell signals"


def _recommended_strategy(top_result: dict[str, Any] | None) -> str:
    if top_result is None:
        return "RSI Mean Reversion"
    raw_signal = top_result.get("raw")
    strategy_name = getattr(raw_signal, "strategy_name", None) if raw_signal is not None else None
    if strategy_name:
        return str(strategy_name)
    return "RSI Mean Reversion"


def _strategy_caption(top_result: dict[str, Any] | None) -> str:
    if top_result is None:
        return "Default scanner strategy"
    return str(top_result.get("reason") or top_result.get("opportunity") or "Signal generated from live scan")


def _best_opportunity_value(top_result: dict[str, Any] | None) -> str:
    if top_result is None:
        return "No Signal"
    return str(top_result.get("ticker") or top_result.get("symbol") or "No Signal")


def _best_opportunity_caption(top_result: dict[str, Any] | None) -> str:
    if top_result is None:
        return "Scanner waiting for actionable setup"
    return f"{str(top_result.get('signal', 'HOLD')).upper()} | {int(top_result.get('confidence', 0) or 0)}% confidence"


def _risk_snapshot(state: Any) -> Any:
    risk_service = getattr(state, "risk_service", None) or getattr(state, "risk_dashboard_service", None)
    if risk_service is None or not hasattr(risk_service, "get_snapshot"):
        return None
    try:
        return risk_service.get_snapshot()
    except Exception:
        return None


def _risk_status(snapshot: Any) -> str:
    assessment = getattr(snapshot, "assessment", None)
    if assessment is None:
        return "Stable"

    score = float(getattr(assessment, "portfolio_risk_score", 0.0) or 0.0)
    if score >= 60.0:
        return "High"
    if score >= 30.0:
        return "Moderate"
    return "Low"


def _risk_status_caption(snapshot: Any) -> str:
    assessment = getattr(snapshot, "assessment", None)
    if assessment is None:
        return "No open portfolio exposure"
    exposure = float(getattr(assessment, "total_exposure", 0.0) or 0.0)
    buying_power = float(getattr(assessment, "buying_power", 0.0) or 0.0)
    return f"Exposure {_format_currency(exposure)} | Buying power {_format_currency(buying_power)}"


def _decision_value(state: Any, top_result: dict[str, Any] | None, snapshot: Any) -> str:
    pending_count = int(_pending_trade_count(state))
    if pending_count > 0 and top_result is not None:
        signal = str(top_result.get("signal", "HOLD")).upper()
        return "Review" if signal == "HOLD" else signal.title()
    if _risk_status(snapshot) == "High":
        return "Monitor"
    return "Stand By"


def _decision_caption(state: Any, top_result: dict[str, Any] | None) -> str:
    pending_count = int(_pending_trade_count(state))
    if pending_count > 0 and top_result is not None:
        symbol = top_result.get("ticker") or top_result.get("symbol") or "trade"
        return f"{pending_count} pending approval | {symbol} first in queue"
    return "No approvals awaiting action"


def _recent_activity_items(state: Any) -> list[str]:
    journal = getattr(state, "journal", None)
    if journal is not None:
        if hasattr(journal, "entries"):
            entries = [str(entry) for entry in list(getattr(journal, "entries"))[:5] if str(entry).strip()]
            if entries:
                return entries
        elif str(journal).strip():
            return [str(journal)]

    items: list[str] = []
    scanner_results = _get_scanner_results(state)
    scanner_service = getattr(state, "market_scanner_service", None)
    if isinstance(scanner_results, dict):
        summary = scanner_results.get("summary", {})
        signals_found = int(summary.get("signals_found", 0) or 0)
        last_scan_time = summary.get("last_scan_time") or getattr(scanner_service, "last_scan_time", "latest refresh")
        items.append(f"Scanner completed at {last_scan_time} with {signals_found} actionable signals.")
        for event in reversed(scanner_results.get("events", [])):
            name = event.get("name")
            status = event.get("status")
            message = event.get("message")
            if name == "ScanCompleted":
                continue
            detail = f"{name}: {status}"
            if message:
                detail = f"{detail} ({message})"
            items.append(detail)
            if len(items) >= 5:
                break

    if len(items) < 5:
        pending_count = int(_pending_trade_count(state))
        items.append(f"Approval queue currently holds {pending_count} pending trade{'s' if pending_count != 1 else ''}.")

    if len(items) < 5:
        snapshot = _risk_snapshot(state)
        assessment = getattr(snapshot, "assessment", None)
        if assessment is not None:
            items.append(
                f"Risk snapshot refreshed with {_risk_status(snapshot).lower()} portfolio risk and {int(getattr(assessment, 'open_positions', 0) or 0)} open positions."
            )

    return items[:5]


def _best_opportunity_summary(top_result: dict[str, Any] | None) -> str:
    if top_result is None:
        return "No actionable scanner setup detected."
    symbol = top_result.get("ticker") or top_result.get("symbol") or "Unknown"
    signal = str(top_result.get("signal", "HOLD")).upper()
    confidence = int(top_result.get("confidence", 0) or 0)
    trend = top_result.get("trend", "Neutral")
    return f"{symbol} is the leading {signal.lower()} idea at {confidence}% confidence with a {trend.lower()} trend."


def _portfolio_risk_summary(assessment: Any) -> str:
    if assessment is None:
        return "Portfolio risk is stable with no active exposures."
    exposure = _format_currency(float(getattr(assessment, "total_exposure", 0.0) or 0.0))
    open_positions = int(getattr(assessment, "open_positions", 0) or 0)
    buying_power = _format_currency(float(getattr(assessment, "buying_power", 0.0) or 0.0))
    return f"{open_positions} open positions, {exposure} total exposure, and {buying_power} available buying power."


def _recommended_next_action(state: Any, top_result: dict[str, Any] | None, assessment: Any) -> str:
    pending_count = int(_pending_trade_count(state))
    if pending_count > 0 and top_result is not None:
        symbol = top_result.get("ticker") or top_result.get("symbol") or "the lead setup"
        return f"Review the pending approval queue and action {symbol} first."
    if top_result is not None and _risk_status(type("Snapshot", (), {"assessment": assessment})()) != "High":
        symbol = top_result.get("ticker") or top_result.get("symbol") or "the lead setup"
        return f"Monitor {symbol} for confirmation and queue it for approval if conditions hold."
    return "Maintain current positioning and wait for the next confirmed scanner signal."


def _format_currency(value: float) -> str:
    return f"${float(value):,.2f}"


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
