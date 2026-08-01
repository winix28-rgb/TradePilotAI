"""
===========================================================
TradePilotAI
Navigation
===========================================================

Central navigation manager for the TradePilotAI dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import streamlit as st


@dataclass(frozen=True)
class NavigationItem:
    """Represents a page within the application."""

    key: str
    title: str
    icon: str
    page: Callable | None = None


class NavigationManager:
    """
    Handles dashboard navigation.
    """

    def __init__(self):

        self.items: list[NavigationItem] = [
            NavigationItem("dashboard", "Dashboard", "🏠"),
            NavigationItem("scanner", "Market Scanner", "🔍"),
            NavigationItem("portfolio", "Portfolio", "💼"),
            NavigationItem("positions", "Positions", "📈"),
            NavigationItem("orders", "Orders", "📋"),
            NavigationItem("trades", "Trade History", "📜"),
            NavigationItem("performance", "Performance", "📊"),
            NavigationItem("backtesting", "Backtesting", "🧪"),
            NavigationItem("strategies", "Strategies", "🧠"),
            NavigationItem("risk", "Risk Management", "🛡️"),
            NavigationItem("reports", "Reports", "📑"),
            NavigationItem("settings", "Settings", "⚙️"),
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

    @property
    def current_page(self) -> str:
        return st.session_state.current_page

    def set_page(self, page: str) -> None:
        st.session_state.current_page = page

    def render_sidebar(self) -> str:
        """
        Draw the application sidebar.
        """

        with st.sidebar:
            st.markdown("<div style='margin-bottom:0.2rem;'></div>", unsafe_allow_html=True)
            st.title("TradePilotAI")
            st.caption("Professional Trading Platform")
            st.markdown("<div style='margin-top:0.2rem;'></div>", unsafe_allow_html=True)

            options = [item.key for item in self.items]
            index = options.index(self.current_page) if self.current_page in options else 0
            selected = st.radio(
                "Navigation",
                options,
                index=index,
                key="sidebar_navigation",
                label_visibility="collapsed",
                format_func=lambda page_key: self._label_for(page_key),
            )

            if selected != self.current_page:
                self.set_page(selected)
                return selected

            st.markdown("<div style='margin-top:0.35rem;'></div>", unsafe_allow_html=True)
            st.caption("Platform Status")
            st.markdown("<div class='tp-status-badge'>🟢 Connected</div>", unsafe_allow_html=True)
            st.caption("Version 2.0")

        return self.current_page

    def _label_for(self, page_key: str) -> str:
        """Return the display label for a navigation key."""
        for item in self.items:
            if item.key == page_key:
                return f"{item.icon}  {item.title}"
        return page_key

    def get_title(self) -> str:
        """
        Returns the current page title.
        """

        for item in self.items:
            if item.key == self.current_page:
                return item.title

        return "Dashboard"

    def pages(self) -> list[NavigationItem]:
        """
        Returns all available pages.
        """

        return self.items