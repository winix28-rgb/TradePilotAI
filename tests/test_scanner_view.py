import pytest

from dashboard.views.scanner_view import (
    _assessment_component_from_selected,
    _decision_narrative,
    _filter_results,
    _normalise,
    _recommendation,
    _seed_scanner_filter_state,
    _suggested_trade_rows_with_state,
    reset_scanner_filters,
)
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.risk.risk_engine import RiskEngine
from tradepilotai_os.scanner.module.service import ScannerService


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


def test_normalise_preserves_decision_review_payloads():
    signal = TradeSignal(
        symbol="TSLA",
        signal="BUY",
        confidence=84,
        price=250.5,
        rsi=61.2,
        ema12=255.0,
        ema26=248.0,
        stop_loss=242.0,
        target=268.0,
        reasons=["RSI recovery", "EMA bullish crossover"],
    )
    row = ScannerService()._to_result_row(symbol="TSLA", signal=signal, volatility=0.02)

    normalised = _normalise({"results": [row]})

    assert normalised[0]["raw"]["decision_result"]["decision"] == row["decision_result"]["decision"]
    assert _assessment_component_from_selected(normalised[0], "technical")["score"] == row["technical_component"]["score"]
    assert _assessment_component_from_selected(normalised[0], "risk")["score"] == row["risk_component"]["score"]


def test_recommendation_and_narrative_share_same_decision_object():
    signal = TradeSignal(
        symbol="TSLA",
        signal="BUY",
        confidence=84,
        price=250.5,
        rsi=61.2,
        ema12=255.0,
        ema26=248.0,
        stop_loss=242.0,
        target=268.0,
        reasons=["RSI recovery", "EMA bullish crossover"],
    )
    selected = _normalise({"results": [ScannerService()._to_result_row(symbol="TSLA", signal=signal, volatility=0.02)]})[0]

    recommendation, confidence = _recommendation(selected)
    narrative = _decision_narrative(selected)

    assert recommendation.replace(" ", "_") == selected["raw"]["decision_result"]["decision"]
    assert confidence in narrative
    assert f"The Decision Engine recommends {recommendation}" in narrative


def test_suggested_trade_rows_reuse_risk_engine_output():
    signal = TradeSignal(
        symbol="TSLA",
        signal="BUY",
        confidence=84,
        price=250.5,
        rsi=61.2,
        ema12=255.0,
        ema26=248.0,
        stop_loss=242.0,
        target=268.0,
        reasons=["RSI recovery", "EMA bullish crossover"],
    )
    selected = _normalise({"results": [ScannerService()._to_result_row(symbol="TSLA", signal=signal, volatility=0.02)]})[0]
    state = type("State", (), {"risk_engine": RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)})()

    rows = _suggested_trade_rows_with_state(selected, state)
    values = {row["Field"]: row["Value"] for row in rows}

    assert values["Suggested Action"] == "BUY"
    assert values["Current Price"] == "250.5"
    assert values["Suggested Stop"] == "242.0"
    assert values["Suggested Target"] == "268.0"
    assert values["Suggested Position Size"] == "117.00"
    assert values["Capital at Risk"] == "$1,000.00"
    assert values["Expected Reward"] == "$2,000.00"
