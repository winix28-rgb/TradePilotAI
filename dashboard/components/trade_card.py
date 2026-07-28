"""
===========================================================
TradePilotAI
Trade Approval Card
===========================================================

Displays pending trades in dashboard.
"""

import streamlit as st



def show_trade_card(
    trade,
    controller,
):
    """
    Display a trade approval card.
    """

    st.subheader(
        f"{trade.action} {trade.symbol}"
    )


    st.write(
        f"Quantity: {trade.quantity}"
    )


    st.write(
        f"Entry Price: £{trade.entry_price:.2f}"
    )


    if trade.stop_loss:

        st.write(
            f"Stop Loss: £{trade.stop_loss:.2f}"
        )


    st.write(
        f"Strategy: {trade.strategy}"
    )


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "✅ Approve",
            key=f"approve_{trade.symbol}",
        ):

            controller.approve_trade(
                trade.symbol
            )

            st.success(
                "Trade approved"
            )



    with col2:

        if st.button(
            "❌ Reject",
            key=f"reject_{trade.symbol}",
        ):

            controller.reject_trade(
                trade.symbol
            )

            st.error(
                "Trade rejected"
            )