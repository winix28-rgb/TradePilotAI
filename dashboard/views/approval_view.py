"""Approval queue view rendering helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_approval_queue(state: Any) -> None:
    """Render the trade approval queue view with actionable approval cards."""
    controller = getattr(state, "controller", None)
    if controller is None:
        st.write("No approval queue available.")
        return

    pending_trades = _collect_pending_trades(controller)

    if not pending_trades:
        st.info("There are currently no approvals awaiting review.")
        return

    summary_cols = st.columns(3, gap="small")
    with summary_cols[0]:
        st.metric("Pending", len(pending_trades))
    with summary_cols[1]:
        st.metric("Buy", _count_trade_direction(pending_trades, "BUY"))
    with summary_cols[2]:
        st.metric("Sell", _count_trade_direction(pending_trades, "SELL"))

    st.write("")
    for index, trade in enumerate(pending_trades):
        _render_trade_card(state, trade, index)
        st.write("")


def _render_trade_card(state: Any, trade: Any, index: int) -> None:
    direction = _safe_trade_value(trade, "direction") or _safe_trade_value(trade, "side") or "N/A"
    symbol = _safe_trade_value(trade, "ticker") or _safe_trade_value(trade, "symbol") or "-"
    entry = _safe_trade_value(trade, "entry_price") or _safe_trade_value(trade, "price") or "-"
    stop = _safe_trade_value(trade, "stop_loss") or _safe_trade_value(trade, "stop") or "-"
    risk = _safe_trade_value(trade, "risk") or _safe_trade_value(trade, "risk_per_trade") or "-"

    st.markdown(
        f"""
        <div style="padding:0.9rem 1rem; border:1px solid #4B5563; border-radius:10px; background:#374151;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                <div><strong>{symbol}</strong></div>
                <div><span style="font-weight:600;">{direction}</span></div>
            </div>
            <div style="margin-top:0.45rem; color:#D1D5DB; font-size:0.95rem;">
                Entry: {entry} &nbsp;·&nbsp; Stop: {stop} &nbsp;·&nbsp; Risk: {risk}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    button_col1, button_col2 = st.columns(2, gap="small")
    with button_col1:
        if st.button("Approve", key=f"approve_{index}_{id(trade)}", use_container_width=True):
            _dispatch_trade_action(state, trade, "approve")
    with button_col2:
        if st.button("Reject", key=f"reject_{index}_{id(trade)}", use_container_width=True):
            _dispatch_trade_action(state, trade, "reject")


def _dispatch_trade_action(state: Any, trade: Any, action: str) -> None:
    candidates = [
        getattr(state, "controller", None),
        getattr(state, "approval_controller", None),
        getattr(state, "approval_service", None),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        for method_name in [f"{action}_trade", f"{action}_order", f"{action}_pending_trade", f"handle_{action}_trade", f"process_{action}_trade"]:
            method = getattr(candidate, method_name, None)
            if callable(method):
                try:
                    method(trade)
                except Exception:
                    pass
                return


def _collect_pending_trades(controller: Any) -> list[Any]:
    if controller is None:
        return []

    for attribute in ["pending_trades", "pending_orders", "approvals", "approval_queue"]:
        value = getattr(controller, attribute, None)
        if value is None:
            continue
        if isinstance(value, list):
            return [item for item in value if item is not None]
        if isinstance(value, tuple):
            return [item for item in value if item is not None]
        if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
            return [item for item in value if item is not None]

    if hasattr(controller, "state"):
        state_obj = getattr(controller, "state")
        if state_obj is not None:
            for attribute in ["pending_trades", "pending_orders", "approvals", "approval_queue"]:
                value = getattr(state_obj, attribute, None)
                if value is None:
                    continue
                if isinstance(value, list):
                    return [item for item in value if item is not None]
                if isinstance(value, tuple):
                    return [item for item in value if item is not None]
                if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
                    return [item for item in value if item is not None]

    return []


def _count_trade_direction(trades: list[Any], direction: str) -> int:
    return sum(1 for trade in trades if str(_safe_trade_value(trade, "direction") or "").upper() == direction.upper())


def _safe_trade_value(trade: Any, attribute: str) -> str:
    if trade is None:
        return ""
    value = getattr(trade, attribute, None)
    if value is None:
        return ""
    return str(value)
