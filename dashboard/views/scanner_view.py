"""Professional scanner workspace for TradePilotAI."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from dashboard.layout import card, empty_state, section, spacer


def _coerce_value(value: Any, default: Any = None) -> Any:
    """Return a reasonable scalar value for scanner display fields."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        return value.strip() or default
    return value


def _watchlist(service: Any) -> list[str]:
    """Return the configured watchlist."""

    for attr in ("get_watchlist", "watchlist", "symbols"):
        if not hasattr(service, attr):
            continue

        try:
            value = getattr(service, attr)
            symbols = value() if callable(value) else value
            return list(symbols or [])
        except Exception:
            continue

    return []


def _normalise(results: Any) -> list[dict[str, Any]]:
    """Convert scanner output into a consistent structure."""

    if results is None:
        return []

    if isinstance(results, dict):
        rows = results.get("results", results.get("data", []))
    else:
        rows = list(results)

    normalised: list[dict[str, Any]] = []

    for row in rows:
        row = dict(row)
        signal = str(row.get("signal", "HOLD")).upper()
        score = float(row.get("confidence", row.get("score", 0)) or 0)
        normalised.append(
            {
                "ticker": row.get("ticker") or row.get("symbol", ""),
                "signal": signal,
                "score": score,
                "confidence": int(row.get("confidence", int(score))),
                "rsi": row.get("rsi"),
                "trend": row.get("trend", "Unknown"),
                "risk": row.get("risk", "Medium"),
                "strategy": row.get("strategy") or "RSI Mean Reversion",
                "reason": row.get("reason") or row.get("opportunity") or "No explanation available.",
                "price": row.get("price"),
                "raw": row,
            }
        )

    normalised.sort(key=lambda x: x["score"], reverse=True)
    return normalised


