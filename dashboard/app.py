"""
===========================================================
TradePilotAI Dashboard
===========================================================
"""

import streamlit as st

from dashboard.state import state
from dashboard.components.trade_card import show_trade_card



st.set_page_config(
    page_title="TradePilotAI",
    layout="wide",
)


st.title("🚀 TradePilotAI Dashboard")


# =========================================================
# STATUS
# =========================================================

st.header("System Status")


c1, c2, c3 = st.columns(3)


with c1:
    st.metric(
        "Engine",
        state.engine_status,
    )


with c2:
    st.metric(
        "Mode",
        state.mode,
    )


with c3:
    st.metric(
        "IG Connection",
        state.connection_status,
    )



# =========================================================
# APPROVAL QUEUE
# =========================================================

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