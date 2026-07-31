"""
Professional Scanner View for TradePilotAI
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# Data
# ---------------------------------------------------------


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


def _normalise(results: Any) -> list[dict]:
    """Convert scanner output into a consistent structure."""

    if results is None:
        return []

    if isinstance(results, dict):
        rows = results.get("results", results.get("data", []))
    else:
        rows = list(results)

    normalised = []

    for row in rows:

        row = dict(row)

        signal = str(row.get("signal", "HOLD")).upper()

        score = float(
            row.get("confidence", row.get("score", 0)) or 0
        )

        normalised.append(
            {
                "ticker": row.get("ticker") or row.get("symbol", ""),
                "signal": signal,
                "score": score,
                "rsi": row.get("rsi"),
                "trend": row.get("trend", "Unknown"),
                "risk": row.get("risk", "Medium"),
                "reason": row.get("reason")
                or row.get("opportunity")
                or "No explanation available.",
                "raw": row,
            }
        )

    normalised.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return normalised


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------


def _summary(results: list[dict]) -> None:

    buys = sum(r["signal"] == "BUY" for r in results)
    sells = sum(r["signal"] == "SELL" for r in results)
    holds = sum(r["signal"] == "HOLD" for r in results)

    avg = (
        sum(r["score"] for r in results) / len(results)
        if results
        else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Scanned", len(results))
    c2.metric("BUY", buys)
    c3.metric("SELL", sells)
    c4.metric("HOLD", holds)
    c5.metric("Average Score", f"{avg:.1f}")


def _filters(results: list[dict]) -> list[dict]:

    left, right = st.columns([2, 1])

    with left:
        search = st.text_input(
            "Search ticker",
            placeholder="TSCO",
        )

    with right:
        minimum = st.slider(
            "Minimum Score",
            0,
            100,
            50,
        )

    filtered = [
        r
        for r in results
        if r["score"] >= minimum
    ]

    if search:
        filtered = [
            r
            for r in filtered
            if search.upper()
            in r["ticker"].upper()
        ]

    return filtered


def _table(results: list[dict]) -> None:

    rows = []

    for i, row in enumerate(results, start=1):

        colour = {
            "BUY": "🟢 BUY",
            "SELL": "🔴 SELL",
        }.get(row["signal"], "🟡 HOLD")

        rows.append(
            {
                "Rank": i,
                "Ticker": row["ticker"],
                "Signal": colour,
                "Score": f"{row['score']:.1f}",
                "RSI": row["rsi"],
                "Trend": row["trend"],
                "Risk": row["risk"],
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


def _cards(results: list[dict]) -> None:

    st.markdown("### Highest Ranked Opportunities")

    for row in results[:5]:

        with st.container(border=True):

            left, right = st.columns([5, 1])

            with left:

                st.subheader(
                    f"{row['ticker']} • {row['signal']}"
                )

                st.progress(row["score"] / 100)

                st.write(row["reason"])

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Score",
                    f"{row['score']:.1f}",
                )

                c2.metric(
                    "RSI",
                    row["rsi"],
                )

                c3.metric(
                    "Risk",
                    row["risk"],
                )

            with right:

                st.button(
                    "Review",
                    key=f"review_{row['ticker']}",
                    use_container_width=True,
                )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------


def render_scanner(state: Any) -> None:

    service = getattr(
        state,
        "market_scanner_service",
        None,
    )

    if service is None:
        st.error("Market Scanner Service unavailable.")
        return

    if st.button(
        "🔄 Scan FTSE Opportunities",
        use_container_width=True,
    ):

        try:

            watchlist = _watchlist(service)

            st.session_state.scanner_results = (
                service.scan(watchlist)
            )

            st.session_state.scanner_error = None

        except Exception as exc:

            st.session_state.scanner_results = None
            st.session_state.scanner_error = str(exc)

    if st.session_state.get("scanner_error"):

        st.error(st.session_state.scanner_error)
        return

    if "scanner_results" not in st.session_state:

        st.info(
            "Press **Scan FTSE Opportunities** to begin."
        )

        return

    results = _normalise(
        st.session_state.scanner_results
    )

    _summary(results)

    st.divider()

    filtered = _filters(results)

    _table(filtered)

    st.divider()

    _cards(filtered)