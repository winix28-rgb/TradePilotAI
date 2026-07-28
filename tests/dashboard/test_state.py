"""
===========================================================
TradePilotAI
Dashboard State Tests
===========================================================
"""

from dashboard.state import DashboardState



def test_dashboard_state_creates_services():

    state = DashboardState()

    assert state.application is not None

    assert state.approval_manager is not None

    assert state.journal is not None

    assert state.performance is not None



def test_dashboard_state_has_status():

    state = DashboardState()

    assert state.engine_status == "RUNNING"

    assert state.mode == "DEMO"

    assert state.connection_status == "CONNECTED"