"""Strategy-related dashboard view rendering helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_strategy(state: Any) -> None:
    """Render the live strategy view content in a trading-terminal layout."""
    service = getattr(state, "live_strategy_service", None)
    controller = getattr(state, "controller", None)
    if service is None and controller is None:
        st.write("No live strategy data available.")
        return

    diagnostics = _extract_diagnostics(service)
    symbol = _coerce_value(diagnostics.get("symbol") or diagnostics.get("ticker") or diagnostics.get("current_symbol"))
    price = _coerce_value(diagnostics.get("current_price") or diagnostics.get("price") or diagnostics.get("last_price"))
    rsi = _coerce_value(diagnostics.get("rsi") or diagnostics.get("RSI"))
    ema12 = _coerce_value(diagnostics.get("ema_12") or diagnostics.get("ema12") or diagnostics.get("fast_ema"))
    ema26 = _coerce_value(diagnostics.get("ema_26") or diagnostics.get("ema26") or diagnostics.get("slow_ema"))
    signal = _coerce_value(diagnostics.get("signal") or diagnostics.get("status") or diagnostics.get("strategy_state"))

    metrics_cols = st.columns(6, gap="small")
    values = [("Current Symbol", symbol), ("Current Price", price), ("RSI", rsi), ("EMA12", ema12), ("EMA26", ema26), ("Signal", signal)]
    for column, (label, value) in zip(metrics_cols, values):
        with column:
            st.caption(label)
            st.write(f"**{value}**")

    st.write("")
    st.write("**Checklist**")
    checklist_items = [
        ("RSI Oversold", _is_checked(rsi, "oversold")),
        ("EMA Bullish Cross", _is_checked(signal, "buy") or _is_checked(signal, "bullish") or _is_checked(signal, "long")),
        ("Risk Acceptable", _is_checked(diagnostics.get("risk"), "acceptable") or _is_checked(diagnostics.get("risk_level"), "acceptable")),
        ("Entry Confirmed", _is_checked(signal, "buy") or _is_checked(signal, "long") or _is_checked(signal, "confirm")),
    ]
    for label, checked in checklist_items:
        st.write(f"{'✓' if checked else '○'} {label}")

    st.write("")
    explanation_items = _extract_explanation_items(service)
    if explanation_items:
        st.write("**Signal Notes**")
        for item in explanation_items:
            st.write(f"• {item}")
    else:
        st.caption("No explanation provided by the current diagnostics.")

    st.write("")
    if st.button("Run Strategy", key="dashboard_run_strategy", use_container_width=True):
        _trigger_strategy_action(state)

    st.caption(f"Strategy service: {type(service).__name__ if service else 'Unavailable'}")
    st.caption(f"Controller: {type(controller).__name__ if controller else 'Unavailable'}")


def _extract_diagnostics(service: Any) -> Any:
    if service is None:
        return {}
    if hasattr(service, "get_diagnostics"):
        try:
            diagnostics = service.get_diagnostics()
            if isinstance(diagnostics, dict):
                return diagnostics
        except Exception:
            return {}
    if hasattr(service, "diagnostics"):
        return getattr(service, "diagnostics") or {}
    return {}


def _extract_explanation_items(service: Any) -> list[str]:
    diagnostics = _extract_diagnostics(service)
    if isinstance(diagnostics, dict):
        explanation = diagnostics.get("explanation") or diagnostics.get("strategy_explanation") or diagnostics.get("explanations")
        if isinstance(explanation, list):
            return [str(item) for item in explanation if str(item).strip()]
        if isinstance(explanation, str):
            return [explanation]
        if isinstance(explanation, dict):
            return [f"{key}: {value}" for key, value in explanation.items() if value is not None]
    return []


def _trigger_strategy_action(state: Any) -> None:
    controller = getattr(state, "controller", None)
    service = getattr(state, "live_strategy_service", None)
    for candidate in [controller, service]:
        if candidate is None:
            continue
        for method_name in ["run_strategy", "execute_strategy", "trigger_strategy", "run_live_strategy", "process_strategy"]:
            method = getattr(candidate, method_name, None)
            if callable(method):
                try:
                    method()
                except Exception:
                    pass
                return


def _coerce_value(value: Any) -> str:
    if value is None:
        return "N/A"
    return str(value)


def _is_checked(value: Any, expected: str) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    return expected.lower() in text
