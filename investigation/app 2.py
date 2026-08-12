"""Professional trading-workstation dashboard entry point."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from dashboard.layout import (
    card,
    empty_state,
    render_desktop_layout,
    render_information_banner,
    render_kpi_card,
    render_panel_header,
    render_section,
    render_table,
    section,
    spacer,
)
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

    st.markdown(
        """
        <style>
        [data-testid="stMainBlockContainer"] {
            max-width: 1600px;
            min-width: 1400px;
            padding-left: 24px;
            padding-right: 24px;
            padding-top: 20px;
            padding-bottom: 20px;
            margin-left: auto;
            margin-right: auto;
        }
        @media (max-width: 1450px) {
            [data-testid="stMainBlockContainer"] {
                min-width: auto;
                width: 100%;
            }
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 20px !important;
            align-items: stretch !important;
        }
        div[data-testid="stColumn"] > div {
            height: 100%;
        }
        .tp-panel-title {
            margin-bottom: 20px;
        }
        div[data-testid="stTable"] {
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _render_header(state)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    _render_kpi_row(state)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    scanner_col, approval_col, summary_col = st.columns([1, 1, 1], gap="small")
    with scanner_col:
        with st.container(height=520):
            _render_panel("Top Opportunities", lambda s: _render_scanner_panel(s), state)
    with approval_col:
        with st.container(height=520):
            _render_panel("Portfolio Status", lambda s: _render_approval_panel(s), state)
    with summary_col:
        with st.container(height=520):
            _render_panel("Market Intelligence", lambda s: _render_ai_summary_panel(s), state)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    positions_col, allocation_col, insight_col = st.columns([1, 1, 1], gap="small")
    with positions_col:
        with st.container(height=520):
            _render_panel("Open Positions", lambda s: _render_positions_panel(s), state)
    with allocation_col:
        with st.container(height=520):
            _render_panel("Portfolio Allocation", lambda s: _render_allocation_panel(s), state)
    with insight_col:
        with st.container(height=520):
            _render_panel("AI Trading Insight", lambda s: _render_activity_panel(s), state)


def _render_header(state: Any) -> None:
    """Render the trading-terminal header with the requested status summary."""
    header_col, status_col = st.columns([0.72, 0.28], gap="small")
    last_update = getattr(getattr(state, "market_scanner_service", None), "last_scan_time", None) or datetime.now().strftime("%d %b %Y %I:%M %p")

    with header_col:
        st.markdown("<h1 class='tp-page-title'>TODAY'S TRADING BRIEF</h1>", unsafe_allow_html=True)
        st.markdown(
            "<div class='tp-page-caption'>AI-generated market assessment based on current market conditions, portfolio analysis and trading engine output.</div>",
            unsafe_allow_html=True,
        )

    with status_col:
        with card():
            st.caption("Connection")
            st.write("**LIVE**")
            st.caption("Market")
            st.write("**OPEN**")
            st.caption("Last Update")
            st.write(f"**{last_update}**")


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
    """Render five KPI cards using existing application service outputs."""
    scanner_results = _get_scanner_results(state)
    top_result = _top_scanner_result(scanner_results) or {}
    snapshot = _risk_snapshot(state)
    assessment = getattr(snapshot, "assessment", None)
    approval_queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)

    market_regime = str(top_result.get("trend") or "Neutral")
    top_confidence = int(top_result.get("confidence", 0) or 0)

    strategy_name = "N/A"
    raw_signal = top_result.get("raw") if isinstance(top_result, dict) else None
    if raw_signal is not None:
        strategy_name = str(getattr(raw_signal, "strategy_name", "") or "N/A")
    if strategy_name == "N/A":
        strategy_name = str(top_result.get("reason") or top_result.get("opportunity") or "N/A")

    best_symbol = str(top_result.get("ticker") or top_result.get("symbol") or "No Signal")
    best_score = int(top_result.get("score", top_confidence) or 0)
    portfolio_fit = int(top_result.get("confidence", top_confidence) or 0)

    risk_value = "N/A"
    risk_caption = _format_currency(0.0)
    if assessment is not None:
        risk_value = f"{float(getattr(assessment, 'portfolio_risk_score', 0.0) or 0.0):.2f}%"
        risk_caption = _format_currency(float(getattr(assessment, "total_exposure", 0.0) or 0.0))

    decision_value = str(top_result.get("signal") or "HOLD").upper()
    pending = getattr(approval_queue, "pending_trades", []) if approval_queue is not None else []
    decision_caption = f"Pending approvals | {len(pending or [])}"

    col1,col2,col3,col4,col5 = st.columns(5,gap="medium")

    with col1:
        render_kpi_card(
            title="Market Regime",
            value=market_regime,
            footer_label="Confidence",
            footer_value=f"{top_confidence}%",
        )

    with col2:
        render_kpi_card(
            title="Recommended Strategy",
            value=strategy_name,
            footer_label="Confidence",
            footer_value=f"{top_confidence}%",
        )

    with col3:
        render_kpi_card(
            title="Best Opportunity",
            value=best_symbol,
            footer_label="Opportunity Score",
            footer_value=str(best_score),
            footer_secondary_label="Portfolio Fit",
            footer_secondary_value=str(portfolio_fit),
        )

    with col4:
        render_kpi_card(
            title="Risk Status",
            value=risk_value,
            footer_label="Portfolio Risk",
            footer_value=risk_caption,
        )

    with col5:
        render_kpi_card(
            title="Decision",
            value=decision_value,
            footer_label="Recommendation",
            footer_value=decision_caption,
        )


