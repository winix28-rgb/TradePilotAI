import contextlib

import streamlit as st

import dashboard.navigation as navigation_module


def test_render_sidebar_switches_page_via_radio_selection(monkeypatch):
    """Navigation should accept a sidebar selection and update the active workspace."""
    st.session_state.clear()
    st.session_state.current_page = "dashboard"

    class DummySidebar:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_radio(label, options, *, index=0, key=None, label_visibility="visible", **kwargs):
        assert label == "Navigation"
        assert options == [item.key for item in navigation_module.NavigationManager().items]
        return "scanner"

    monkeypatch.setattr(navigation_module.st, "sidebar", DummySidebar())
    monkeypatch.setattr(navigation_module.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(navigation_module.st, "radio", fake_radio)
    monkeypatch.setattr(navigation_module.st, "rerun", lambda: None)
    monkeypatch.setattr(navigation_module.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(navigation_module.st, "title", lambda *args, **kwargs: None)
    monkeypatch.setattr(navigation_module.st, "caption", lambda *args, **kwargs: None)

    manager = navigation_module.NavigationManager()
    page = manager.render_sidebar()

    assert page == "scanner"
    assert st.session_state.current_page == "scanner"
