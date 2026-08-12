"""Professional scanner workspace for TradePilotAI."""

from __future__ import annotations

from typing import Any

import streamlit as st
from tradepilotai_os.models.trade import Trade

from dashboard.layout import (
    apply_desktop_layout,
    card,
    empty_state,
    quality_badge,
    render_decision_badge,
    render_information_banner,
    render_kpi_card,
    render_section,
    render_table,
    score_rating,
    section,
    spacer,
)


_REVIEW_DATA_UNAVAILABLE = "Not Yet Calculated"
_EXEC_SUMMARY_NOT_AVAILABLE = "Not Yet Calculated"
_SUGGESTED_TRADE_NOT_AVAILABLE = "Not Yet Calculated"
_PENDING_STRATEGY_OUTPUT = "Pending Strategy Output"
_PENDING_RISK_CALCULATION = "Pending Risk Calculation"
_PENDING_PORTFOLIO_ANALYSIS = "Pending Portfolio Analysis"
_PENDING_MARKET_ANALYSIS = "Pending Market Analysis"
_PENDING_DECISION_OUTPUT = "Not Yet Calculated"


def _apply_scanner_hierarchy_styles() -> None:
    """Apply scanner-only hierarchy styles without changing behavior."""
    st.markdown(
        """
        <style>
        .tp-opportunity-focus .tp-card {
            border: 2px solid #CBD5E1;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
        }
        .tp-scanner-table-header-primary {
            font-weight: 800;
            color: #0F172A;
            font-size: 0.92rem;
            letter-spacing: 0.01em;
        }
        .tp-scanner-table-header-secondary {
            font-weight: 700;
            color: #64748B;
            font-size: 0.80rem;
        }
        .tp-op-ticker {
            font-weight: 800;
            font-size: 1.10rem;
            line-height: 1.0;
        }
        .tp-op-score {
            font-weight: 800;
            font-size: 1.15rem;
            color: #0F172A;
            line-height: 1.0;
        }
        .tp-op-secondary {
            color: #64748B;
            font-size: 0.88rem;
            font-weight: 600;
            line-height: 1.1;
        }
        .tp-op-score-rating {
            color: #64748B;
            font-size: 0.80rem;
            font-weight: 700;
            line-height: 1.1;
            margin-top: 2px;
        }
        .tp-semantic-positive {
            color: #16A34A;
            font-weight: 700;
        }
        .tp-semantic-negative {
            color: #DC2626;
            font-weight: 700;
        }
        .tp-semantic-neutral {
            color: #6B7280;
            font-weight: 700;
        }
        .tp-semantic-warning {
            color: #F59E0B;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _decision_from_signal(signal: str) -> str:
    normalized = str(signal or "HOLD").strip().upper()
    mapping = {
        "BUY": "EXECUTE",
        "HOLD": "WATCH",
        "SELL": "REJECT",
        "INSUFFICIENT_DATA": "INSUFFICIENT_DATA",
    }
    return mapping.get(normalized, "INSUFFICIENT_DATA")


def _semantic_text(value: str, positive: tuple[str, ...], negative: tuple[str, ...], neutral: tuple[str, ...], warning: tuple[str, ...] = ()) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {item.lower() for item in positive}:
        css_class = "tp-semantic-positive"
    elif normalized in {item.lower() for item in negative}:
        css_class = "tp-semantic-negative"
    elif normalized in {item.lower() for item in warning}:
        css_class = "tp-semantic-warning"
    else:
        css_class = "tp-semantic-neutral" if normalized in {item.lower() for item in neutral} else "tp-semantic-neutral"
    return f"<span class='{css_class}'>{str(value or 'Unknown')}</span>"


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
                "strategy": row.get("strategy") if isinstance(row.get("strategy"), str) else "RSI Mean Reversion",
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
                st.button(
                    "Reset Filters",
                    use_container_width=True,
                    key="scanner_reset",
                    on_click=reset_scanner_filters,
                    type="secondary",
                )

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

    header_cols = st.columns([0.5, 1.2, 0.8, 1.4, 0.9, 0.9, 0.9, 0.7, 0.8, 1.0, 0.9], gap="small")
    header_labels = ["Rank", "Ticker", "Decision", "Strategy", "Confidence", "Score", "Trend", "RSI", "Risk", "Current Price", "Review"]
    for col, label in zip(header_cols, header_labels):
        with col:
            css_class = "tp-scanner-table-header-primary" if label in {"Ticker", "Score"} else "tp-scanner-table-header-secondary"
            st.markdown(f"<div class='{css_class}'>{label}</div>", unsafe_allow_html=True)

    st.divider()

    for index, row in enumerate(results, start=1):
        ticker = str(row.get("ticker", "-") or "-")
        signal = str(row.get("signal", "HOLD") or "HOLD").upper()
        is_selected = ticker.upper() == active_review

        with st.container(border=True):
            if is_selected:
                st.markdown(
                    "<div class='tp-scanner-selected-banner'>Selected for review</div>",
                    unsafe_allow_html=True,
                )

            row_cols = st.columns([0.5, 1.2, 0.8, 1.4, 0.9, 0.9, 0.9, 0.7, 0.8, 1.0, 0.9], gap="small")
            with row_cols[0]:
                st.write(index)
            with row_cols[1]:
                st.markdown(f"<div class='tp-op-ticker'>{ticker}</div>", unsafe_allow_html=True)
                ticker_action_label = "Focused" if is_selected else "Select"
                if st.button(ticker_action_label, key=f"scanner_ticker_{ticker}", use_container_width=True, type="secondary"):
                    _set_review_selection(ticker)
                    st.rerun()
            with row_cols[2]:
                render_decision_badge(_decision_from_signal(signal))
            with row_cols[3]:
                st.write(str(row.get("strategy", "RSI Mean Reversion")))
            with row_cols[4]:
                st.markdown(f"<div class='tp-op-secondary'>{int(row.get('confidence', 0) or 0)}%</div>", unsafe_allow_html=True)
            with row_cols[5]:
                score_value = float(row.get("score", 0) or 0)
                st.markdown(
                    f"""
                    <div class='tp-op-score'>{score_value:.1f}</div>
                    <div class='tp-op-score-rating'>{score_rating(score_value)}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with row_cols[6]:
                st.markdown(
                    _semantic_text(
                        str(row.get("trend", "Unknown")),
                        positive=("Bullish",),
                        negative=("Bearish",),
                        neutral=("Neutral", "Unknown"),
                    ),
                    unsafe_allow_html=True,
                )
            with row_cols[7]:
                st.markdown(f"<div class='tp-op-secondary'>{float(row.get('rsi', 0) or 0):.1f}</div>", unsafe_allow_html=True)
            with row_cols[8]:
                st.markdown(
                    _semantic_text(
                        str(row.get("risk", "Medium")),
                        positive=("Low",),
                        negative=("High",),
                        neutral=("Unknown",),
                        warning=("Medium",),
                    ),
                    unsafe_allow_html=True,
                )
            with row_cols[9]:
                st.write(f"{float(row.get('price', 0) or 0):,.2f}")
            with row_cols[10]:
                review_label = "Selected" if is_selected else "Open"
                if st.button(review_label, key=f"scanner_review_{ticker}", use_container_width=True, type="secondary"):
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


def _decision_result_from_selected(selected: dict[str, Any]) -> Any:
    raw = selected.get("raw")

    candidates = [
        selected.get("decision_result"),
        selected.get("decision"),
        raw.get("decision_result") if isinstance(raw, dict) else None,
        raw.get("decision") if isinstance(raw, dict) else None,
    ]

    for candidate in candidates:
        if candidate is not None:
            return candidate
    return None


def _decision_payload(selected: dict[str, Any]) -> dict[str, Any]:
    source = _decision_result_from_selected(selected)
    if isinstance(source, dict):
        return source
    if source is None:
        return {}

    payload: dict[str, Any] = {}
    for key in (
        "decision_score",
        "decision",
        "decision_quality",
        "recommendation_stability",
        "confidence",
        "coverage",
        "reasons_for",
        "reasons_against",
        "decision_explanation",
        "assessment_breakdown",
    ):
        value = getattr(source, key, None)
        if value is not None:
            payload[key] = value
    return payload


def _pending_assessment_label(name: str) -> str:
    if name == "portfolio":
        return _PENDING_PORTFOLIO_ANALYSIS
    if name == "market":
        return _PENDING_MARKET_ANALYSIS
    if name == "risk":
        return _PENDING_RISK_CALCULATION
    return _PENDING_STRATEGY_OUTPUT


def _decision_action(selected: dict[str, Any]) -> str:
    decision = _decision_display(_decision_payload(selected).get("decision"))
    return decision if decision != _EXEC_SUMMARY_NOT_AVAILABLE else _PENDING_DECISION_OUTPUT


def _decision_confidence_label(selected: dict[str, Any]) -> str:
    confidence = _decision_confidence_display(_decision_payload(selected).get("confidence"))
    return confidence if confidence != _EXEC_SUMMARY_NOT_AVAILABLE else _PENDING_DECISION_OUTPUT


def _decision_basis(selected: dict[str, Any]) -> str:
    payload = _decision_payload(selected)
    reasons = payload.get("reasons_for")
    if isinstance(reasons, list):
        text = "; ".join(str(item).strip() for item in reasons if str(item).strip())
        if text:
            return text

    ranking_reason = _selected_value_by_keys(selected, ("ranking_reason", "reason"))
    return _display_value(ranking_reason, default=_PENDING_DECISION_OUTPUT)


def _risk_assessment_from_selected(selected: dict[str, Any], state: Any) -> Any:
    risk_engine = getattr(state, "risk_engine", None)
    if risk_engine is None:
        return None

    direction = str(_selected_value_by_keys(selected, ("signal",)) or "").strip().upper()
    entry_price = _selected_value_by_keys(selected, ("entry_price", "current_price", "price"))
    stop_loss = _selected_value_by_keys(selected, ("stop_loss", "stop_price", "stop"))

    try:
        trade = Trade(
            ticker=str(_selected_value_by_keys(selected, ("ticker", "symbol")) or ""),
            direction=direction,
            entry_time=None,
            entry_price=float(entry_price),
            stop_loss=float(stop_loss),
        )
    except (TypeError, ValueError):
        return None

    try:
        return risk_engine.assess_trade(trade)
    except Exception:
        return None


def _decision_value_from_source(source: Any, key: str) -> Any:
    if source is None:
        return None
    if isinstance(source, dict):
        return source.get(key)
    return getattr(source, key, None)


def _decision_display(value: Any) -> str:
    if value is None:
        return _EXEC_SUMMARY_NOT_AVAILABLE
    text = str(value).strip()
    if not text:
        return _EXEC_SUMMARY_NOT_AVAILABLE
    return text.replace("_", " ")


def _decision_score_display(value: Any) -> str:
    if value is None:
        return _EXEC_SUMMARY_NOT_AVAILABLE
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return _EXEC_SUMMARY_NOT_AVAILABLE


def _decision_confidence_display(value: Any) -> str:
    if value is None:
        return _EXEC_SUMMARY_NOT_AVAILABLE
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return _EXEC_SUMMARY_NOT_AVAILABLE

    if numeric <= 1.0:
        numeric *= 100.0
    return f"{int(round(numeric))}%"


def _render_trade_decision_summary(selected: dict[str, Any]) -> None:
    source = _decision_result_from_selected(selected)

    decision = _decision_display(_decision_value_from_source(source, "decision"))
    decision_score_raw = _decision_value_from_source(source, "decision_score")
    decision_score = _decision_score_display(decision_score_raw)
    decision_quality = quality_badge(decision_score_raw) if decision_score != _EXEC_SUMMARY_NOT_AVAILABLE else _PENDING_DECISION_OUTPUT
    confidence = _decision_confidence_display(_decision_value_from_source(source, "confidence"))
    recommendation_stability = _decision_display(_decision_value_from_source(source, "recommendation_stability"))
    if recommendation_stability == _EXEC_SUMMARY_NOT_AVAILABLE:
        recommendation_stability = _PENDING_DECISION_OUTPUT

    cols = st.columns(5, gap="small")
    with cols[0]:
        st.markdown("<div class='tp-kpi-card'>", unsafe_allow_html=True)
        st.markdown("<div class='tp-kpi-title'>Decision</div>", unsafe_allow_html=True)
        render_decision_badge(decision)
        st.markdown("</div>", unsafe_allow_html=True)

    summary_items = [
        ("Decision Score", decision_score),
        ("Decision Quality", decision_quality),
        ("Confidence", confidence),
        ("Recommendation Stability", recommendation_stability),
    ]
    for col, (title, value) in zip(cols[1:], summary_items):
        with col:
            render_kpi_card(
                title=title,
                value=value,
                footer_label="",
                footer_value="",
                show_footer=False,
            )


def _assessment_component_from_selected(selected: dict[str, Any], name: str) -> Any:
    raw = selected.get("raw")
    decision = _decision_payload(selected)
    assessment_breakdown = decision.get("assessment_breakdown") if isinstance(decision, dict) else None

    candidates = [
        selected.get(name),
        raw.get(name) if isinstance(raw, dict) else None,
        selected.get(f"{name}_component"),
        raw.get(f"{name}_component") if isinstance(raw, dict) else None,
    ]

    for candidate in candidates:
        if isinstance(candidate, dict) and candidate.get("score") is not None:
            return candidate
        if candidate is not None and hasattr(candidate, "score"):
            return candidate
    if isinstance(assessment_breakdown, dict) and assessment_breakdown.get(name) is not None:
        return {"score": assessment_breakdown.get(name)}
    return None


def _assessment_score_display(component: Any) -> str:
    score = _decision_value_from_source(component, "score")
    if score is None:
        return ""
    try:
        return f"{float(score):.1f}"
    except (TypeError, ValueError):
        return ""


def _assessment_score_rating(component: Any) -> str:
    score = _decision_value_from_source(component, "score")
    return score_rating(score)


def _assessment_confidence_footer(component: Any) -> tuple[str, str]:
    confidence = _decision_value_from_source(component, "confidence")
    if confidence is None:
        return "", ""

    try:
        numeric = float(confidence)
    except (TypeError, ValueError):
        return "", ""

    if numeric <= 1.0:
        numeric *= 100.0
    return "Confidence", f"{int(round(numeric))}%"


def _assessment_explanation(component: Any, name: str) -> str:
    explanation = _decision_value_from_source(component, "explanation")
    if isinstance(explanation, dict) and explanation:
        factor, contribution = max(explanation.items(), key=lambda item: float(item[1]))
        return f"{str(factor).replace('_', ' ').title()}: {float(contribution):.2f}"
    return _pending_assessment_label(name)


def _render_assessment_breakdown_summary(selected: dict[str, Any]) -> None:
    assessment_specs = [
        ("Technical", "technical"),
        ("Strategy", "strategy"),
        ("Risk", "risk"),
        ("Portfolio", "portfolio"),
        ("Market", "market"),
    ]

    cols = st.columns(5, gap="small")
    for col, (title, key) in zip(cols, assessment_specs):
        component = _assessment_component_from_selected(selected, key)
        value = _assessment_score_display(component)
        rating = _assessment_score_rating(component) if value else _pending_assessment_label(key)
        footer_label, footer_value = _assessment_confidence_footer(component)
        with col:
            render_kpi_card(
                title=title,
                value=value or _pending_assessment_label(key),
                footer_label=footer_label,
                footer_value=footer_value,
                footer_secondary_label="Explanation",
                footer_secondary_value=_assessment_explanation(component, key),
                show_footer=True,
            )
            if value:
                st.caption(f"Rating: {rating}")


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
    return _decision_action(selected), _decision_confidence_label(selected)


def _priority_score(value: Any) -> float:
    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        pass

    text = str(value).strip().lower()
    if not text:
        return 0.0

    if text.endswith("%"):
        text = text[:-1].strip()
        try:
            return float(text)
        except (TypeError, ValueError):
            return 0.0

    rank = {
        "critical": 5.0,
        "high": 4.0,
        "medium": 3.0,
        "moderate": 3.0,
        "low": 2.0,
        "minor": 1.0,
        "informational": 1.0,
        "info": 1.0,
    }
    return rank.get(text, 0.0)


def _decision_evidence_rows(selected: dict[str, Any], evidence_key: str) -> list[dict[str, str]]:
    source = _decision_result_from_selected(selected)
    reasons = _decision_value_from_source(source, evidence_key)

    if reasons is None:
        return []
    if isinstance(reasons, (tuple, set)):
        reasons = list(reasons)
    if not isinstance(reasons, list):
        reasons = [reasons]

    rows_with_priority: list[tuple[float, int, dict[str, str]]] = []

    for index, reason in enumerate(reasons):
        assessment = "General"
        evidence = ""
        priority = "Unspecified"

        if isinstance(reason, dict):
            assessment = _display_value(
                reason.get("assessment")
                or reason.get("component")
                or reason.get("factor")
                or reason.get("source"),
                default="General",
            )
            evidence = _display_value(
                reason.get("evidence")
                or reason.get("reason")
                or reason.get("text")
                or reason.get("message"),
                default="",
            )
            priority_value = (
                reason.get("priority")
                or reason.get("weight")
                or reason.get("importance")
                or reason.get("rank")
            )
            if priority_value is not None:
                priority = _display_value(priority_value, default="Unspecified")
        else:
            evidence = _display_value(reason, default="")

        if not evidence:
            continue

        rows_with_priority.append(
            (
                _priority_score(priority),
                index,
                {
                    "Assessment": assessment,
                    "Evidence": evidence,
                    "Priority": priority,
                },
            )
        )

    rows_with_priority.sort(key=lambda row: (-row[0], row[1]))
    return [row for _, _, row in rows_with_priority]


def _render_decision_evidence(selected: dict[str, Any]) -> None:
    reasons_for = _decision_evidence_rows(selected, "reasons_for")
    reasons_against = _decision_evidence_rows(selected, "reasons_against")

    columns = ["Assessment", "Evidence", "Priority"]
    default_row = [{"Assessment": "General", "Evidence": _PENDING_DECISION_OUTPUT, "Priority": "-"}]

    left, right = st.columns([0.5, 0.5], gap="small")
    with left:
        st.caption("Reasons FOR")
        render_table(rows=reasons_for or default_row, columns=columns)
    with right:
        st.caption("Reasons AGAINST")
        render_table(rows=reasons_against or default_row, columns=columns)


def _selected_value_by_keys(selected: dict[str, Any], keys: tuple[str, ...]) -> Any:
    raw = selected.get("raw")

    for key in keys:
        if key in selected and selected.get(key) is not None:
            return selected.get(key)

        if isinstance(raw, dict) and raw.get(key) is not None:
            return raw.get(key)

        if raw is not None:
            value = getattr(raw, key, None)
            if value is not None:
                return value

    return None


def _suggested_trade_rows(selected: dict[str, Any]) -> list[dict[str, str]]:
    return _suggested_trade_rows_with_state(selected, None)


def _suggested_trade_rows_with_state(selected: dict[str, Any], state: Any) -> list[dict[str, str]]:
    risk_assessment = _risk_assessment_from_selected(selected, state) if state is not None else None

    def _value(keys: tuple[str, ...]) -> str:
        return _display_value(_selected_value_by_keys(selected, keys), default="")

    current_price = _value(("current_price", "price")) or _PENDING_MARKET_ANALYSIS
    action = _value(("signal",)) or _PENDING_STRATEGY_OUTPUT
    entry_price = _value(("entry_price", "entry")) or _PENDING_STRATEGY_OUTPUT

    stop_loss = _value(("stop_price", "stop_loss", "stop"))
    if not stop_loss and risk_assessment is not None and getattr(risk_assessment, "stop_loss", None) is not None:
        stop_loss = _display_price(getattr(risk_assessment, "stop_loss", None))
    stop_loss = stop_loss or _PENDING_RISK_CALCULATION

    target = _value(("target_price", "target", "take_profit"))
    if not target and risk_assessment is not None and getattr(risk_assessment, "take_profit", None) is not None:
        target = _display_price(getattr(risk_assessment, "take_profit", None))
    target = target or _PENDING_RISK_CALCULATION

    reward_risk = _value(("reward_risk", "reward_risk_ratio", "rr_ratio", "rr")) or _PENDING_RISK_CALCULATION

    position_size = _value(("position_size", "position_size_recommendation"))
    if not position_size and risk_assessment is not None and getattr(risk_assessment, "position_size", None) is not None:
        position_size = _display_numeric(getattr(risk_assessment, "position_size", None))
    position_size = position_size or _PENDING_RISK_CALCULATION

    capital_at_risk = ""
    if risk_assessment is not None and getattr(risk_assessment, "metadata", None):
        risk_amount = risk_assessment.metadata.get("risk_amount")
        if risk_amount is not None:
            capital_at_risk = _display_price(risk_amount)
    capital_at_risk = capital_at_risk or _PENDING_RISK_CALCULATION

    expected_reward = ""
    if risk_assessment is not None and getattr(risk_assessment, "metadata", None):
        risk_amount = risk_assessment.metadata.get("risk_amount")
        if risk_amount is not None:
            expected_reward = _display_price(float(risk_amount) * 2.0)
    expected_reward = expected_reward or _PENDING_RISK_CALCULATION

    return [
        {"Field": "Suggested Action", "Value": action},
        {"Field": "Current Price", "Value": current_price},
        {"Field": "Entry Price", "Value": entry_price},
        {"Field": "Suggested Stop", "Value": stop_loss},
        {"Field": "Suggested Target", "Value": target},
        {"Field": "Reward / Risk", "Value": reward_risk},
        {"Field": "Suggested Position Size", "Value": position_size},
        {"Field": "Capital at Risk", "Value": capital_at_risk},
        {"Field": "Expected Reward", "Value": expected_reward},
    ]


def _render_suggested_trade(selected: dict[str, Any], state: Any) -> None:
    render_table(rows=_suggested_trade_rows_with_state(selected, state), columns=["Field", "Value"])


def _opportunity_assessment_display(selected: dict[str, Any], key: str) -> str:
    raw = selected.get("raw")

    for source in (selected, raw if isinstance(raw, dict) else None):
        if not isinstance(source, dict):
            continue

        score_breakdown = source.get("score_breakdown")
        if isinstance(score_breakdown, dict) and score_breakdown.get(key) is not None:
            value = score_breakdown.get(key)
            try:
                return f"{float(value):.1f}"
            except (TypeError, ValueError):
                return _display_value(value, default=_SUGGESTED_TRADE_NOT_AVAILABLE)

    component = _assessment_component_from_selected(selected, key)
    score = _decision_value_from_source(component, "score")
    if score is not None:
        try:
            return f"{float(score):.1f}"
        except (TypeError, ValueError):
            return _display_value(score, default=_SUGGESTED_TRADE_NOT_AVAILABLE)

    return _SUGGESTED_TRADE_NOT_AVAILABLE


def _decision_reason_lines(selected: dict[str, Any], key: str, maximum: int = 5) -> list[str]:
    source = _decision_result_from_selected(selected)
    reasons = _decision_value_from_source(source, key)
    if reasons is None:
        return []
    if isinstance(reasons, (tuple, set)):
        reasons = list(reasons)
    if not isinstance(reasons, list):
        reasons = [reasons]

    lines: list[str] = []
    for reason in reasons:
        if isinstance(reason, dict):
            text = _display_value(
                reason.get("evidence")
                or reason.get("reason")
                or reason.get("text")
                or reason.get("message"),
                default="",
            )
        else:
            text = _display_value(reason, default="")

        if not text or text == _EXEC_SUMMARY_NOT_AVAILABLE:
            continue

        lines.append(text)
        if len(lines) >= maximum:
            break

    return lines


def _decision_next_step(selected: dict[str, Any]) -> str:
    decision_value = _decision_payload(selected).get("decision")
    decision = str(decision_value or "").strip().upper()

    if decision == "EXECUTE":
        return "Review the proposed entry, stop and target, then submit the trade if market conditions remain unchanged."
    if decision == "WATCH":
        return "Monitor this opportunity until additional confirmation is available."
    if decision == "REJECT":
        return "Do not enter this trade under current conditions."
    if decision == "INSUFFICIENT_DATA":
        return "Collect additional market information before making a decision."
    return _PENDING_DECISION_OUTPUT


def _decision_narrative(selected: dict[str, Any]) -> str:
    payload = _decision_payload(selected)

    decision = _decision_action(selected)
    decision_score = _decision_score_display(payload.get("decision_score"))
    confidence = _decision_confidence_label(selected)
    opportunity_score_raw = _selected_value_by_keys(selected, ("overall_score", "score"))
    try:
        opportunity_score = f"{float(opportunity_score_raw):.1f}"
    except (TypeError, ValueError):
        opportunity_score = _PENDING_DECISION_OUTPUT

    technical = _opportunity_assessment_display(selected, "technical")
    strategy = _opportunity_assessment_display(selected, "strategy")
    risk = _opportunity_assessment_display(selected, "risk")
    portfolio = _opportunity_assessment_display(selected, "portfolio")
    market = _opportunity_assessment_display(selected, "market")

    strengths = _decision_reason_lines(selected, "reasons_for", maximum=5)
    risks = _decision_reason_lines(selected, "reasons_against", maximum=5)

    lines = [
        "SUMMARY",
        f"The Decision Engine recommends {decision} with a Decision Score of {decision_score}.",
        f"Confidence: {confidence}.",
        (
            f"Opportunity Score: {opportunity_score}. "
            f"Technical: {technical}, Strategy: {strategy}, Risk: {risk}, "
            f"Portfolio: {portfolio}, Market: {market}."
        ),
        "",
        "STRENGTHS",
    ]

    if strengths:
        lines.extend(f"- {item}" for item in strengths)
    else:
        lines.append(_PENDING_DECISION_OUTPUT)

    lines.extend(["", "RISKS"])
    if risks:
        lines.extend(f"- {item}" for item in risks)
    else:
        lines.append(_PENDING_DECISION_OUTPUT)

    lines.extend(["", "SUGGESTED NEXT STEP", _decision_next_step(selected)])
    return "\n".join(lines)


def _flatten_explanation_value(value: Any) -> str:
    if value is None:
        return _SUGGESTED_TRADE_NOT_AVAILABLE
    if isinstance(value, str):
        text = value.strip()
        return text or _SUGGESTED_TRADE_NOT_AVAILABLE
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            item_text = _flatten_explanation_value(item)
            if item_text != _SUGGESTED_TRADE_NOT_AVAILABLE:
                parts.append(f"{key}: {item_text}")
        return "; ".join(parts) if parts else _SUGGESTED_TRADE_NOT_AVAILABLE
    if isinstance(value, (list, tuple, set)):
        items = [_flatten_explanation_value(item) for item in value]
        items = [item for item in items if item != _SUGGESTED_TRADE_NOT_AVAILABLE]
        return "; ".join(items) if items else _SUGGESTED_TRADE_NOT_AVAILABLE
    text = str(value).strip()
    return text or _SUGGESTED_TRADE_NOT_AVAILABLE


def _score_component_explanation_rows(selected: dict[str, Any], component_name: str) -> list[dict[str, str]]:
    component = _assessment_component_from_selected(selected, component_name)
    explanation = _decision_value_from_source(component, "explanation")

    if not isinstance(explanation, dict) or not explanation:
        return []

    rows: list[dict[str, str]] = []
    for factor, contribution in explanation.items():
        rows.append(
            {
                "Factor": _flatten_explanation_value(factor),
                "Contribution": _flatten_explanation_value(contribution),
            }
        )

    return rows


def _render_supporting_evidence(selected: dict[str, Any]) -> None:
    rows: list[dict[str, str]] = []
    component_titles = [
        ("Technical", "technical"),
        ("Strategy", "strategy"),
        ("Risk", "risk"),
        ("Portfolio", "portfolio"),
        ("Market", "market"),
    ]

    for title, component_name in component_titles:
        for item in _score_component_explanation_rows(selected, component_name):
            rows.append({"Source": title, "Factor": item["Factor"], "Evidence": item["Contribution"]})

    decision = _decision_payload(selected)
    for reason in decision.get("reasons_for", []) or []:
        rows.append({"Source": "Decision Engine", "Factor": "Strength", "Evidence": _display_value(reason, default="")})
    for reason in decision.get("reasons_against", []) or []:
        rows.append({"Source": "Decision Engine", "Factor": "Risk", "Evidence": _display_value(reason, default="")})

    ranking_reason = _selected_value_by_keys(selected, ("ranking_reason",))
    if ranking_reason is not None:
        rows.append({"Source": "Scanner", "Factor": "Ranking Reason", "Evidence": _display_value(ranking_reason, default="")})

    signal_reasons = _raw_value(selected, "reasons")
    if isinstance(signal_reasons, list):
        for reason in signal_reasons:
            text = _display_value(reason, default="")
            if text:
                rows.append({"Source": "Strategy", "Factor": "Signal Reason", "Evidence": text})

    filtered_rows = [row for row in rows if row["Evidence"]]
    if not filtered_rows:
        empty_state(_PENDING_DECISION_OUTPUT)
        return

    render_table(rows=filtered_rows, columns=["Source", "Factor", "Evidence"])


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
    recommendation, recommendation_confidence = _recommendation(selected)

    render_section("Trade Decision", lambda: _render_trade_decision_summary(selected))
    render_section("Assessment Breakdown", lambda: _render_assessment_breakdown_summary(selected))

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

    render_section("Decision Evidence", lambda: _render_decision_evidence(selected))
    render_section("Suggested Trade", lambda: _render_suggested_trade(selected, state))
    render_section("Supporting Evidence", lambda: _render_supporting_evidence(selected))

    render_information_banner("Decision Narrative", _decision_narrative(selected))

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
        return _PENDING_PORTFOLIO_ANALYSIS
    return _REVIEW_DATA_UNAVAILABLE


def _position_sizing_view(selected: dict[str, Any], portfolio: dict[str, Any], state: Any) -> str:
    position_size = _raw_value(selected, "position_size")
    if position_size is not None:
        return _display_numeric(position_size)

    risk_assessment = _risk_assessment_from_selected(selected, state)
    if risk_assessment is not None and getattr(risk_assessment, "position_size", None) is not None:
        return _display_numeric(getattr(risk_assessment, "position_size", None))

    selected_position = portfolio.get("selected_position")
    if selected_position is not None:
        return _display_value(getattr(selected_position, "quantity", None))

    risk_engine = getattr(state, "risk_engine", None)
    max_size = getattr(risk_engine, "max_position_size", None)
    if max_size is not None:
        return f"Configured max size: {_display_numeric(max_size)}"
    return _PENDING_RISK_CALCULATION


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
    return _decision_basis(selected)


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
    _apply_scanner_hierarchy_styles()

    service = getattr(state, "market_scanner_service", None)
    if service is None:
        st.error("Market Scanner Service unavailable.")
        return

    if st.button("Scan FTSE Opportunities", use_container_width=True, key="scanner_run", type="primary"):
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

    filters, filtered_results = _render_filters(results)

    spacer(1)
    section("Market Summary")
    with card():
        _render_market_summary(filtered_results)

    spacer(1)
    st.markdown("<div class='tp-opportunity-focus'>", unsafe_allow_html=True)
    section("Opportunity Table")
    with card():
        _render_results_table(filtered_results)
    st.markdown("</div>", unsafe_allow_html=True)

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