def _render_panel(title: str, renderer: Any, state: Any) -> None:
    """Render a bordered content panel for each dashboard section."""
    with st.container():
        section(title)
        with card():
            renderer(state)


def _render_scanner_panel(state: Any) -> None:
    """Render the Market Review left panel content."""
    scanner_results = _get_scanner_results(state)
    results = scanner_results.get("results", []) if isinstance(scanner_results, dict) else []

    rows = []
    for item in list(results)[:3]:
        rows.append(
            {
                "Ticker": str(item.get("ticker") or item.get("symbol") or "-"),
                "Signal": str(item.get("signal") or "HOLD").upper(),
                "Score": int(item.get("score", item.get("confidence", 0)) or 0),
                "Portfolio Fit": int(item.get("confidence", 0) or 0),
                "Action": str(item.get("signal") or "WATCH").upper(),
            }
        )
    render_table(
        rows,
        columns=["Ticker", "Signal", "Score", "Portfolio Fit", "Action"],
        numeric_columns=["Score", "Portfolio Fit"],
    )


def _render_approval_panel(state: Any) -> None:
    """Render the Market Review centre panel content."""
    snapshot = _risk_snapshot(state)
    assessment = getattr(snapshot, "assessment", None)
    risk_engine = getattr(state, "risk_engine", None)
    approval_queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)

    risk_value = "N/A"
    cash_available = _format_currency(0.0)
    max_position_size = _format_currency(float(getattr(risk_engine, "max_position_size", 0.0) or 0.0))
    capital_allocation = "0.00%"
    readiness = "Pending approvals: 0"

    if assessment is not None:
        risk_value = f"{float(getattr(assessment, 'portfolio_risk_score', 0.0) or 0.0):.2f}%"
        cash_available = _format_currency(float(getattr(assessment, "available_cash", 0.0) or 0.0))
        capital_allocation = f"{float(getattr(assessment, 'portfolio_risk_score', 0.0) or 0.0):.2f}%"

    pending = getattr(approval_queue, "pending_trades", []) if approval_queue is not None else []
    readiness = f"Pending approvals: {len(pending or [])}"

    st.write("Portfolio Risk")
    st.write(f"**{risk_value}**")

    st.write("Cash Available")
    st.write(f"**{cash_available}**")

    st.write("Maximum Position Size")
    st.write(f"**{max_position_size}**")

    st.write("Capital Allocation")
    st.write(f"**{capital_allocation}**")

    st.write("Portfolio Ready")
    st.write(f"**{readiness}**")


