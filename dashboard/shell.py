"""
===========================================================
TradePilotAI
Application Shell
===========================================================

The ApplicationShell provides the common layout for every
workspace in TradePilotAI.

Every page is rendered inside this shell.
"""

from __future__ import annotations

import streamlit as st

from dashboard.navigation import NavigationManager
from dashboard.styles import apply_theme


class ApplicationShell:
    """
    Main application shell.
    """

    def __init__(self):

        apply_theme()

        self.navigation = NavigationManager()

    def render(self) -> str:
        """
        Draw the application shell.

        Returns
        -------
        str
            Current page key.
        """

        page = self.navigation.render_sidebar()

        self._render_header()

        return page

    def _render_header(self) -> None:
        """
        Render the page header.
        """

        title = self.navigation.get_title()

        left, right = st.columns([4, 1])

        with left:

            st.title(title)

        with right:

            st.metric(
                label="Connection",
                value="LIVE",
                delta="Connected",
            )

        st.divider()

    def render_placeholder(
        self,
        page_name: str,
    ) -> None:
        """
        Temporary placeholder while pages are built.
        """

        st.info(
            f"{page_name} workspace is under construction."
        )

        st.write("")

        st.write(
            "This workspace will become part of the "
            "TradePilotAI Professional Trading Platform."
        )