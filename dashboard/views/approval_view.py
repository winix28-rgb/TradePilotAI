"""Approval queue view rendering helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_approval_queue(state: Any) -> None:
    """Render the approval queue as a professional trading workspace."""
    queue = getattr(state, "approval_queue", None) or getattr(state, "approval_service", None) or getattr(state, "approval_controller", None)
    if queue is None:
        st.write("No approval queue available.")
        return

    pending_trades = _collect_pending_trades(queue)
    if not pending_trades:
        st.info("There are currently no approvals awaiting review.")
        return

    filtered_trades = _filter_and_sort_trades(pending_trades)

    summary_cols = st.columns(4, gap="small")
    with summary_cols[0]:
        st.metric("Pending", len(filtered_trades))
    with summary_cols[1]:
        st.metric("Buy", _count_trade_direction(filtered_trades, "BUY"))
    with summary_cols[2]:
        st.metric("Sell", _count_trade_direction(filtered_trades, "SELL"))
    with summary_cols[3]:
        st.metric("Review", "Ready")

    st.write("")
    _render_trading_grid(state, queue, filtered_trades)


def _render_trading_grid(state: Any, queue: Any, trades: list[Any]) -> None:
    filter_cols = st.columns([2.2, 1.2, 1.2, 1.2], gap="small")
    with filter_cols[0]:
        search = st.text_input("Search ticker", placeholder="AAPL")
    with filter_cols[1]:
        sort_by = st.selectbox("Sort by", ["Confidence", "Ticker", "Strategy", "Risk", "Trend"], index=0)
    with filter_cols[2]:
        direction_filter = st.multiselect("Direction", ["BUY", "SELL"], default=[])
    with filter_cols[3]:
        trend_filter = st.multiselect("Trend", ["Bullish", "Bearish", "Neutral"], default=[])

    if search:
        trades = [trade for trade in trades if str(_safe_trade_value(trade, "ticker") or _safe_trade_value(trade, "symbol") or "").upper().startswith(search.upper())]
    if direction_filter:
        trades = [trade for trade in trades if str(_trade_direction(trade)).upper() in {value.upper() for value in direction_filter}]
    if trend_filter:
        trades = [trade for trade in trades if str(_trade_trend(trade)).capitalize() in {value.capitalize() for value in trend_filter}]

    trades = _sort_trades(trades, sort_by)

    if not trades:
        st.info("No trades match the current filters.")
        return

    header_cols = st.columns([0.9, 1.1, 0.8, 1.3, 0.8, 1.0, 0.8, 0.8, 0.9, 0.9, 1.1], gap="small")
    header_labels = ["Status", "Ticker", "Direction", "Strategy", "Confidence", "Price", "Trend", "RSI", "R/R", "Risk £", "Portfolio Impact"]
    for col, label in zip(header_cols, header_labels):
        with col:
            st.caption(label)

    st.divider()

    for index, trade in enumerate(trades):
        context = _build_trade_context(trade)
        row_cols = st.columns([0.9, 1.1, 0.8, 1.3, 0.8, 1.0, 0.8, 0.8, 0.9, 0.9, 1.2], gap="small")
        with row_cols[0]:
            st.write(_status_badge(context["status"]))
        with row_cols[1]:
            st.write(f"**{context['symbol']}**")
        with row_cols[2]:
            st.write(context["direction"])
        with row_cols[3]:
            st.write(context["strategy_name"])
        with row_cols[4]:
            st.write(context["confidence"])
        with row_cols[5]:
            st.write(context["price"])
        with row_cols[6]:
            st.write(context["trend"])
        with row_cols[7]:
            st.write(context["rsi"])
        with row_cols[8]:
            st.write(context["reward_risk"])
        with row_cols[9]:
            st.write(context["risk_value"])
        with row_cols[10]:
            if st.button("Review", key=f"review_{context['key']}", use_container_width=True):
                st.session_state["selected_trade_key"] = context["key"]
                st.session_state["selected_trade_index"] = index

    selected_key = st.session_state.get("selected_trade_key")
    if selected_key is not None:
        selected_trade = next((trade for trade in trades if _build_trade_context(trade)["key"] == selected_key), None)
        if selected_trade is not None:
            st.divider()
            _render_trade_workspace(state, queue, selected_trade)


def _render_trade_workspace(state: Any, queue: Any, trade: Any) -> None:
    context = _build_trade_context(trade)

    st.markdown("### Professional Trade Ticket")
    top_cols = st.columns([2.0, 1.0], gap="large")
    with top_cols[0]:
        st.markdown(f"## {context['symbol']} • {context['direction']}")
        st.caption(f"Strategy: {context['strategy_name']} • Confidence: {context['confidence']} • Status: {context['status']}")
    with top_cols[1]:
        st.write("")
        action_cols = st.columns(3, gap="small")
        with action_cols[0]:
            if st.button("Reject", use_container_width=True):
                _dispatch_trade_action(state, queue, trade, "reject")
        with action_cols[1]:
            if st.button("Modify", use_container_width=True):
                _dispatch_trade_action(state, queue, trade, "modify")
        with action_cols[2]:
            if st.button("Approve", use_container_width=True):
                _dispatch_trade_action(state, queue, trade, "approve")

    tabs = st.tabs(["Overview", "Chart", "Risk", "Portfolio", "History", "AI"])

    with tabs[0]:
        info_cols = st.columns([1.2, 1.0], gap="large")
        with info_cols[0]:
            trade_info = st.container(border=True)
            with trade_info:
                st.subheader("Trade Information")
                details_cols = st.columns(4, gap="small")
                for col, label, value in zip(details_cols, ["Entry", "Current", "Stop", "Target"], [context["entry_price"], context["price"], context["stop_loss"], context["target_price"]]):
                    with col:
                        st.caption(label)
                        st.write(f"**{value}**")
                risk_cols = st.columns(4, gap="small")
                for col, label, value in zip(risk_cols, ["Risk £", "Reward £", "Reward/Risk", "Portfolio Impact"], [context["risk_value"], context["reward_value"], context["reward_risk"], context["portfolio_impact"]]):
                    with col:
                        st.caption(label)
                        st.write(f"**{value}**")
        with info_cols[1]:
            indicators = st.container(border=True)
            with indicators:
                st.subheader("Indicators")
                indicator_cols = st.columns(3, gap="small")
                for col, label, value in zip(indicator_cols, ["RSI", "EMA12", "EMA26"], [context["rsi"], context["ema12"], context["ema26"]]):
                    with col:
                        st.caption(label)
                        st.write(f"**{value}**")
                st.caption("Trend")
                st.write(f"**{context['trend']}**")
                st.caption("ATR / Volume")
                st.write("ATR: N/A • Volume: N/A")

    with tabs[1]:
        st.info("Chart view is available in the broader workstation presentation and remains read-only in this sprint.")

    with tabs[2]:
        st.container(border=True)
        st.subheader("Risk")
        st.write(f"Validation Result: {context['validation_result']}")
        st.write(f"Maximum Risk: {context['max_risk']}")
        st.write(f"Portfolio Exposure: {context['portfolio_exposure']}")
        st.write(f"Duplicate Position: {context['duplicate_position']}")

    with tabs[3]:
        st.container(border=True)
        st.subheader("Portfolio")
        st.write(f"Cash Available: {context['cash_available']}")
        st.write(f"Buying Power: {context['buying_power']}")
        st.write(f"Portfolio Exposure: {context['portfolio_exposure']}")
        st.write(f"Sector Exposure: {context['sector_exposure']}")

    with tabs[4]:
        st.container(border=True)
        st.subheader("History")
        st.write("No prior execution history is available for this review pane.")

    with tabs[5]:
        st.info("AI assistance is disabled for this sprint.")

    reasons = context.get("reasons") or []
    if reasons:
        st.write("")
        st.subheader("Reasons")
        chips = st.columns(min(6, len(reasons)))
        for col, reason in zip(chips, reasons):
            with col:
                st.caption(f"● {reason}")

    st.write("")
    st.subheader("Notes")
    st.text_area("Trader notes", value="Reviewing the live signal in the professional workspace.", height=90)

    st.write("")
    editor_cols = st.columns(4, gap="small")
    with editor_cols[0]:
        edited_price = st.number_input("Edit price", value=float(context["price"]) if _is_number(context["price"]) else 0.0, key=f"workspace_price_{context['key']}")
    with editor_cols[1]:
        edited_stop = st.number_input("Edit stop loss", value=float(context["stop_loss"]) if _is_number(context["stop_loss"]) else 0.0, key=f"workspace_stop_{context['key']}")
    with editor_cols[2]:
        edited_target = st.number_input("Edit target", value=float(context["target_price"]) if _is_number(context["target_price"]) else 0.0, key=f"workspace_target_{context['key']}")
    with editor_cols[3]:
        edited_confidence = st.number_input("Edit confidence", min_value=0, max_value=100, value=int(context["confidence"]) if _is_number(context["confidence"]) else 0, key=f"workspace_confidence_{context['key']}")

    if st.button("Apply modification", use_container_width=True):
        _dispatch_trade_action(state, queue, trade, "modify", updates={
            "price": edited_price,
            "stop_loss": edited_stop,
            "target": edited_target,
            "confidence": edited_confidence,
        })


def _dispatch_trade_action(state: Any, queue: Any, trade: Any, action: str, updates: dict[str, Any] | None = None) -> None:
    candidates = [queue, getattr(state, "approval_queue", None), getattr(state, "approval_controller", None), getattr(state, "approval_service", None), getattr(state, "controller", None)]
    for candidate in candidates:
        if candidate is None:
            continue
        method_name = f"{action}_trade"
        method = getattr(candidate, method_name, None)
        if callable(method):
            try:
                if updates is None:
                    method(trade)
                else:
                    method(trade, updates)
            except TypeError:
                try:
                    method(trade)
                except Exception:
                    pass
            except Exception:
                pass
            return


def _collect_pending_trades(queue: Any) -> list[Any]:
    if queue is None:
        return []

    for attribute in ["pending_trades", "pending_orders", "approvals", "approval_queue"]:
        value = getattr(queue, attribute, None)
        if value is None:
            continue
        if isinstance(value, list):
            return [item for item in value if item is not None]
        if isinstance(value, tuple):
            return [item for item in value if item is not None]
        if hasattr(value, "__iter__") and not isinstance(value, (str, bytes, dict)):
            return [item for item in value if item is not None]

    if hasattr(queue, "state"):
        state_obj = getattr(queue, "state")
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


def _filter_and_sort_trades(trades: list[Any]) -> list[Any]:
    return list(trades)


def _sort_trades(trades: list[Any], sort_by: str) -> list[Any]:
    if sort_by == "Ticker":
        return sorted(trades, key=lambda item: str(_build_trade_context(item)["symbol"]).lower())
    if sort_by == "Strategy":
        return sorted(trades, key=lambda item: str(_build_trade_context(item)["strategy_name"]).lower())
    if sort_by == "Risk":
        return sorted(trades, key=lambda item: float(_build_trade_context(item)["risk_value"] or 0), reverse=True)
    if sort_by == "Trend":
        return sorted(trades, key=lambda item: str(_build_trade_context(item)["trend"]).lower())
    return sorted(trades, key=lambda item: int(_build_trade_context(item)["confidence"] or 0), reverse=True)


def _count_trade_direction(trades: list[Any], direction: str) -> int:
    return sum(1 for trade in trades if str(_trade_direction(trade)).upper() == direction.upper())


def _trade_direction(trade: Any) -> str:
    signal = trade if hasattr(trade, "symbol") and hasattr(trade, "signal") else None
    direction = getattr(signal, "signal", "") or _safe_trade_value(trade, "direction") or _safe_trade_value(trade, "side") or "N/A"
    return str(direction).strip() or "N/A"


def _trade_trend(trade: Any) -> str:
    signal = trade if hasattr(trade, "symbol") and hasattr(trade, "signal") else None
    return _trend_from_signal(signal)


def _safe_trade_value(trade: Any, attribute: str) -> str:
    if trade is None:
        return ""
    value = getattr(trade, attribute, None)
    if value is None:
        return ""
    return str(value)


def _status_badge(status: str) -> str:
    return f"● {status}"


def _build_trade_context(trade: Any) -> dict[str, Any]:
    signal = trade if hasattr(trade, "symbol") and hasattr(trade, "signal") else None
    direction = str(getattr(signal, "signal", "") or _safe_trade_value(trade, "direction") or _safe_trade_value(trade, "side") or "N/A")
    symbol = getattr(signal, "symbol", None) or _safe_trade_value(trade, "ticker") or _safe_trade_value(trade, "symbol") or "-"
    price = getattr(signal, "price", None) or _safe_trade_value(trade, "price") or _safe_trade_value(trade, "entry_price") or "-"
    entry_price = getattr(signal, "price", None) or _safe_trade_value(trade, "entry_price") or _safe_trade_value(trade, "price") or "-"
    stop_loss = getattr(signal, "stop_loss", None) or _safe_trade_value(trade, "stop_loss") or _safe_trade_value(trade, "stop") or "-"
    target_price = getattr(signal, "target", None) or _safe_trade_value(trade, "target") or _safe_trade_value(trade, "take_profit") or "-"
    strategy_name = getattr(signal, "strategy_name", None) or "RSI Mean Reversion"
    confidence = getattr(signal, "confidence", None) or _safe_trade_value(trade, "confidence") or "-"
    reasons = getattr(signal, "reasons", None) or []
    trend = _trend_from_signal(signal)
    rsi = getattr(signal, "rsi", None)
    ema12 = getattr(signal, "ema12", None)
    ema26 = getattr(signal, "ema26", None)
    reward_risk = _reward_risk_ratio(entry_price, stop_loss, target_price)
    risk_value = _risk_value(entry_price, stop_loss)
    reward_value = _reward_value(entry_price, target_price)
    portfolio_impact = _portfolio_impact(risk_value)
    portfolio_exposure = "N/A"
    cash_available = "N/A"
    buying_power = "N/A"
    sector_exposure = "N/A"
    max_risk = "N/A"
    validation_result = "Pending review"
    duplicate_position = "No"

    return {
        "status": "Pending",
        "symbol": symbol,
        "direction": direction,
        "strategy_name": strategy_name,
        "confidence": confidence,
        "price": price,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target_price": target_price,
        "trend": trend,
        "rsi": rsi,
        "ema12": ema12,
        "ema26": ema26,
        "reward_risk": reward_risk,
        "risk_value": risk_value,
        "reward_value": reward_value,
        "portfolio_impact": portfolio_impact,
        "reasons": reasons,
        "portfolio_exposure": portfolio_exposure,
        "cash_available": cash_available,
        "buying_power": buying_power,
        "sector_exposure": sector_exposure,
        "max_risk": max_risk,
        "validation_result": validation_result,
        "duplicate_position": duplicate_position,
        "key": f"{symbol}_{direction}_{strategy_name}",
    }


def _trend_from_signal(signal: Any) -> str:
    if signal is None:
        return "Neutral"
    ema12 = getattr(signal, "ema12", None)
    ema26 = getattr(signal, "ema26", None)
    if ema12 is None or ema26 is None:
        return "Neutral"
    if float(ema12) > float(ema26):
        return "Bullish"
    if float(ema12) < float(ema26):
        return "Bearish"
    return "Neutral"


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _reward_risk_ratio(entry_price: Any, stop_loss: Any, target_price: Any) -> str:
    try:
        entry = float(entry_price)
        stop = float(stop_loss)
        target = float(target_price)
    except (TypeError, ValueError):
        return "N/A"

    if stop <= 0 or entry <= 0:
        return "N/A"

    risk_distance = abs(entry - stop)
    if risk_distance <= 0:
        return "N/A"

    reward_distance = abs(target - entry)
    if reward_distance <= 0:
        return "N/A"

    return f"{reward_distance / risk_distance:.2f}"


def _reward_value(entry_price: Any, target_price: Any) -> str:
    try:
        entry = float(entry_price)
        target = float(target_price)
    except (TypeError, ValueError):
        return "N/A"
    return f"{abs(target - entry):.2f}"


def _risk_value(entry_price: Any, stop_loss: Any) -> str:
    try:
        entry = float(entry_price)
        stop = float(stop_loss)
    except (TypeError, ValueError):
        return "N/A"
    return f"{abs(entry - stop):.2f}"


def _portfolio_impact(risk_value: Any) -> str:
    try:
        value = float(risk_value)
    except (TypeError, ValueError):
        return "N/A"
    if value >= 10:
        return "High"
    if value >= 5:
        return "Medium"
    return "Low"
