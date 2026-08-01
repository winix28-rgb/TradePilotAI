import pytest

from dashboard.views.scanner_view import _filter_results, _normalise, _seed_scanner_filter_state, reset_scanner_filters


def test_normalise_converts_scan_payload_to_consistent_rows():
    payload = {
        "results": [
            {
                "ticker": "TSLA",
                "signal": "BUY",
                "confidence": 83,
                "score": 83,
                "rsi": 64.3,
                "trend": "Bullish",
                "risk": "Low",
                "reason": "Momentum breakout",
                "price": 250.0,
            }
        ]
    }

    rows = _normalise(payload)

    assert len(rows) == 1
    assert rows[0]["ticker"] == "TSLA"
    assert rows[0]["signal"] == "BUY"
    assert rows[0]["score"] == 83.0
    assert rows[0]["strategy"] == "RSI Mean Reversion"


def test_filter_results_applies_search_strategy_signal_and_score_filters():
    rows = [
        {
            "ticker": "TSLA",
            "signal": "BUY",
            "score": 85.0,
            "confidence": 85,
            "trend": "Bullish",
            "risk": "Low",
            "strategy": "RSI Mean Reversion",
            "rsi": 67.2,
            "price": 250.0,
            "reason": "Momentum breakout",
        },
        {
            "ticker": "SHEL",
            "signal": "SELL",
            "score": 72.0,
            "confidence": 72,
            "trend": "Bearish",
            "risk": "High",
            "strategy": "EMA Cross",
            "rsi": 41.1,
            "price": 59.0,
            "reason": "Mean reversion",
        },
    ]

    filtered = _filter_results(
        rows,
        {
            "search": "TS",
            "strategy": "RSI Mean Reversion",
            "signal": "BUY",
            "trend": "Bullish",
            "risk": "Low",
            "confidence": 80,
            "minimum_score": 80,
        },
    )

    assert len(filtered) == 1
    assert filtered[0]["ticker"] == "TSLA"


def test_filter_results_supports_sector_filtering():
    rows = [
        {
            "ticker": "TSLA",
            "signal": "BUY",
            "score": 84.0,
            "confidence": 84,
            "trend": "Bullish",
            "risk": "Low",
            "strategy": "RSI Mean Reversion",
            "rsi": 67.2,
            "price": 250.0,
            "reason": "Momentum breakout",
            "sector": "Technology",
        },
        {
            "ticker": "SHEL",
            "signal": "SELL",
            "score": 72.0,
            "confidence": 72,
            "trend": "Bearish",
            "risk": "High",
            "strategy": "EMA Cross",
            "rsi": 41.1,
            "price": 59.0,
            "reason": "Mean reversion",
            "sector": "Energy",
        },
    ]

    filtered = _filter_results(rows, {"sector": "Technology"})

    assert len(filtered) == 1
    assert filtered[0]["ticker"] == "TSLA"


def test_reset_scanner_filters_callback_restores_defaults():
    import streamlit as st

    st.session_state.clear()
    st.session_state.scanner_search = "TSLA"
    st.session_state.scanner_strategy = "EMA Cross"
    st.session_state.scanner_signal = "BUY"
    st.session_state.scanner_trend = "Bullish"
    st.session_state.scanner_risk = "High"
    st.session_state.scanner_sector = "Technology"
    st.session_state.scanner_confidence = 90
    st.session_state.scanner_min_score = 80

    reset_scanner_filters()
    _seed_scanner_filter_state()

    assert st.session_state["_scanner_filters_reset_requested"] is False
    assert st.session_state.scanner_search == ""
    assert st.session_state.scanner_strategy == ""
    assert st.session_state.scanner_signal == ""
    assert st.session_state.scanner_trend == ""
    assert st.session_state.scanner_risk == ""
    assert st.session_state.scanner_sector == ""
    assert st.session_state.scanner_confidence == 0
    assert st.session_state.scanner_min_score == 50
