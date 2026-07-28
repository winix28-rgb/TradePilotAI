"""
===========================================================
TradePilotAI Dashboard
===========================================================

Main trading control interface.
"""

import streamlit as st

from dashboard.state import state
from dashboard.components.trade_card import show_trade_card


st.set_page_config(
    page_title="TradePilotAI",
    layout="wide",
)


# =========================================================
# HEADER
# =========================================================

st.title("🚀 TradePilotAI Dashboard")


# =========================================================
# SYSTEM STATUS
# =========================================================

st.header("System Status")


col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Engine",
        state.engine_status
    )


with col2:
    st.metric(
        "Mode",
        state.mode
    )


with col3:
    st.metric(
        "Connection",
        state.connection_status
    )


# =========================================================
# APPROVAL QUEUE
# =========================================================

st.divider()

st.header(
    "Trade Approval Queue"
)


pending = state.pending_trades()


if not pending:

    st.info(
        "No pending trade approvals."
    )

else:

    for trade in pending:

        show_trade_card(
            trade,
            state.approval_manager,
        )


# =========================================================
# RECENT ACTIVITY
# =========================================================

st.divider()

st.header(
    "Recent Activity"
)


if hasattr(state, "journal"):

    events = state.journal.events()


    if events:

        for event in reversed(events[-5:]):

            st.write(
                f"{event['type']} - {event['symbol']}"
            )

    else:

        st.info(
            "No activity recorded."
        )

else:

    st.info(
        "Journal not connected yet."
    )


# =========================================================
# PERFORMANCE SUMMARY
# =========================================================

st.divider()

st.header(
    "Performance Summary"
)


if hasattr(state, "performance"):

    performance = state.performance


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "Trades",
            performance.total_trades
        )


    with c2:

        st.metric(
            "Win Rate",
            f"{performance.win_rate:.2f}%"
        )


    with c3:

        st.metric(
            "Profit Factor",
            f"{performance.profit_factor:.2f}"
        )

else:

    st.info(
        "Performance engine not connected yet."
    )