def _render_positions_panel(state: Any) -> None:
    """Render the Open Positions panel content."""
    portfolio = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio, "state", None)
    snapshot = _risk_snapshot(state)
    assessment = getattr(snapshot, "assessment", None)

    deployed_value = _format_currency(float(getattr(assessment, "total_exposure", 0.0) or 0.0)) if assessment is not None else _format_currency(0.0)
    exposure_value = f"{float(getattr(assessment, 'portfolio_risk_score', 0.0) or 0.0):.2f}%" if assessment is not None else "0.00%"
    average_risk_value = f"{float(getattr(assessment, 'value_at_risk', 0.0) or 0.0):.2f}" if assessment is not None else "0.00"
    scanner_service = getattr(state, "market_scanner_service", None)
    next_review = str(getattr(scanner_service, "last_scan_time", "") or "Awaiting scanner update")

    if portfolio_state is None:
        st.write("Status")
        st.write("**No Open Positions**")

        st.write("Capital Deployed")
        st.write(f"**{deployed_value}**")

        st.write("Portfolio Exposure")
        st.write(f"**{exposure_value}**")

        st.write("Average Risk")
        st.write(f"**{average_risk_value}%**")

        st.write("Next Review")
        st.write(f"**{next_review}**")
        return

    positions = [position for position in getattr(portfolio_state, "positions", {}).values() if getattr(position, "quantity", 0) > 0]
    if not positions:
        st.write("Status")
        st.write("**No Open Positions**")

        st.write("Capital Deployed")
        st.write(f"**{deployed_value}**")

        st.write("Portfolio Exposure")
        st.write(f"**{exposure_value}**")

        st.write("Average Risk")
        st.write(f"**{average_risk_value}%**")

        st.write("Next Review")
        st.write(f"**{next_review}**")
        return

    risk_rows = {}
    if snapshot is not None:
        risk_rows = {getattr(item, "symbol", ""): item for item in getattr(snapshot, "positions", [])}

    rows = []
    for position in positions:
        symbol = getattr(position, "symbol", "-")
        risk_row = risk_rows.get(symbol)
        pnl_value = _format_currency(float(getattr(risk_row, "unrealised_pnl", 0.0) or 0.0))
        risk_value = f"{float(getattr(risk_row, 'risk_percent', 0.0) or 0.0):.2f}%"
        average_price = float(getattr(position, "average_price", 0.0) or 0.0)
        market_price = float(getattr(position, "market_price", 0.0) or 0.0)
        rows.append(
            {
                "Ticker": symbol,
                "Direction": str(getattr(position, "direction", "LONG") or "LONG").upper(),
                "Entry": _format_currency(average_price),
                "Current": _format_currency(market_price),
                "P/L": pnl_value,
                "Risk": risk_value,
            }
        )
    render_table(
        rows,
        columns=["Ticker", "Direction", "Entry", "Current", "P/L", "Risk"],
    )


def _render_allocation_panel(state: Any) -> None:
    """Render the Portfolio Allocation panel content."""
    snapshot = _risk_snapshot(state)
    positions = getattr(snapshot, "positions", []) if snapshot is not None else []

    rows = []
    for item in list(positions)[:5]:
        rows.append(
            {
                "Asset": str(getattr(item, "symbol", "-")),
                "Allocation %": f"{float(getattr(item, 'exposure_percent', 0.0) or 0.0):.2f}%",
            }
        )

    render_table(
        rows,
        columns=["Asset", "Allocation %"],
    )


def _render_activity_panel(state: Any) -> None:
    """Render the bottom dashboard insight content."""
    st.write("AI Trading Insight")

    st.write("Primary Insight")
    st.write("Current market conditions favour trend-following strategies.")

    st.write("Risk Assessment")
    st.write("Portfolio risk remains LOW.")

    st.write("Market Condition")
    st.write("FTSE 100 breadth remains positive.")

    st.write("Recommended Action")
    st.write("Monitor SHEL for confirmation before execution.")


def _render_ai_summary_panel(state: Any) -> None:
    """Render the Market Intelligence panel content."""
    scanner_results = _get_scanner_results(state)
    top_result = _top_scanner_result(scanner_results) or {}
    snapshot = _risk_snapshot(state)
    assessment = getattr(snapshot, "assessment", None)
    approval_queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)

    regime_value = str(top_result.get("trend") or "Neutral")
    trend_value = str(top_result.get("reason") or top_result.get("opportunity") or "No active trend signal")
    opportunity_value = str(top_result.get("ticker") or top_result.get("symbol") or "No Signal")
    portfolio_risk_value = f"{float(getattr(assessment, 'portfolio_risk_score', 0.0) or 0.0):.2f}%" if assessment is not None else "N/A"

    recommended_action = str(top_result.get("signal") or "HOLD").upper()
    if approval_queue is not None and getattr(approval_queue, "last_action", None):
        recommended_action = str((approval_queue.last_action or {}).get("reason") or recommended_action)

    st.write("Market Regime")
    st.write(f"**{regime_value}**")

    st.write("Market Trend")
    st.write(f"**{trend_value}**")

    st.write("Best Opportunity")
    st.write(f"**{opportunity_value}**")

    st.write("Portfolio Risk")
    st.write(f"**{portfolio_risk_value}**")

    st.write("Recommended Action")
    st.write(f"**{recommended_action}**")


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
    return "Trend Following"


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
    return "Portfolio Risk | $0.00"


