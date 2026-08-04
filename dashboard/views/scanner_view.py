"""Professional scanner workspace for TradePilotAI."""

from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.layout import (
    apply_desktop_layout,
    card,
    empty_state,
    render_information_banner,
    render_kpi_card,
    render_section,
    render_table,
    section,
    spacer,
)


_REVIEW_DATA_UNAVAILABLE = "Not available from current scanner data."


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
            render_kpi_card(
                title=str(label),
                value=str(value),
                footer_label="",
                footer_value="",
                show_footer=False,
            )


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
            render_kpi_card(
                title=str(label),
                value=str(value),
                footer_label="",
                footer_value="",
                show_footer=False,
            )


def _signal_badge(signal: str) -> str:
    signal_text = str(signal or "HOLD").upper()
    palette = {"BUY": "#16A34A", "SELL": "#DC2626", "HOLD": "#F59E0B"}
    color = palette.get(signal_text, palette["HOLD"])
    return f"<span style='color:{color};font-weight:700'>{signal_text}</span>"


def _review_options(results: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("ticker", "")).upper() for row in results if str(row.get("ticker", "")).strip()]


def _ensure_review_selection(results: list[dict[str, Any]]) -> str:
    options = _review_options(results)
    current = str(st.session_state.get("scanner_review_key", "") or "").upper()
    if not options:
        st.session_state.pop("scanner_review_key", None)
        return ""
    if current not in options:
        current = options[0]
        st.session_state["scanner_review_key"] = current
    return current


def _set_review_selection(ticker: str) -> None:
    st.session_state["scanner_review_key"] = str(ticker or "").upper()


