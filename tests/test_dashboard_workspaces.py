from dashboard.workspaces import (
    render_backtesting_workspace,
    render_dashboard_workspace,
    render_live_trading_workspace,
    render_portfolio_workspace,
    render_reports_workspace,
    render_risk_workspace,
    render_scanner_workspace,
    render_settings_workspace,
    render_strategy_workspace,
    render_trade_history_workspace,
)


def test_dashboard_workspace_modules_export_renderers():
    assert callable(render_dashboard_workspace)
    assert callable(render_scanner_workspace)
    assert callable(render_portfolio_workspace)
    assert callable(render_risk_workspace)
    assert callable(render_reports_workspace)
    assert callable(render_backtesting_workspace)
    assert callable(render_live_trading_workspace)
    assert callable(render_trade_history_workspace)
    assert callable(render_strategy_workspace)
    assert callable(render_settings_workspace)
