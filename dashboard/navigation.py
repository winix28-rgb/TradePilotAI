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

            st.title("TradePilotAI")

            st.caption("Professional Trading Platform")

            st.divider()

            for item in self.items:

                selected = self.current_page == item.key

                label = f"{item.icon}  {item.title}"

                if st.button(
                    label,
                    use_container_width=True,
                    type="primary" if selected else "secondary",
                    key=f"nav_{item.key}",
                ):
                    self.set_page(item.key)
                    st.rerun()

            st.divider()

            st.caption("Platform Status")

            st.success("🟢 Connected")

            st.caption("Version 2.0")

        return self.current_page

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