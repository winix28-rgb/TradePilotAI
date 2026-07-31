"""
TradePilotAI Layout Helpers
"""

from __future__ import annotations

from contextlib import contextmanager

import streamlit as st


# ----------------------------------------------------------
# Spacing
# ----------------------------------------------------------

def spacer(lines: int = 1) -> None:
    """Insert vertical spacing."""
    for _ in range(lines):
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ----------------------------------------------------------
# Section Title
# ----------------------------------------------------------

def section(title: str) -> None:
    """Render a section heading."""
    st.markdown(
        f"""
        <div class="tp-panel-title">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------
# Card Container
# ----------------------------------------------------------

@contextmanager
def card():
    """
    Creates a bordered card.

    Usage

        with card():
            st.write(...)
    """

    st.markdown(
        """
        <div class="tp-card">
        """,
        unsafe_allow_html=True,
    )

    yield

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------
# Status Badge
# ----------------------------------------------------------

def badge(
    text: str,
    colour: str = "info",
):
    colours = {
        "success": ("#DCFCE7", "#166534"),
        "danger": ("#FEE2E2", "#991B1B"),
        "warning": ("#FEF3C7", "#92400E"),
        "info": ("#DBEAFE", "#1E3A8A"),
    }

    bg, fg = colours.get(colour, colours["info"])

    st.markdown(
        f"""
        <span style="
            background:{bg};
            color:{fg};
            padding:5px 12px;
            border-radius:999px;
            font-size:13px;
            font-weight:600;">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------
# KPI Card
# ----------------------------------------------------------

def kpi(
    title: str,
    value: str,
    delta: str | None = None,
):
    with card():

        st.caption(title)

        st.markdown(
            f"""
            <div style="
                font-size:28px;
                font-weight:700;
                color:#111827;">
                {value}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if delta:
            st.caption(delta)


# ----------------------------------------------------------
# Empty State
# ----------------------------------------------------------

def empty_panel(message: str = "No data available") -> None:
    st.info(message)