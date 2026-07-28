"""
===========================================================
TradePilotAI
Performance Dashboard Page
===========================================================

Displays trading performance statistics.
"""

import streamlit as st



def show_performance(
    performance_engine,
):
    """
    Display performance metrics.
    """

    st.title(
        "📈 Performance Dashboard"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Total Trades",
            performance_engine.total_trades,
        )


    with col2:

        st.metric(
            "Win Rate",
            f"{performance_engine.win_rate:.2f}%",
        )


    with col3:

        profit_factor = (
            performance_engine.profit_factor
        )

        if profit_factor == float("inf"):

            value = "∞"

        else:

            value = f"{profit_factor:.2f}"


        st.metric(
            "Profit Factor",
            value,
        )


    st.divider()


    col4, col5 = st.columns(2)


    with col4:

        st.metric(
            "Net Profit",
            f"£{performance_engine.net_profit:.2f}",
        )


    with col5:

        st.metric(
            "Maximum Drawdown",
            f"£{performance_engine.maximum_drawdown:.2f}",
        )


    st.divider()


    st.subheader(
        "Equity Curve"
    )


    curve = (
        performance_engine.equity_curve
    )


    if curve:

        st.line_chart(
            curve
        )

    else:

        st.info(
            "No performance data available."
        )