def _render_results_table(results: list[dict[str, Any]]) -> None:
    if not results:
        empty_state("No opportunities match the applied filters")
        return

    active_review = _ensure_review_selection(results)

    header_cols = st.columns([0.5, 1.1, 0.8, 1.4, 0.9, 0.8, 0.9, 0.7, 0.8, 1.0, 0.9], gap="small")
    header_labels = ["Rank", "Ticker", "Signal", "Strategy", "Confidence", "Score", "Trend", "RSI", "Risk", "Current Price", "Review"]
    for col, label in zip(header_cols, header_labels):
        with col:
            st.caption(label)

    st.divider()

    for index, row in enumerate(results, start=1):
        ticker = str(row.get("ticker", "-") or "-")
        signal = str(row.get("signal", "HOLD") or "HOLD").upper()
        is_selected = ticker.upper() == active_review

        with st.container(border=True):
            if is_selected:
                st.markdown(
                    "<div style='background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:6px 10px;margin-bottom:8px;font-weight:600;color:#1D4ED8;'>Selected for review</div>",
                    unsafe_allow_html=True,
                )

            row_cols = st.columns([0.5, 1.1, 0.8, 1.4, 0.9, 0.8, 0.9, 0.7, 0.8, 1.0, 0.9], gap="small")
            with row_cols[0]:
                st.write(index)
            with row_cols[1]:
                ticker_label = f"**{ticker}**" if is_selected else ticker
                if st.button(ticker_label, key=f"scanner_ticker_{ticker}", use_container_width=True):
                    _set_review_selection(ticker)
                    st.rerun()
            with row_cols[2]:
                st.markdown(_signal_badge(signal), unsafe_allow_html=True)
            with row_cols[3]:
                st.write(str(row.get("strategy", "RSI Mean Reversion")))
            with row_cols[4]:
                st.write(f"{int(row.get('confidence', 0) or 0)}%")
            with row_cols[5]:
                st.write(f"{float(row.get('score', 0) or 0):.1f}")
            with row_cols[6]:
                st.write(str(row.get("trend", "Unknown")))
            with row_cols[7]:
                st.write(f"{float(row.get('rsi', 0) or 0):.1f}")
            with row_cols[8]:
                st.write(str(row.get("risk", "Medium")))
            with row_cols[9]:
                st.write(f"{float(row.get('price', 0) or 0):,.2f}")
            with row_cols[10]:
                review_label = "Selected" if is_selected else "Open"
                if st.button(review_label, key=f"scanner_review_{ticker}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    _set_review_selection(ticker)
                    st.rerun()


def _raw_value(selected: dict[str, Any], attribute: str) -> Any:
    raw = selected.get("raw")
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw.get(attribute)
    return getattr(raw, attribute, None)


def _display_value(value: Any, default: str = _REVIEW_DATA_UNAVAILABLE) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or default
    if isinstance(value, list):
        if not value:
            return default
        return ", ".join(str(item) for item in value if str(item).strip()) or default
    return str(value)


def _display_price(value: Any) -> str:
    if value is None:
        return _REVIEW_DATA_UNAVAILABLE
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return _display_value(value)


def _display_confidence(value: Any) -> str:
    if value is None:
        return _REVIEW_DATA_UNAVAILABLE
    try:
        return f"{int(value)}%"
    except (TypeError, ValueError):
        return _display_value(value)


def _display_numeric(value: Any, suffix: str = "") -> str:
    if value is None:
        return _REVIEW_DATA_UNAVAILABLE
    try:
        return f"{float(value):.2f}{suffix}"
    except (TypeError, ValueError):
        return _display_value(value)


def _portfolio_snapshot(state: Any, ticker: str) -> dict[str, Any]:
    portfolio_source = getattr(state, "portfolio_service", None) or getattr(state, "portfolio_manager", None)
    portfolio_state = getattr(portfolio_source, "state", None)
    if portfolio_state is None:
        broker = getattr(state, "broker", None)
        portfolio_state = getattr(broker, "portfolio", None)

    positions = getattr(portfolio_state, "positions", {}) or {}
    selected_position = positions.get(ticker) if isinstance(positions, dict) else None

    return {
        "cash": getattr(portfolio_state, "cash", None),
        "exposure": getattr(portfolio_state, "exposure", None),
        "positions": positions,
        "selected_position": selected_position,
    }


def _rsi_interpretation(rsi: Any) -> str:
    try:
        rsi_value = float(rsi)
    except (TypeError, ValueError):
        return _REVIEW_DATA_UNAVAILABLE

    if rsi_value >= 70:
        return f"Overbought at {rsi_value:.1f}."
    if rsi_value <= 30:
        return f"Oversold at {rsi_value:.1f}."
    return f"Neutral-to-balanced at {rsi_value:.1f}."


def _ma_alignment(selected: dict[str, Any]) -> str:
    ema12 = _raw_value(selected, "ema12")
    ema26 = _raw_value(selected, "ema26")
    try:
        fast = float(ema12)
        slow = float(ema26)
    except (TypeError, ValueError):
        return _REVIEW_DATA_UNAVAILABLE

    if fast > slow:
        return f"EMA12 above EMA26 ({fast:.2f} vs {slow:.2f})."
    if fast < slow:
        return f"EMA12 below EMA26 ({fast:.2f} vs {slow:.2f})."
    return f"EMA12 is aligned with EMA26 at {fast:.2f}."


def _momentum_view(selected: dict[str, Any]) -> str:
    signal = _display_value(selected.get("signal"))
    trend = _display_value(selected.get("trend"))
    confidence = _display_confidence(selected.get("confidence"))
    return f"{signal} setup with {trend.lower()} trend and {confidence} confidence."


def _strategy_validation(selected: dict[str, Any]) -> tuple[str, str, str]:
    reasons = _raw_value(selected, "reasons") or []
    rationale = _display_value(reasons, default=_display_value(selected.get("reason")))

    passed_rules: list[str] = []
    failed_rules: list[str] = []

    ema12 = _raw_value(selected, "ema12")
    ema26 = _raw_value(selected, "ema26")
    try:
        if float(ema12) > float(ema26):
            passed_rules.append("Fast moving average is above the slow moving average.")
        elif float(ema12) < float(ema26):
            failed_rules.append("Fast moving average is below the slow moving average.")
    except (TypeError, ValueError):
        failed_rules.append(_REVIEW_DATA_UNAVAILABLE)

    rsi = selected.get("rsi")
    try:
        rsi_value = float(rsi)
        if 30 <= rsi_value <= 70:
            passed_rules.append(f"RSI is inside the balanced range at {rsi_value:.1f}.")
        else:
            failed_rules.append(f"RSI is outside the balanced range at {rsi_value:.1f}.")
    except (TypeError, ValueError):
        failed_rules.append(_REVIEW_DATA_UNAVAILABLE)

    confidence = selected.get("confidence")
    try:
        confidence_value = int(confidence)
        if confidence_value >= 60:
            passed_rules.append(f"Confidence threshold met at {confidence_value}%.")
        else:
            failed_rules.append(f"Confidence remains below the preferred threshold at {confidence_value}%.")
    except (TypeError, ValueError):
        failed_rules.append(_REVIEW_DATA_UNAVAILABLE)

    signal = str(selected.get("signal", "HOLD") or "HOLD").upper()
    if signal in {"BUY", "SELL"}:
        passed_rules.append(f"Strategy produced an actionable {signal} signal.")
    else:
        failed_rules.append("Strategy did not produce an actionable signal.")

    return (
        rationale,
        "; ".join(passed_rules) if passed_rules else _REVIEW_DATA_UNAVAILABLE,
        "; ".join(failed_rules) if failed_rules else _REVIEW_DATA_UNAVAILABLE,
    )


def _reasons_for_trade(selected: dict[str, Any]) -> list[str]:
    reasons = _raw_value(selected, "reasons") or []
    items = [str(reason).strip() for reason in reasons if str(reason).strip()]
    if selected.get("trend"):
        items.append(f"Trend context: {_display_value(selected.get('trend'))}.")
    if selected.get("confidence") is not None:
        items.append(f"Confidence: {_display_confidence(selected.get('confidence'))}.")
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped or [_REVIEW_DATA_UNAVAILABLE]


def _reasons_against_trade(selected: dict[str, Any], portfolio: dict[str, Any]) -> list[str]:
    items: list[str] = []
    signal = str(selected.get("signal", "HOLD") or "HOLD").upper()
    if signal == "HOLD":
        items.append("Strategy remains on HOLD rather than issuing an executable signal.")

    rsi = selected.get("rsi")
    try:
        rsi_value = float(rsi)
        if rsi_value >= 70:
            items.append(f"RSI is overbought at {rsi_value:.1f}.")
        elif rsi_value <= 30:
            items.append(f"RSI is oversold at {rsi_value:.1f}.")
    except (TypeError, ValueError):
        items.append(_REVIEW_DATA_UNAVAILABLE)

    if str(selected.get("risk", "")).lower() == "high":
        items.append("Scanner risk rating is High.")

    if portfolio.get("selected_position") is not None:
        items.append("Portfolio already holds this symbol.")

    return items or [_REVIEW_DATA_UNAVAILABLE]


def _recommendation(selected: dict[str, Any]) -> tuple[str, str]:
    signal = str(selected.get("signal", "HOLD") or "HOLD").upper()
    risk = str(selected.get("risk", "") or "")
    try:
        confidence = int(selected.get("confidence", 0) or 0)
    except (TypeError, ValueError):
        confidence = 0

    try:
        rsi = float(selected.get("rsi", 0) or 0)
    except (TypeError, ValueError):
        rsi = 0.0

    confidence_label = "HIGH" if confidence >= 80 else "MEDIUM" if confidence >= 60 else "LOW"

    if signal == "BUY" and confidence >= 70 and risk.lower() != "high":
        return "EXECUTE", confidence_label
    if signal == "SELL" and confidence >= 70:
        return "REJECT", confidence_label
    if risk.lower() == "high" or rsi >= 70 or (0 < rsi <= 30) or confidence < 55:
        return "REJECT", "LOW"
    return "WATCH", confidence_label


def _render_reason_list(items: list[str], column_name: str) -> None:
    render_table(rows=[{column_name: item} for item in items], columns=[column_name])


def _render_ai_review_tab(selected: dict[str, Any], state: Any) -> None:
    ticker = _display_value(selected.get("ticker"))
    signal = _display_value(selected.get("signal"))
    strategy = _display_value(selected.get("strategy"))
    confidence = _display_confidence(selected.get("confidence"))
    current_price = _display_price(selected.get("price"))
    portfolio = _portfolio_snapshot(state, ticker)

    rationale, passed_rules, failed_rules = _strategy_validation(selected)
    reasons_for = _reasons_for_trade(selected)
    reasons_against = _reasons_against_trade(selected, portfolio)
    recommendation, recommendation_confidence = _recommendation(selected)

    render_section("Trade Summary", lambda: _render_ai_trade_summary(ticker, signal, strategy, confidence, current_price))

    analysis_left, analysis_right = st.columns([0.5, 0.5], gap="small")
    with analysis_left:
        render_section("Technical Analysis", lambda: render_table(
            rows=[
                {"Metric": "Trend", "Value": _display_value(selected.get("trend"))},
                {"Metric": "RSI interpretation", "Value": _rsi_interpretation(selected.get("rsi"))},
                {"Metric": "Moving average alignment", "Value": _ma_alignment(selected)},
                {"Metric": "Momentum", "Value": _momentum_view(selected)},
                {"Metric": "Support", "Value": _display_price(_raw_value(selected, "stop_loss"))},
                {"Metric": "Resistance", "Value": _display_price(_raw_value(selected, "target"))},
            ],
            columns=["Metric", "Value"],
        ))
    with analysis_right:
        render_section("Strategy Validation", lambda: render_table(
            rows=[
                {"Field": "Why this trade was selected", "Value": rationale},
                {"Field": "Rules passed", "Value": passed_rules},
                {"Field": "Rules failed", "Value": failed_rules},
            ],
            columns=["Field", "Value"],
        ))

    risk_left, risk_right = st.columns([0.5, 0.5], gap="small")
    with risk_left:
        render_section("Risk Assessment", lambda: render_table(
            rows=[
                {"Metric": "Position risk", "Value": _display_value(selected.get("risk"))},
                {"Metric": "Portfolio exposure", "Value": _display_price(portfolio.get("exposure"))},
                {"Metric": "Reward/Risk", "Value": _display_numeric(_raw_value(selected, "reward_risk"))},
                {"Metric": "Stop Loss", "Value": _display_price(_raw_value(selected, "stop_loss"))},
                {"Metric": "Target", "Value": _display_price(_raw_value(selected, "target"))},
            ],
            columns=["Metric", "Value"],
        ))
    with risk_right:
        render_section("Portfolio Impact", lambda: render_table(
            rows=[
                {"Metric": "Diversification impact", "Value": _diversification_view(portfolio)},
                {"Metric": "Sector exposure", "Value": _display_value(_raw_value(selected, "sector"))},
                {"Metric": "Cash remaining", "Value": _display_price(portfolio.get("cash"))},
                {"Metric": "Position sizing", "Value": _position_sizing_view(selected, portfolio, state)},
            ],
            columns=["Metric", "Value"],
        ))

    reasons_left, reasons_right = st.columns([0.5, 0.5], gap="small")
    with reasons_left:
        render_section("Reasons FOR the trade", lambda: _render_reason_list(reasons_for, "Reason"))
    with reasons_right:
        render_section("Reasons AGAINST the trade", lambda: _render_reason_list(reasons_against, "Risk"))

    render_information_banner(
        "AI Conclusion",
        _build_ai_conclusion(selected, recommendation, recommendation_confidence, portfolio),
    )

    render_section("Recommendation", lambda: render_table(
        rows=[
            {"Field": "Action", "Value": recommendation},
            {"Field": "Confidence", "Value": recommendation_confidence},
            {"Field": "Basis", "Value": _build_recommendation_basis(selected)},
        ],
        columns=["Field", "Value"],
    ))


def _render_ai_trade_summary(ticker: str, signal: str, strategy: str, confidence: str, current_price: str) -> None:
    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    cards = [
        (col1, "Ticker", ticker),
        (col2, "Signal", signal),
        (col3, "Strategy", strategy),
        (col4, "Confidence", confidence),
        (col5, "Current Price", current_price),
    ]
    for column, title, value in cards:
        with column:
            render_kpi_card(title=title, value=value, footer_label="AI", footer_value="Review")


def _diversification_view(portfolio: dict[str, Any]) -> str:
    selected_position = portfolio.get("selected_position")
    positions = portfolio.get("positions", {}) or {}
    if selected_position is not None:
        return "Diversification would not improve because the portfolio already holds this symbol."
    if isinstance(positions, dict) and positions:
        return "Diversification may improve because this symbol is not currently in the portfolio."
    if isinstance(positions, dict):
        return "Portfolio is empty, so diversification impact is not available from current scanner data."
    return _REVIEW_DATA_UNAVAILABLE


def _position_sizing_view(selected: dict[str, Any], portfolio: dict[str, Any], state: Any) -> str:
    position_size = _raw_value(selected, "position_size")
    if position_size is not None:
        return _display_numeric(position_size)

    selected_position = portfolio.get("selected_position")
    if selected_position is not None:
        return _display_value(getattr(selected_position, "quantity", None))

    risk_engine = getattr(state, "risk_engine", None)
    max_size = getattr(risk_engine, "max_position_size", None)
    if max_size is not None:
        return f"Configured max size: {_display_numeric(max_size)}"
    return _REVIEW_DATA_UNAVAILABLE


def _build_ai_conclusion(selected: dict[str, Any], recommendation: str, recommendation_confidence: str, portfolio: dict[str, Any]) -> str:
    trend = _display_value(selected.get("trend"))
    risk = _display_value(selected.get("risk"))
    confidence = _display_confidence(selected.get("confidence"))
    exposure = _display_price(portfolio.get("exposure"))
    return (
        f"The selected opportunity shows a {trend.lower()} backdrop with {confidence} confidence and a scanner risk rating of {risk}. "
        f"Current portfolio exposure is {exposure}. Based on the existing strategy output and portfolio context, the AI review recommendation is {recommendation} with {recommendation_confidence} confidence."
    )


def _build_recommendation_basis(selected: dict[str, Any]) -> str:
    return "; ".join(
        [
            f"Signal: {_display_value(selected.get('signal'))}",
            f"Trend: {_display_value(selected.get('trend'))}",
            f"RSI: {_display_numeric(selected.get('rsi'))}",
            f"Risk: {_display_value(selected.get('risk'))}",
        ]
    )


def _render_review_panel(results: list[dict[str, Any]], state: Any) -> None:
    if not results:
        return

    review_key = _ensure_review_selection(results)
    selected = next((row for row in results if str(row.get("ticker", "")).upper() == str(review_key).upper()), results[0])

    review_tabs = st.tabs(["Overview", "Indicators", "Risk", "Portfolio", "History", "AI"])
    with review_tabs[0]:
        with card():
            render_kpi_card(
                title="Ticker",
                value=str(selected.get("ticker", "-")),
                footer_label="",
                footer_value="",
                show_footer=False,
            )
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
        _render_ai_review_tab(selected, state)

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
    apply_desktop_layout()

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
    _ensure_review_selection(results)
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
        review_options = _review_options(results)
        _ensure_review_selection(results)
        st.selectbox("Select review target", review_options, key="scanner_review_key")
        _render_review_panel(results, state)
    else:
        if results:
            empty_state("No opportunities match the current filters. The active review target is preserved below.")
            st.selectbox("Select review target", _review_options(results), key="scanner_review_key")
            _render_review_panel(results, state)
        else:
            empty_state("No opportunities available for review")