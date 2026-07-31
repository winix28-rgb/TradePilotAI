"""Reusable UI widgets for the Strategy Centre workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.ui_library import Card, DataTable, KPIChartCard, SectionHeader


class StrategySummaryCard(KPIChartCard):
    """Display a KPIs summary for a strategy."""

    def __init__(self, title: str, value: str, subtitle: str | None = None) -> None:
        super().__init__(title=title, value=value, subtitle=subtitle)


class StrategyLibraryTable(DataTable):
    """Render the strategy library table."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        table_rows = [
            [item.get("name", "-"), item.get("version", "-"), item.get("description", "-"), item.get("status", "-"), item.get("markets", "-"), item.get("timeframe", "-"), item.get("created_date", "-"), item.get("last_modified", "-")]
            for item in rows
        ]
        super().__init__(headers=["Strategy Name", "Version", "Description", "Status", "Supported Markets", "Timeframe", "Created Date", "Last Modified"], rows=table_rows)


class StrategyConfigurationCard(Card):
    """Render the strategy configuration summary."""

    def __init__(self, config: dict[str, Any]) -> None:
        body = [f"RSI Period: {config.get('rsi_period', 'N/A')}", f"RSI Buy Level: {config.get('rsi_buy_level', 'N/A')}", f"RSI Sell Level: {config.get('rsi_sell_level', 'N/A')}", f"EMA Fast: {config.get('ema_fast', 'N/A')}", f"EMA Slow: {config.get('ema_slow', 'N/A')}", f"Risk Per Trade: {config.get('risk_per_trade', 'N/A')}", f"Maximum Positions: {config.get('max_positions', 'N/A')}", f"Reward : Risk: {config.get('reward_risk', 'N/A')}", f"Stop Loss: {config.get('stop_loss', 'N/A')}", f"Take Profit: {config.get('take_profit', 'N/A')}", f"Execution: {config.get('execution_mode', 'Paper')}"]
        super().__init__(title="Strategy Configuration", body=body)


class PerformanceSummaryCard(Card):
    """Render the strategy performance summary."""

    def __init__(self, performance: dict[str, Any]) -> None:
        body = [f"Backtest Return: {performance.get('backtest_return', 'N/A')}", f"Paper Return: {performance.get('paper_return', 'N/A')}", f"Live Return: {performance.get('live_return', 'N/A')}", f"Win Rate: {performance.get('win_rate', 'N/A')}", f"Profit Factor: {performance.get('profit_factor', 'N/A')}", f"Sharpe Ratio: {performance.get('sharpe_ratio', 'N/A')}", f"Max Drawdown: {performance.get('max_drawdown', 'N/A')}", f"Total Trades: {performance.get('total_trades', 'N/A')}"]
        super().__init__(title="Performance Summary", body=body)


class VersionHistoryCard(Card):
    """Render the version history table."""

    def __init__(self, versions: list[dict[str, Any]]) -> None:
        body = [f"{item.get('version', '-')}: {item.get('date', '-')}, {item.get('author', '-')}, {item.get('notes', '-')}" for item in versions]
        super().__init__(title="Version History", body=body)


class DeploymentCard(Card):
    """Render the deployment summary."""

    def __init__(self, deployment: dict[str, Any]) -> None:
        body = [f"Target: {deployment.get('target', 'N/A')}", f"Status: {deployment.get('status', 'N/A')}", f"Broker Interface: {deployment.get('broker_interface', 'N/A')}", f"Orchestrator: {deployment.get('orchestrator', 'N/A')}"]
        super().__init__(title="Deployment", body=body)