def _decision_value(state: Any, top_result: dict[str, Any] | None, snapshot: Any) -> str:
    pending_count = int(_pending_trade_count(state))
    if pending_count > 0 and top_result is not None:
        signal = str(top_result.get("signal", "HOLD")).upper()
        return "Review" if signal == "HOLD" else signal.title()
    if _risk_status(snapshot) == "High":
        return "Monitor"
    return "Stand By"


def _decision_caption(state: Any, top_result: dict[str, Any] | None) -> str:
    return "Recommendation | Moderate"


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
    return "\n".join(
        [
            "Strong trend alignment",
            "Positive momentum",
            "Low portfolio risk",
            "Excellent strategy fit",
            "Diversification remains healthy",
            "Sector exposure is balanced",
            "Risk impact is manageable",
            "Cash availability supports the trade",
        ]
    )


def _format_currency(value: float) -> str:
    return f"${float(value):,.2f}"


def _pending_trade_count(state: Any) -> str:
    return "0"


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

    render_desktop_layout()
    render_panel_header("Settings", status="LIVE")

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5, gap="small")
    with kpi1:
        render_kpi_card(
            title="Trading Engine",
            value=_service_name(controller),
            footer_label="Setting",
            footer_value="Runtime",
        )
    with kpi2:
        render_kpi_card(
            title="Broker Connection",
            value=_connection_status(state),
            footer_label="Setting",
            footer_value="Runtime",
        )
    with kpi3:
        render_kpi_card(
            title="Trading Mode",
            value=_mode_value(state),
            footer_label="Setting",
            footer_value="Runtime",
        )
    with kpi4:
        render_kpi_card(
            title="Broker",
            value=_service_name(broker) or _service_name(live_service),
            footer_label="Setting",
            footer_value="Runtime",
        )
    with kpi5:
        render_kpi_card(
            title="Diagnostics",
            value=_diagnostic_value(performance),
            footer_label="Setting",
            footer_value="Runtime",
        )

    main_left, main_right = st.columns([0.6, 0.4], gap="small")
    with main_left:
        render_section(
            "Runtime Status",
            lambda: render_table(
                rows=[
                    {"Setting": label, "Value": value}
                    for label, value in status_items
                ],
                columns=["Setting", "Value"],
            ),
        )
    with main_right:
        render_section(
            "Connection Details",
            lambda: render_table(
                rows=[
                    {"Detail": "Broker Connection", "Value": _connection_status(state)},
                    {"Detail": "Trading Mode", "Value": _mode_value(state)},
                    {"Detail": "Broker", "Value": _service_name(broker) or _service_name(live_service)},
                    {"Detail": "Diagnostics", "Value": _diagnostic_value(performance)},
                ],
                columns=["Detail", "Value"],
            ),
        )

    bottom_left, bottom_right = st.columns([0.5, 0.5], gap="small")
    with bottom_left:
        render_section(
            "Engine Snapshot",
            lambda: render_table(
                rows=[
                    {"Field": "Trading Engine", "Value": _service_name(controller)},
                    {"Field": "Broker", "Value": _service_name(broker) or _service_name(live_service)},
                ],
                columns=["Field", "Value"],
            ),
        )
    with bottom_right:
        render_section(
            "Diagnostics Snapshot",
            lambda: render_table(
                rows=[
                    {"Field": "Broker Connection", "Value": _connection_status(state)},
                    {"Field": "Trading Mode", "Value": _mode_value(state)},
                    {"Field": "Diagnostics", "Value": _diagnostic_value(performance)},
                ],
                columns=["Field", "Value"],
            ),
        )

    render_information_banner(
        "System Notes",
        "\n".join(
            [
                f"Trading Engine: {_service_name(controller)}",
                f"Broker Connection: {_connection_status(state)}",
                f"Trading Mode: {_mode_value(state)}",
                f"Broker: {_service_name(broker) or _service_name(live_service)}",
                f"Diagnostics: {_diagnostic_value(performance)}",
            ]
        ),
    )


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
