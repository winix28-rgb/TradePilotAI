"""Regression tests for the dashboard shell module."""

from dashboard.shell import ApplicationShell


def test_dashboard_shell_can_be_imported() -> None:
    """The shell should import cleanly without missing page modules."""
    assert ApplicationShell is not None
