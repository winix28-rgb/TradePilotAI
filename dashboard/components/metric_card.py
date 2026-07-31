"""
===========================================================
TradePilotAI
Metric Card Component
===========================================================

Reusable metric cards used throughout the application.
"""

from __future__ import annotations

import streamlit as st


class MetricCard:
    """
    Professional metric card.

    Example
    -------
    MetricCard(
        "Portfolio Value",
        "£102,550",
        "+2.15%"
    ).render()
    """

    def __init__(
        self,
        title: str,
        value: str,
        delta: str = "",
        help_text: str | None = None,
    ):

        self.title = title
        self.value = value
        self.delta = delta
        self.help_text = help_text

    def render(self) -> None:

        with st.container():

            st.markdown(
                '<div class="tp-card">',
                unsafe_allow_html=True,
            )

            st.metric(
                label=self.title,
                value=self.value,
                delta=self.delta,
                help=self.help_text,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


def metric_grid(cards: list[MetricCard], columns: int = 4) -> None:
    """
    Render a responsive grid of metric cards.

    Parameters
    ----------
    cards
        List of MetricCard objects.

    columns
        Number of columns.
    """

    if not cards:
        return

    for start in range(0, len(cards), columns):

        row = cards[start : start + columns]

        cols = st.columns(len(row))

        for col, card in zip(cols, row):

            with col:
                card.render()