"""Backtesting dashboard page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import (
    Breadcrumb,
    Card,
    SectionHeader,
    StatusBadge,
    StatusBar,
    Toolbar,
)
from tradepilotai_os.workspace import WorkspacePage

from .components import BacktestChartCard, BacktestKpiCard, BacktestStatsTable, BacktestSummarySection, BacktestTradeList
from .data_provider import BacktestingDataProvider


class BacktestingPage(WorkspacePage):
    """Render a professional backtesting dashboard using shared UI components."""

    def __init__(self, data_provider: BacktestingDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Backtesting", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.get_backtest_data()
        else:
            self.data = {
                "summary": {"status": "pending"},
                "metrics": {},
                "charts": {},
                "best_trades": [],
                "worst_trades": [],
                "trade_statistics": [],
                "trade_list": [],
                "events": [],
            }

        metrics = self.data.get("metrics", {})
        charts = self.data.get("charts", {})
        trade_statistics = self.data.get("trade_statistics", [])
        best_trades = self.data.get("best_trades", [])
        worst_trades = self.data.get("worst_trades", [])
        trade_list = self.data.get("trade_list", [])
        events = self.data.get("events", [])

        lines = [
            "",
            "=" * 80,
            "BACKTESTING DASHBOARD",
            "=" * 80,
            "",
            SectionHeader(title="Backtest Overview", subtitle="Shared component layout").render(),
            "",
            Toolbar(title="Backtest Controls", actions=["Run", "Export"]).render(),
            "",
            self._build_breadcrumbs(),
            "",
            StatusBadge(label="Backtest", status="ready").render(),
            "",
            BacktestSummarySection(title="Summary", body=[f"Status: {self.data.get('summary', {}).get('status', 'pending')}", f"Source: {self.data.get('summary', {}).get('source', 'placeholder')}"]).render(),
            "",
            BacktestKpiCard(title="Total Return", value=metrics.get("total_return", "0%"), subtitle="performance").render(),
            BacktestKpiCard(title="Net Profit", value=metrics.get("net_profit", "$0"), subtitle="absolute pnl").render(),
            BacktestKpiCard(title="CAGR", value=metrics.get("cagr", "0%"), subtitle="annualized").render(),
            BacktestKpiCard(title="Win Rate", value=metrics.get("win_rate", "0%"), subtitle="winning trades").render(),
            BacktestKpiCard(title="Profit Factor", value=metrics.get("profit_factor", "0"), subtitle="risk/reward").render(),
            BacktestKpiCard(title="Sharpe Ratio", value=metrics.get("sharpe_ratio", "0"), subtitle="risk-adjusted").render(),
            BacktestKpiCard(title="Maximum Drawdown", value=metrics.get("max_drawdown", "0%"), subtitle="drawdown").render(),
            BacktestKpiCard(title="Total Trades", value=str(metrics.get("total_trades", 0)), subtitle="executed").render(),
            "",
            BacktestChartCard(title="Equity Curve", points=charts.get("equity_curve", [])).render(),
            BacktestChartCard(title="Drawdown Curve", points=charts.get("drawdown_curve", [])).render(),
            BacktestChartCard(title="Monthly Returns", points=charts.get("monthly_returns", [])).render(),
            BacktestChartCard(title="Win/Loss Distribution", points=charts.get("win_loss_distribution", [])).render(),
            "",
            Card(title="Best Trades", body=[f"{item['symbol']}: {item['return']}" for item in best_trades]).render(),
            "",
            Card(title="Worst Trades", body=[f"{item['symbol']}: {item['return']}" for item in worst_trades]).render(),
            "",
            Card(title="Trade Statistics", body=[f"{item['metric']}: {item['value']}" for item in trade_statistics]).render(),
            "",
            BacktestStatsTable(headers=["Metric", "Value"], rows=[[item["metric"], item["value"]] for item in trade_statistics]).render(),
            "",
            BacktestTradeList(rows=[[item["symbol"], item["side"], item["entry"], item["exit"], item["pnl"]] for item in trade_list]).render(),
            "",
            Card(title="Backtest Events", body=[f"{item['event']}: {item['status']}" for item in events]).render(),
            "",
            self.build_status_bar(container=self._resolve_container()),
            "",
        ]

        return "\n".join(lines).rstrip()

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "backtesting"
        items = ["Dashboard", "Backtesting"]
        if current_route and current_route != "backtesting":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
