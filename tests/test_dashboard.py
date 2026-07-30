from tradepilotai_os.dashboard import DashboardPage


def test_dashboard_renders_expected_panels():
    view = DashboardPage()
    rendered = view.render()

    assert "TRADEPILOTAI OS DASHBOARD" in rendered
    assert "System Status" in rendered
    assert "KPI Overview" in rendered
    assert "Equity Curve" in rendered
    assert "Pipeline Summary" in rendered
    assert "Portfolio Snapshot" in rendered
    assert "Market Scanner Summary" in rendered
    assert "Strategy Performance" in rendered
    assert "Recent Trades" in rendered
    assert "System Messages" in rendered
