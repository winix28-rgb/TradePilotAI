from dashboard import app as dashboard_app


def test_dispatcher_maps_sidebar_routes_to_existing_renderers():
    assert dashboard_app._resolve_renderer_key("dashboard") == "dashboard"
    assert dashboard_app._resolve_renderer_key("scanner") == "scanner"
    assert dashboard_app._resolve_renderer_key("portfolio") == "portfolio"
    assert dashboard_app._resolve_renderer_key("trades") == "trade_history"
    assert dashboard_app._resolve_renderer_key("strategies") == "strategy"
    assert dashboard_app._resolve_renderer_key("risk") == "risk"
    assert dashboard_app._resolve_renderer_key("performance") == "performance"
    assert dashboard_app._resolve_renderer_key("reports") == "reports"
    assert dashboard_app._resolve_renderer_key("validation") == "validation"
    assert dashboard_app._resolve_renderer_key("system_status") == "system_status"
    assert dashboard_app._resolve_renderer_key("paper_trading") == "paper_trading"
    assert dashboard_app._resolve_renderer_key("trade_journal") == "trade_journal"


def test_workspace_navigation_chrome_is_removed_before_rendering():
    sample = "\n".join(
        [
            "",
            "====================",
            "SCANNER WORKSPACE",
            "====================",
            "",
            "Scanner Overview - Trading opportunity workspace",
            "",
            "Scanner Controls: Scan | Refresh",
            "",
            "Dashboard / Scanner",
            "",
            "Scanner[live]",
            "",
            "Scanner Summary",
            "",
        ]
    )

    cleaned = dashboard_app._strip_workspace_navigation_markup(sample)

    assert "SCANNER WORKSPACE" in cleaned
    assert "Scanner Overview" in cleaned
    assert "Scanner Controls" not in cleaned
    assert "Dashboard / Scanner" not in cleaned
    assert "Scanner Summary" in cleaned


def test_streamlit_runtime_disables_builtin_sidebar_navigation():
    assert hasattr(dashboard_app, "st")
