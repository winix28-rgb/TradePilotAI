"""
===========================================================
TradePilotAI Dashboard
===========================================================

Operator interface.

Version 1:
- System status
- Trading mode
- Account display
- Signal monitoring

No execution controls yet.
"""

import streamlit as st


st.set_page_config(
    page_title="TradePilotAI",
    layout="wide",
)


st.title("🚀 TradePilotAI Dashboard")


# =========================================================
# STATUS
# =========================================================

st.header("System Status")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Engine Status",
        "RUNNING",
    )


with col2:

    st.metric(
        "Trading Mode",
        "DEMO",
    )


with col3:

    st.metric(
        "Risk Status",
        "NORMAL",
    )


# =========================================================
# ACCOUNT
# =========================================================

st.header("Account")


account_col1, account_col2, account_col3 = st.columns(3)


with account_col1:

    st.metric(
        "Balance",
        "£10,000",
    )


with account_col2:

    st.metric(
        "Equity",
        "£10,000",
    )


with account_col3:

    st.metric(
        "Open Positions",
        "0",
    )


# =========================================================
# SIGNALS
# =========================================================

st.header("Latest Signals")


signals = [

    {
        "Symbol": "RR.L",
        "Signal": "BUY",
        "Reason": "RSI Oversold + EMA Cross",
    },

    {
        "Symbol": "TSCO.L",
        "Signal": "WAIT",
        "Reason": "No setup",
    },

]


st.table(
    signals
)


# =========================================================
# CONTROLS
# =========================================================

st.header("Trading Controls")


if st.button("Pause Trading"):

    st.warning(
        "Trading paused"
    )


if st.button("Emergency Stop"):

    st.error(
        "Emergency stop activated"
    )