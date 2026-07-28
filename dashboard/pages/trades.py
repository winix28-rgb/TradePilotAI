"""
===========================================================
TradePilotAI
Trade History Page
===========================================================

Displays recorded trading events.
"""

import streamlit as st



def show_trade_history(
    journal,
):
    """
    Display trade journal events.
    """


    st.title(
        "📒 Trade History"
    )


    events = journal.events()


    if not events:

        st.info(
            "No trade history available."
        )

        return



    for event in reversed(events):

        st.divider()


        st.write(
            f"Time: {event['time']}"
        )

        st.write(
            f"Event: {event['type']}"
        )

        st.write(
            f"Symbol: {event['symbol']}"
        )


        if event["details"]:

            st.json(
                event["details"]
            )