"""Paper Trading workspace page for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

from dashboard.layout import render_desktop_layout
from dashboard.layout import render_kpi_card
from dashboard.layout import render_panel_header
from dashboard.layout import render_section
from dashboard.layout import render_table
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.workspace.base import WorkspacePage

from .data_provider import PaperTradingDataProvider


class PaperTradingPage(WorkspacePage):
    """Render the paper-trading workspace."""

    def __init__(self, data_provider: PaperTradingDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Paper Trading", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        if self.data_provider is not None:
            if __import__("streamlit").button("Refresh Portfolio", use_container_width=True):
                self.data = self.data_provider.refresh()
            else:
                self.data = self.data_provider.get_paper_trading_data()
        else:
            self.data = {
                "summary": {},
                "open_positions": [],
                "closed_trades": [],
                "statistics": {},
            }

        summary = self.data.get("summary", {})
        open_positions = self.data.get("open_positions", [])
        closed_trades = self.data.get("closed_trades", [])
        statistics = self.data.get("statistics", {})

        render_desktop_layout()
        render_panel_header("PAPER TRADING WORKSPACE", status="in-memory")
        self._render_summary(summary)
        render_section("Open Positions", lambda: self._render_open_positions(open_positions))
        render_section("Closed Trades", lambda: self._render_closed_trades(closed_trades))
        render_section("Portfolio Statistics", lambda: self._render_statistics(statistics))

        return (
            "PAPER TRADING WORKSPACE Dashboard / Paper Trading "
            "Portfolio Summary Open Positions Closed Trades Portfolio Statistics"
        )

    def _render_summary(self, summary: dict[str, Any]) -> None:
        __import__("streamlit").subheader("Portfolio Summary")
        items = [
            ("Current Equity", self._currency(summary.get("current_equity", summary.get("portfolio_value", 0.0)))),
            ("Cash", self._currency(summary.get("cash", 0.0))),
            ("Buying Power", self._currency(summary.get("buying_power", 0.0))),
            ("Exposure", self._currency(summary.get("current_exposure", 0.0))),
            ("Realised P/L", self._currency(summary.get("realised_pnl", 0.0))),
            ("Unrealised P/L", self._currency(summary.get("unrealised_pnl", 0.0))),
            ("Total P/L", self._currency(summary.get("total_pnl", 0.0))),
            ("Open Positions", self._stringify(summary.get("open_positions", 0))),
        ]
        columns = 3
        for start in range(0, len(items), columns):
            cols = __import__("streamlit").columns(columns, gap="small")
            for col, (title, value) in zip(cols, items[start : start + columns]):
                with col:
                    render_kpi_card(title=title, value=value, footer_label="Account", footer_value="Paper")

    def _render_open_positions(self, positions: list[dict[str, Any]]) -> None:
        streamlit = __import__("streamlit")
        if positions and self.data_provider is not None:
            close_cols = streamlit.columns([2, 2, 2, 1], gap="small")
            option_map = {
                f"{self._stringify(item.get('position_id', 'N/A'))} | {self._stringify(item.get('symbol', 'N/A'))}": self._stringify(
                    item.get("position_id", "")
                )
                for item in positions
            }
            options = list(option_map.keys())
            with close_cols[0]:
                selected_option = streamlit.selectbox("Close Position", options=options, key="paper_close_position")
            with close_cols[1]:
                close_reason = streamlit.selectbox(
                    "Exit Type",
                    options=["MANUAL_EXIT", "END_OF_SESSION", "END_OF_TEST"],
                    key="paper_close_reason",
                )
            with close_cols[2]:
                close_explanation = streamlit.text_input(
                    "Explanation",
                    value="Manual user-requested close.",
                    key="paper_close_explanation",
                )
            with close_cols[3]:
                streamlit.write("")
                if streamlit.button("Close Position", use_container_width=True):
                    selected_position_id = option_map.get(selected_option, "")
                    self.data = self.data_provider.close_position(
                        selected_position_id,
                        reason=close_reason,
                        explanation=close_explanation,
                    )
                    positions = self.data.get("open_positions", [])

        rows = [
            {
                "Symbol": self._stringify(item.get("symbol", "N/A")),
                "Strategy": self._stringify(item.get("strategy_name", item.get("strategy_id", "N/A"))),
                "Direction": self._stringify(item.get("direction", "N/A")),
                "Quantity": self._stringify(item.get("quantity", 0)),
                "Entry Price": self._currency(item.get("entry_price", 0.0)),
                "Current Price": self._currency(item.get("current_price", 0.0)),
                "Today's Change": self._currency(item.get("todays_change", 0.0)),
                "Market Value": self._currency(item.get("market_value", 0.0)),
                "Unrealised P/L": self._currency(item.get("unrealised_pnl", 0.0)),
                "Unrealised P/L %": self._percent(item.get("unrealised_pnl_percent", 0.0)),
                "Days Open": self._stringify(item.get("days_open", 0)),
                "Distance to Stop": self._currency(item.get("distance_to_stop_loss", 0.0)),
                "Distance to Target": self._currency(item.get("distance_to_target", 0.0)),
                "Last Updated": self._stringify(item.get("last_updated", "N/A")),
                "Status": self._stringify(item.get("status", "N/A")),
                "Price Status": self._stringify(item.get("price_status", "LIVE")),
            }
            for item in positions
        ]
        render_table(
            rows=rows,
            columns=[
                "Symbol",
                "Strategy",
                "Direction",
                "Quantity",
                "Entry Price",
                "Current Price",
                "Today's Change",
                "Market Value",
                "Unrealised P/L",
                "Unrealised P/L %",
                "Days Open",
                "Distance to Stop",
                "Distance to Target",
                "Last Updated",
                "Status",
                "Price Status",
            ],
        )

    def _render_closed_trades(self, trades: list[dict[str, Any]]) -> None:
        rows = [
            {
                "Trade ID": self._stringify(item.get("trade_id", "N/A")),
                "Position ID": self._stringify(item.get("position_id", "N/A")),
                "Decision ID": self._stringify(item.get("decision_id", "N/A")),
                "Strategy ID": self._stringify(item.get("strategy_id", "N/A")),
                "Symbol": self._stringify(item.get("symbol", "N/A")),
                "Strategy": self._stringify(item.get("strategy_name", item.get("strategy", "N/A"))),
                "Direction": self._stringify(item.get("direction", "N/A")),
                "Entry Date": self._stringify(item.get("entry_date", "N/A")),
                "Exit Date": self._stringify(item.get("exit_date", "N/A")),
                "Entry": self._currency(item.get("entry_price", 0.0)),
                "Exit": self._currency(item.get("exit_price", 0.0)),
                "Quantity": self._stringify(item.get("quantity", 0)),
                "Gross Profit": self._currency(item.get("gross_profit", 0.0)),
                "Commission": self._currency(item.get("commission", 0.0)),
                "Spread Cost": self._currency(item.get("spread_cost", 0.0)),
                "Slippage Cost": self._currency(item.get("slippage_cost", 0.0)),
                "Costs": self._currency(item.get("costs", 0.0)),
                "Net Profit": self._currency(item.get("net_profit", 0.0)),
                "Reason": self._stringify(item.get("exit_reason", "N/A")),
                "Exit Explanation": self._stringify(item.get("exit_explanation", "N/A")),
                "Holding Period": self._stringify(item.get("holding_period", item.get("holding_period_days", 0))),
            }
            for item in trades
        ]
        render_table(
            rows=rows,
            columns=[
                "Trade ID",
                "Position ID",
                "Decision ID",
                "Strategy ID",
                "Symbol",
                "Strategy",
                "Direction",
                "Entry Date",
                "Exit Date",
                "Entry",
                "Exit",
                "Quantity",
                "Gross Profit",
                "Commission",
                "Spread Cost",
                "Slippage Cost",
                "Costs",
                "Net Profit",
                "Reason",
                "Exit Explanation",
                "Holding Period",
            ],
        )

    def _render_statistics(self, statistics: dict[str, Any]) -> None:
        rows = [
            {"Metric": "Total Trades", "Value": self._stringify(statistics.get("total_trades", 0))},
            {"Metric": "Winning Trades", "Value": self._stringify(statistics.get("winning_trades", 0))},
            {"Metric": "Losing Trades", "Value": self._stringify(statistics.get("losing_trades", 0))},
            {"Metric": "Win Rate", "Value": self._percent(statistics.get("win_rate", 0.0))},
            {"Metric": "Average Winner", "Value": self._currency(statistics.get("average_winner", 0.0))},
            {"Metric": "Average Loser", "Value": self._currency(statistics.get("average_loser", 0.0))},
            {"Metric": "Largest Winner", "Value": self._currency(statistics.get("largest_winner", 0.0))},
            {"Metric": "Largest Loser", "Value": self._currency(statistics.get("largest_loser", 0.0))},
            {"Metric": "Current Exposure", "Value": self._currency(statistics.get("current_exposure", 0.0))},
            {"Metric": "Cash Allocation", "Value": self._percent(statistics.get("cash_allocation", 0.0))},
            {"Metric": "Invested Allocation", "Value": self._percent(statistics.get("invested_allocation", 0.0))},
            {"Metric": "Portfolio Return", "Value": self._percent(statistics.get("portfolio_return_percent", 0.0))},
            {"Metric": "Average Position Size", "Value": self._currency(statistics.get("average_position_size", 0.0))},
            {"Metric": "Largest Position", "Value": self._currency(statistics.get("largest_position", 0.0))},
            {"Metric": "Smallest Position", "Value": self._currency(statistics.get("smallest_position", 0.0))},
        ]
        render_table(rows=rows, columns=["Metric", "Value"])

    def refresh(self) -> str:
        if self.data_provider is not None:
            self.data = self.data_provider.refresh()
        return self.render()

    def _currency(self, value: Any) -> str:
        try:
            return f"£{float(value):,.2f}"
        except (TypeError, ValueError):
            return self._stringify(value)

    def _percent(self, value: Any) -> str:
        try:
            return f"{float(value):.2f}%"
        except (TypeError, ValueError):
            return self._stringify(value)

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        return str(value)