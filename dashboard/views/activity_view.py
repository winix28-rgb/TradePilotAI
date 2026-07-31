"""Activity view rendering helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_activity(state: Any) -> None:
    """Render the recent activity view."""
    journal = getattr(state, "journal", None)
    if journal is None:
        st.write("No journal activity available.")
        return

    if hasattr(journal, "entries"):
        entries = list(getattr(journal, "entries"))
        if entries:
            for entry in entries[:5]:
                st.write(str(entry))
        else:
            st.write("No recent activity recorded.")
    else:
        st.write(str(journal))
