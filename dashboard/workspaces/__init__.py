"""Single-entry-point workspace renderers for the TradePilotAI dashboard."""

from .dashboard import render_dashboard_workspace
from .scanner import render_scanner_workspace
from .portfolio import render_portfolio_workspace
from .risk import render_risk_workspace
from .reports import render_reports_workspace
from .backtesting import render_backtesting_workspace
from .live_trading import render_live_trading_workspace
from .trade_history import render_trade_history_workspace
from .strategy import render_strategy_workspace
from .settings import render_settings_workspace

__all__ = [
    "render_dashboard_workspace",
    "render_scanner_workspace",
    "render_portfolio_workspace",
    "render_risk_workspace",
    "render_reports_workspace",
    "render_backtesting_workspace",
    "render_live_trading_workspace",
    "render_trade_history_workspace",
    "render_strategy_workspace",
    "render_settings_workspace",
]
