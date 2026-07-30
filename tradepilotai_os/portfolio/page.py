"""Portfolio dashboard page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.ui_library import (
    Breadcrumb,
    Card,
    DataTable,
    KPIChartCard,
    SectionHeader,
    StatusBadge,
    StatusBar,
    Toolbar,
)


class PortfolioPage:
    """Render the portfolio dashboard with reusable panels and tables."""

    def __init__(self, portfolio_service: Any | None = None, navigation_service: NavigationService | None = None) -> None:
        self.portfolio_service = portfolio_service
        self.navigation_service = navigation_service or NavigationService()

    def render(self) -> str:
        """Render the portfolio dashboard to a string."""

        summary = self._build_summary()
        positions = self._build_positions()

        lines = [
            "",
            "=" * 80,
            "PORTFOLIO DASHBOARD",
            "=" * 80,
            "",
            SectionHeader(title="Portfolio Overview", subtitle="Shared component layout").render(),
            "",
            Toolbar(title="Portfolio Controls", actions=["Rebalance", "Export"]).render(),
            "",
            self._build_breadcrumbs(),
            "",
            StatusBadge(label="Allocation", status="balanced").render(),
            "",
            Card(title="Summary", body=[
                f"Portfolio Value: {summary['portfolio_value']}",
                f"Cash: {summary['cash']}",
                f"Buying Power: {summary['buying_power']}",
                f"Today's Profit/Loss: {summary['today_pnl']}",
                f"Total Return: {summary['total_return']}",
                f"Unrealised Profit/Loss: {summary['unrealised_pnl']}",
                f"Realised Profit/Loss: {summary['realised_pnl']}",
            ]).render(),
            "",
            KPIChartCard(title="Performance", value=summary["total_return"], subtitle="month to date").render(),
            "",
            "Portfolio Allocation",
            "Sector Allocation",
            "Portfolio Growth",
            "Monthly Returns",
            "",
            SectionHeader(title="Open Positions").render(),
        ]

        if positions:
            lines.append(
                DataTable(
                    headers=["Symbol", "Qty", "Entry", "Current"],
                    rows=positions,
                ).render()
            )
        else:
            lines.append("No open positions")

        lines.extend([
            "",
            StatusBar(container=self._resolve_container(), version="1.0.0").render(),
        ])

        return "\n".join(lines)

    def _build_breadcrumbs(self) -> str:
        current_route = self.navigation_service.current_route() or "portfolio"
        items = ["Dashboard", "Portfolio"]
        if current_route and current_route != "portfolio":
            items.append(current_route)
        return Breadcrumb(items=items).render()

    def _resolve_container(self) -> Any | None:
        if self.portfolio_service is None:
            return None
        return getattr(self.portfolio_service, "container", None)

    def _build_summary(self) -> dict[str, str]:
        if self.portfolio_service is None or getattr(self.portfolio_service, "state", None) is None:
            return {
                "portfolio_value": "$0.00",
                "cash": "$0.00",
                "buying_power": "$0.00",
                "today_pnl": "$0.00",
                "total_return": "0.00%",
                "unrealised_pnl": "$0.00",
                "realised_pnl": "$0.00",
            }

        state = self.portfolio_service.state
        portfolio_value = getattr(state, "cash", 0.0) + getattr(state, "unrealised_pnl", 0.0)
        return {
            "portfolio_value": self._format_currency(portfolio_value),
            "cash": self._format_currency(getattr(state, "cash", 0.0)),
            "buying_power": self._format_currency(getattr(state, "buying_power", 0.0)),
            "today_pnl": self._format_currency(getattr(state, "today_pnl", 0.0)),
            "total_return": self._format_percentage(getattr(state, "total_return", 0.0)),
            "unrealised_pnl": self._format_currency(getattr(state, "unrealised_pnl", 0.0)),
            "realised_pnl": self._format_currency(getattr(state, "realised_pnl", 0.0)),
        }

    def _build_positions(self) -> list[list[Any]]:
        if self.portfolio_service is None or getattr(self.portfolio_service, "state", None) is None:
            return []

        state = self.portfolio_service.state
        positions = getattr(state, "positions", {}) or {}
        rows: list[list[Any]] = []
        for symbol, position in positions.items():
            rows.append(
                [
                    symbol,
                    getattr(position, "quantity", 0),
                    getattr(position, "average_price", 0.0),
                    getattr(position, "market_price", 0.0),
                ]
            )
        return rows

    def _format_currency(self, value: float) -> str:
        return f"${float(value):,.2f}"

    def _format_percentage(self, value: float) -> str:
        return f"{float(value) * 100:.2f}%"