def _filter_results(results: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply the scanner filters without changing scanner logic."""

    search = (filters.get("search") or "").strip().upper()
    strategy = (filters.get("strategy") or "").strip()
    signal = (filters.get("signal") or "").strip().upper()
    trend = (filters.get("trend") or "").strip()
    risk = (filters.get("risk") or "").strip()
    sector = (filters.get("sector") or "").strip()
    confidence = int(filters.get("confidence") or 0)
    minimum_score = float(filters.get("minimum_score") or 0)

    filtered = [row for row in results if float(row.get("score", 0) or 0) >= minimum_score]

    if search:
        filtered = [row for row in filtered if search in str(row.get("ticker", "")).upper()]
    if strategy:
        filtered = [row for row in filtered if str(row.get("strategy", "")).lower() == strategy.lower()]
    if signal:
        filtered = [row for row in filtered if str(row.get("signal", "")).upper() == signal]
    if trend:
        filtered = [row for row in filtered if str(row.get("trend", "")).lower() == trend.lower()]
    if risk:
        filtered = [row for row in filtered if str(row.get("risk", "")).lower() == risk.lower()]
    if sector:
        filtered = [row for row in filtered if str(row.get("sector") or "").lower() == sector.lower()]
    if confidence:
        filtered = [row for row in filtered if int(row.get("confidence", 0) or 0) >= confidence]

    return filtered


def _default_scanner_filter_state() -> dict[str, Any]:
    """Return the default state for scanner filters."""
    return {
        "scanner_search": "",
        "scanner_strategy": "",
        "scanner_signal": "",
        "scanner_trend": "",
        "scanner_risk": "",
        "scanner_sector": "",
        "scanner_confidence": 0,
        "scanner_min_score": 50,
    }


def reset_scanner_filters() -> None:
    """Request a reset of scanner filters on the next render cycle."""
    st.session_state["_scanner_filters_reset_requested"] = True


def _seed_scanner_filter_state() -> None:
    """Initialise scanner filter state before the widgets are created."""
    defaults = _default_scanner_filter_state()
    if st.session_state.get("_scanner_filters_reset_requested", False):
        st.session_state["_scanner_filters_reset_requested"] = False
        for key, value in defaults.items():
            st.session_state[key] = value
        return

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_summary(results: list[dict[str, Any]]) -> None:
    buys = sum(r["signal"] == "BUY" for r in results)
    sells = sum(r["signal"] == "SELL" for r in results)
    holds = sum(r["signal"] == "HOLD" for r in results)
    avg_confidence = sum(int(r.get("confidence", 0) or 0) for r in results) / len(results) if results else 0

    cols = st.columns(6, gap="small")
    summary_items = [
        ("Symbols Scanned", len(results)),
        ("BUY Signals", buys),
        ("SELL Signals", sells),
        ("HOLD Signals", holds),
        ("Average Confidence", f"{avg_confidence:.1f}%"),
        ("Last Scan Time", st.session_state.get("scanner_scan_time", "Live")),
    ]
    for col, (label, value) in zip(cols, summary_items):
        with col:
            with card():
                st.markdown(f"<div class='tp-kpi-title'>{label}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='tp-kpi-value'>{value}</div>", unsafe_allow_html=True)


def _render_filters(results: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _seed_scanner_filter_state()

    defaults = _default_scanner_filter_state()
    filter_state = {
        "search": st.session_state.get("scanner_search", defaults["scanner_search"]),
        "strategy": st.session_state.get("scanner_strategy", defaults["scanner_strategy"]),
        "signal": st.session_state.get("scanner_signal", defaults["scanner_signal"]),
        "trend": st.session_state.get("scanner_trend", defaults["scanner_trend"]),
        "risk": st.session_state.get("scanner_risk", defaults["scanner_risk"]),
        "sector": st.session_state.get("scanner_sector", defaults["scanner_sector"]),
        "confidence": st.session_state.get("scanner_confidence", defaults["scanner_confidence"]),
        "minimum_score": st.session_state.get("scanner_min_score", defaults["scanner_min_score"]),
    }

    with st.container():
        section("Scanner Filters")
        with card():
            search_col, strategy_col, signal_col = st.columns([1.6, 1.2, 1.0], gap="small")
            with search_col:
                search = st.text_input(
                    "Search Symbol",
                    placeholder="TSLA",
                    key="scanner_search",
                    value=str(filter_state["search"] or ""),
                )
            with strategy_col:
                strategies = ["", "RSI Mean Reversion", "EMA Cross"]
                strategy_value = filter_state["strategy"]
                strategy_index = strategies.index(strategy_value) if strategy_value in strategies else 0
                strategy = st.selectbox(
                    "Strategy",
                    strategies,
                    key="scanner_strategy",
                    index=strategy_index,
                )
            with signal_col:
                signals = ["", "BUY", "SELL", "HOLD"]
                signal_value = filter_state["signal"]
                signal_index = signals.index(signal_value) if signal_value in signals else 0
                signal = st.selectbox("Signal", signals, key="scanner_signal", index=signal_index)

            trend_col, risk_col, sector_col = st.columns([1.0, 1.0, 1.0], gap="small")
            with trend_col:
                trends = ["", "Bullish", "Bearish", "Neutral"]
                trend_value = filter_state["trend"]
                trend_index = trends.index(trend_value) if trend_value in trends else 0
                trend = st.selectbox("Trend", trends, key="scanner_trend", index=trend_index)
            with risk_col:
                risks = ["", "Low", "Medium", "High"]
                risk_value = filter_state["risk"]
                risk_index = risks.index(risk_value) if risk_value in risks else 0
                risk = st.selectbox("Risk", risks, key="scanner_risk", index=risk_index)
            with sector_col:
                sectors = ["", "Technology", "Energy", "Financials", "Consumer", "Healthcare"]
                sector_value = filter_state["sector"]
                sector_index = sectors.index(sector_value) if sector_value in sectors else 0
                sector = st.selectbox("Sector", sectors, key="scanner_sector", index=sector_index)

            confidence_col, min_col, reset_col = st.columns([1.0, 1.0, 1.0], gap="small")
            with confidence_col:
                confidence = st.slider(
                    "Confidence",
                    0,
                    100,
                    int(filter_state["confidence"] or 0),
                    key="scanner_confidence",
                )
            with min_col:
                minimum_score = st.slider(
                    "Minimum Score",
                    0,
                    100,
                    int(filter_state["minimum_score"] or 50),
                    key="scanner_min_score",
                )
            with reset_col:
                st.button("Reset Filters", use_container_width=True, key="scanner_reset", on_click=reset_scanner_filters)

    filters = {
        "search": search,
        "strategy": strategy,
        "signal": signal,
        "trend": trend,
        "risk": risk,
        "sector": sector,
        "confidence": confidence,
        "minimum_score": minimum_score,
    }
    return filters, _filter_results(results, filters)


def _render_market_summary(results: list[dict[str, Any]]) -> None:
    if not results:
        empty_state("No opportunities available")
        return

    highest_confidence = max(results, key=lambda item: int(item.get("confidence", 0) or 0))
    buy_candidates = [row for row in results if str(row.get("signal", "")).upper() == "BUY"]
    sell_candidates = [row for row in results if str(row.get("signal", "")).upper() == "SELL"]
    highest_risk = max(results, key=lambda item: float(item.get("score", 0) or 0))

    summary_items = [
        ("Best BUY", f"{buy_candidates[0]['ticker'] if buy_candidates else '-'} • {buy_candidates[0]['confidence'] if buy_candidates else 0}%"),
        ("Best SELL", f"{sell_candidates[0]['ticker'] if sell_candidates else '-'} • {sell_candidates[0]['confidence'] if sell_candidates else 0}%"),
        ("Highest Confidence", f"{highest_confidence['ticker']} • {highest_confidence['confidence']}%"),
        ("Highest Risk", f"{highest_risk['ticker']} • {highest_risk['risk']}"),
        ("Average RSI", f"{sum(float(row.get('rsi', 0) or 0) for row in results)/len(results):.1f}" if results else "N/A"),
    ]

    cols = st.columns(5, gap="small")
    for col, (label, value) in zip(cols, summary_items):
        with col:
            with card():
                st.markdown(f"<div class='tp-kpi-title'>{label}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='tp-kpi-value'>{value}</div>", unsafe_allow_html=True)


def _signal_badge(signal: str) -> str:
    signal_text = str(signal or "HOLD").upper()
    palette = {"BUY": "#16A34A", "SELL": "#DC2626", "HOLD": "#F59E0B"}
    color = palette.get(signal_text, palette["HOLD"])
    return f"<span style='color:{color};font-weight:700'>{signal_text}</span>"


def _render_results_table(results: list[dict[str, Any]]) -> None:
    if not results:
        empty_state("No opportunities match the applied filters")
        return

    rows = []
    for index, row in enumerate(results, start=1):
        signal = str(row.get("signal", "HOLD") or "HOLD").upper()
        rows.append(
            {
                "Rank": index,
                "Ticker": row.get("ticker", "-"),
                "Signal": signal,
                "Strategy": row.get("strategy", "RSI Mean Reversion"),
                "Confidence": f"{int(row.get('confidence', 0) or 0)}%",
                "Score": f"{float(row.get('score', 0) or 0):.1f}",
                "Trend": row.get("trend", "Unknown"),
                "RSI": f"{float(row.get('rsi', 0) or 0):.1f}",
                "Risk": row.get("risk", "Medium"),
                "Current Price": f"{float(row.get('price', 0) or 0):,.2f}",
                "Review": "Open",
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        height=320,
        column_config={
            "Signal": st.column_config.TextColumn(width="small"),
            "Review": st.column_config.TextColumn(width="small"),
            "Rank": st.column_config.NumberColumn(width="small"),
        },
    )


def _render_review_panel(results: list[dict[str, Any]], state: Any) -> None:
    if not results:
        return

    review_key = st.session_state.get("scanner_review_key")
    if not review_key:
        review_key = results[0].get("ticker")
    selected = next((row for row in results if str(row.get("ticker", "")).upper() == str(review_key).upper()), results[0])

    review_tabs = st.tabs(["Overview", "Indicators", "Risk", "Portfolio", "History", "AI"])
    with review_tabs[0]:
        with card():
            st.markdown(f"<div class='tp-kpi-title'>Ticker</div><div class='tp-kpi-value'>{selected.get('ticker', '-')}</div>", unsafe_allow_html=True)
            st.write(f"Direction: {selected.get('signal', 'HOLD')}")
            st.write(f"Strategy: {selected.get('strategy', 'RSI Mean Reversion')}")
            st.write(f"Entry: {selected.get('price', 'N/A')}")
            st.write(f"Current: {selected.get('price', 'N/A')}")
            st.write(f"Stop: {_coerce_value(selected.get('stop'), 'N/A')}")
            st.write(f"Target: {_coerce_value(selected.get('target'), 'N/A')}")
            st.write(f"Confidence: {selected.get('confidence', 0)}%")
            st.write(f"Trade Reasons: {_coerce_value(selected.get('reason'), 'No explanation available.')}")
    with review_tabs[1]:
        with card():
            st.write(f"EMA12: {_coerce_value(selected.get('raw', {}).get('ema12'), 'N/A')}")
            st.write(f"EMA26: {_coerce_value(selected.get('raw', {}).get('ema26'), 'N/A')}")
            st.write(f"RSI: {_coerce_value(selected.get('rsi'), 'N/A')}")
            st.write(f"MACD: {_coerce_value(selected.get('raw', {}).get('macd'), 'N/A')}")
            st.write(f"Trend: {_coerce_value(selected.get('trend'), 'Unknown')}")
    with review_tabs[2]:
        with card():
            st.write(f"Suggested Position Size: {_coerce_value(selected.get('raw', {}).get('position_size'), 1)}")
            st.write(f"Risk %: {_coerce_value(selected.get('raw', {}).get('risk_pct'), 1.0)}")
            st.write(f"Reward / Risk: {_coerce_value(selected.get('raw', {}).get('reward_risk'), 2.0)}")
            st.write(f"Portfolio Exposure: {_coerce_value(selected.get('raw', {}).get('portfolio_exposure'), 'Pending review')}")
    with review_tabs[3]:
        with card():
            st.write(f"Current Exposure: {_coerce_value(selected.get('raw', {}).get('current_exposure'), 'Pending review')}")
            st.write(f"Available Cash: {_coerce_value(selected.get('raw', {}).get('cash_available'), 'Pending review')}")
            st.write(f"Buying Power: {_coerce_value(selected.get('raw', {}).get('buying_power'), 'Pending review')}")
            st.write(f"Open Positions: {_coerce_value(selected.get('raw', {}).get('open_positions'), 'Pending review')}")
    with review_tabs[4]:
        with card():
            st.write(f"Previous Signals: {_coerce_value(selected.get('raw', {}).get('previous_signals'), 'Review scanner history')}")
            st.write(f"Previous Trades: {_coerce_value(selected.get('raw', {}).get('previous_trades'), 'No prior trades')}")
            st.write(f"Performance: {_coerce_value(selected.get('raw', {}).get('performance'), 'Monitor in portfolio workspace')}")
    with review_tabs[5]:
        with card():
            empty_state("AI analysis not yet enabled")

    action_col1, action_col2, action_col3, action_col4 = st.columns([1, 1, 1, 1], gap="small")
    with action_col1:
        st.button("Approve", use_container_width=True, key=f"approve_{selected.get('ticker', 'scanner')}")
    with action_col2:
        st.button("Modify", use_container_width=True, key=f"modify_{selected.get('ticker', 'scanner')}")
    with action_col3:
        st.button("Reject", use_container_width=True, key=f"reject_{selected.get('ticker', 'scanner')}")
    with action_col4:
        st.button("Close Review", use_container_width=True, key=f"close_review_{selected.get('ticker', 'scanner')}")


def render_scanner(state: Any) -> None:
    """Render the professional scanner decision workspace."""
    service = getattr(state, "market_scanner_service", None)
    if service is None:
        st.error("Market Scanner Service unavailable.")
        return

    if st.button("Scan FTSE Opportunities", use_container_width=True, key="scanner_run"):
        try:
            watchlist = _watchlist(service)
            st.session_state.scanner_results = service.scan(watchlist)
            st.session_state.scanner_error = None
            st.session_state.scanner_scan_time = st.session_state.get("scanner_scan_time", "Live")
            queue = getattr(state, "approval_queue", None)
            if queue is not None and hasattr(queue, "load_from_scan_results"):
                queue.load_from_scan_results(st.session_state.scanner_results)
        except Exception as exc:
            st.session_state.scanner_results = None
            st.session_state.scanner_error = str(exc)

    if st.session_state.get("scanner_error"):
        st.error(st.session_state.scanner_error)
        return

    if "scanner_results" not in st.session_state:
        st.info("Run a scan to populate the trading workspace.")
        return

    results = _normalise(st.session_state.scanner_results)
    _render_summary(results)
    spacer(1)

    filter_col, summary_col = st.columns([0.72, 0.28], gap="small")
    with filter_col:
        filters, filtered_results = _render_filters(results)
    with summary_col:
        section("Market Summary")
        with card():
            _render_market_summary(filtered_results)

    spacer(1)
    section("Opportunity Table")
    with card():
        _render_results_table(filtered_results)

    spacer(1)
    section("Review Workspace")
    if filtered_results:
        review_options = [row.get("ticker") for row in filtered_results]
        selected_review = st.selectbox("Select review target", review_options, key="scanner_review_key")
        _render_review_panel(filtered_results, state)
    else:
        empty_state("No opportunities available for review")