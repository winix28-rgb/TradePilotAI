"""Backtesting dashboard page for the TradePilotAI OS."""

from __future__ import annotations

from html import escape
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.layout import (
    render_desktop_layout,
    empty_state,
    render_panel_header,
    render_section,
    render_table,
)

from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.workspace import WorkspacePage

from .data_provider import BacktestingDataProvider


class BacktestingPage(WorkspacePage):
    """Render a professional backtesting dashboard using shared UI components."""

    def __init__(self, data_provider: BacktestingDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Backtesting", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}
        self._run_request: dict[str, Any] | None = None
        self._comparison_run_request: dict[str, Any] | None = None
        self._selected_strategy_definition: dict[str, Any] | None = None

    def render(self) -> str:
        """Render the backtesting workspace using shared Streamlit components."""
        self._apply_backtesting_styles()

        if self.data_provider is None:
            self.data_provider = BacktestingDataProvider(state=st.session_state)

        self.data = self.data_provider.get_backtest_data()

        configuration = self.data.get("configuration", {})
        strategy_definitions = self._strategy_definitions()
        metrics = self.data.get("metrics", {})
        charts = self.data.get("charts", {})
        breakdown = self.data.get("performance_breakdown", {})
        trade_history = self.data.get("trade_history", [])
        signal_explainability = self.data.get("signal_explainability", [])
        status = self.data.get("backtest_status", {})
        progress = self.data.get("progress", {})
        comparison = self.data.get("comparison", {})

        render_desktop_layout()
        render_panel_header("BACKTESTING WORKSPACE", status=self._stringify(self.data.get("summary", {}).get("status", "pending")))

        backtest_tab, comparison_tab = st.tabs(["Backtest", "Comparison"])

        with backtest_tab:
            render_section("Strategy Configuration", lambda: self._render_strategy_configuration(configuration, strategy_definitions))
            render_section("Strategy Information", lambda: self._render_strategy_information(self._selected_strategy_definition))

            if self._run_request is not None and self.data_provider is not None:
                self.data_provider.run_backtest(self._run_request)
                self._run_request = None
                self.data = self.data_provider.get_backtest_data()
                metrics = self.data.get("metrics", {})
                charts = self.data.get("charts", {})
                breakdown = self.data.get("performance_breakdown", {})
                trade_history = self.data.get("trade_history", [])
                signal_explainability = self.data.get("signal_explainability", [])
                status = self.data.get("backtest_status", {})
                progress = self.data.get("progress", {})

            render_section("Backtest Status", lambda: self._render_backtest_status(status))
            render_section("Progress Panel", lambda: self._render_progress_panel(progress))
            render_section("Summary KPIs", lambda: self._render_summary_kpis(metrics))
            render_section("Equity Curve", lambda: self._render_equity_curve(charts.get("equity_curve", [])))
            render_section("Drawdown Curve", lambda: self._render_drawdown_curve(charts.get("drawdown_curve", [])))
            render_section("Monthly Returns + Exit Reasons", lambda: self._render_performance_breakdown(breakdown, charts))
            render_section("Trade History", lambda: self._render_trade_history(trade_history))
            render_section("Signal Explainability", lambda: self._render_signal_explainability(signal_explainability))

        with comparison_tab:
            render_section("Comparison Configuration", lambda: self._render_strategy_comparison_configuration(configuration, strategy_definitions))

            if self._comparison_run_request is not None and self.data_provider is not None:
                self.data_provider.run_strategy_comparison(self._comparison_run_request)
                self._comparison_run_request = None
                self.data = self.data_provider.get_backtest_data()
                comparison = self.data.get("comparison", {})

            render_section("Comparison Summary", lambda: self._render_strategy_comparison_summary(comparison))
            render_section("Comparison Table", lambda: self._render_strategy_comparison_table(comparison.get("table", [])))
            render_section("Equity Curve Overlay", lambda: self._render_equity_comparison_curve(comparison.get("charts", {}).get("equity_curve", [])))
            render_section("Drawdown Comparison", lambda: self._render_drawdown_comparison_curve(comparison.get("charts", {}).get("drawdown_curve", [])))
            render_section("Monthly Returns Comparison", lambda: self._render_monthly_returns_comparison(comparison.get("charts", {}).get("monthly_returns", [])))
            render_section("Trade Count Comparison", lambda: self._render_trade_count_comparison(comparison.get("charts", {}).get("trade_counts", [])))

        # Return a compact route key so callers can detect successful rendering
        # without leaking internal UI labels as visible page text.
        return "backtesting"

    def _render_strategy_configuration(self, configuration: dict[str, Any], strategy_definitions: list[dict[str, Any]]) -> None:
        strategy_lookup = {item.get("strategy_id"): item for item in strategy_definitions}
        selected_strategy_id = self._stringify(configuration.get("strategy_id", "rsi_mean_reversion"))
        if selected_strategy_id not in strategy_lookup and strategy_definitions:
            selected_strategy_id = self._stringify(strategy_definitions[0].get("strategy_id", "rsi_mean_reversion"))

        strategy_label_map = {
            self._stringify(item.get("name", item.get("strategy_id", ""))): self._stringify(item.get("strategy_id", ""))
            for item in strategy_definitions
        }
        selected_label = next((label for label, sid in strategy_label_map.items() if sid == selected_strategy_id), None)
        if selected_label is None and strategy_label_map:
            selected_label = next(iter(strategy_label_map.keys()))

        date_col, capital_col, cost_col, run_col = st.columns([2.0, 1.0, 2.4, 1.0], gap="small")
        with date_col:
            st.caption("Strategy")
            selected_label = st.selectbox(
                "Strategy",
                options=list(strategy_label_map.keys()) or ["RSI Mean Reversion"],
                index=(list(strategy_label_map.keys()).index(selected_label) if selected_label in strategy_label_map else 0),
                key="backtest_strategy_id",
                label_visibility="collapsed",
            )
            selected_strategy_id = strategy_label_map.get(selected_label, selected_strategy_id)
            selected_definition = strategy_lookup.get(selected_strategy_id)
            self._selected_strategy_definition = selected_definition
            recommended_timeframe = self._stringify(
                configuration.get(
                    "strategy_primary_timeframe",
                    selected_definition.get("primary_timeframe", "1h") if selected_definition else "1h",
                )
            )

            symbols = st.text_input(
                "Symbols",
                value=self._stringify(configuration.get("symbols", "AAPL,TSLA")),
                key="backtest_symbols",
                label_visibility="collapsed",
            )
            st.caption("Date Range")
            date_range = st.text_input(
                "Date Range",
                value=self._stringify(configuration.get("date_range", "2024-01-01 to 2024-12-31")),
                key="backtest_date_range",
                label_visibility="collapsed",
            )

            st.caption(f"Recommended Timeframe: {recommended_timeframe}")
            current_timeframe = st.text_input(
                "Current Timeframe",
                value=self._stringify(configuration.get("current_timeframe", recommended_timeframe)),
                key="backtest_timeframe",
                label_visibility="collapsed",
            )
            st.caption(f"Current Timeframe: {current_timeframe}")
            if current_timeframe and recommended_timeframe and current_timeframe != recommended_timeframe:
                st.warning("⚠ Strategy is being run outside its recommended timeframe.")

            if selected_definition is not None:
                st.caption(self._stringify(selected_definition.get("description", "")))
                indicators = selected_definition.get("indicators", [])
                if isinstance(indicators, list) and indicators:
                    st.caption(f"Indicators: {', '.join(str(item) for item in indicators)}")
        with capital_col:
            st.caption("Capital")
            capital = st.text_input(
                "Capital",
                value=self._stringify(configuration.get("capital", "$100,000")),
                key="backtest_capital",
                label_visibility="collapsed",
            )
        with cost_col:
            commission_col, spread_col, slippage_col = st.columns(3, gap="small")
            with commission_col:
                st.caption("Commission")
                commission = st.text_input(
                    "Commission",
                    value=self._stringify(configuration.get("commission", "0.05%")),
                    key="backtest_commission",
                    label_visibility="collapsed",
                )
            with spread_col:
                st.caption("Spread")
                spread = st.text_input(
                    "Spread",
                    value=self._stringify(configuration.get("spread", "0.02")),
                    key="backtest_spread",
                    label_visibility="collapsed",
                )
            with slippage_col:
                st.caption("Slippage")
                slippage = st.text_input(
                    "Slippage",
                    value=self._stringify(configuration.get("slippage", "0.01")),
                    key="backtest_slippage",
                    label_visibility="collapsed",
                )
        with run_col:
            st.caption(" ")
            run_requested = st.button("Run Backtest", use_container_width=True, key="run_backtest_button")

        strategy_params = self._render_strategy_parameters(
            selected_strategy_id=selected_strategy_id,
            selected_definition=strategy_lookup.get(selected_strategy_id),
            existing_parameters=configuration.get("strategy_parameters", {}),
        )

        if run_requested:
            self._run_request = {
                "symbols": symbols,
                "date_range": date_range,
                "capital": capital,
                "commission": commission,
                "spread": spread,
                "slippage": slippage,
                "strategy_id": selected_strategy_id,
                "timeframe": current_timeframe,
                "strategy_parameters": strategy_params,
            }

    def _render_strategy_comparison_configuration(self, configuration: dict[str, Any], strategy_definitions: list[dict[str, Any]]) -> None:
        strategy_lookup = {item.get("strategy_id"): item for item in strategy_definitions}
        label_lookup = {
            self._stringify(item.get("name", item.get("strategy_id", ""))): self._stringify(item.get("strategy_id", ""))
            for item in strategy_definitions
        }

        default_labels = list(label_lookup.keys())[: min(3, len(label_lookup))] or ["RSI Mean Reversion"]
        selected_labels = st.multiselect(
            "Strategies",
            options=list(label_lookup.keys()) or ["RSI Mean Reversion"],
            default=default_labels,
            key="backtest_comparison_strategy_ids",
            help="Select multiple strategies to compare on the same market data.",
        )
        selected_strategy_ids = [label_lookup.get(label) for label in selected_labels if label_lookup.get(label)]
        if not selected_strategy_ids and strategy_definitions:
            selected_strategy_ids = [self._stringify(strategy_definitions[0].get("strategy_id", "rsi_mean_reversion"))]

        selected_timeframes = sorted({self._stringify(strategy_lookup.get(strategy_id, {}).get("primary_timeframe", "")) for strategy_id in selected_strategy_ids if strategy_id})
        if len([item for item in selected_timeframes if item]) > 1:
            st.warning("Selected strategies use different recommended timeframes.")

        date_col, capital_col, cost_col, run_col = st.columns([2.0, 1.0, 2.4, 1.0], gap="small")
        with date_col:
            st.caption("Symbols")
            symbols = st.text_input(
                "Symbols",
                value=self._stringify(configuration.get("symbols", "AAPL,TSLA")),
                key="backtest_comparison_symbols",
                label_visibility="collapsed",
            )
            st.caption("Date Range")
            date_range = st.text_input(
                "Date Range",
                value=self._stringify(configuration.get("date_range", "2024-01-01 to 2024-12-31")),
                key="backtest_comparison_date_range",
                label_visibility="collapsed",
            )
        with capital_col:
            st.caption("Capital")
            capital = st.text_input(
                "Capital",
                value=self._stringify(configuration.get("capital", "$100,000")),
                key="backtest_comparison_capital",
                label_visibility="collapsed",
            )
        with cost_col:
            commission_col, spread_col, slippage_col = st.columns(3, gap="small")
            with commission_col:
                st.caption("Commission")
                commission = st.text_input(
                    "Commission",
                    value=self._stringify(configuration.get("commission", "0.05%")),
                    key="backtest_comparison_commission",
                    label_visibility="collapsed",
                )
            with spread_col:
                st.caption("Spread")
                spread = st.text_input(
                    "Spread",
                    value=self._stringify(configuration.get("spread", "0.02")),
                    key="backtest_comparison_spread",
                    label_visibility="collapsed",
                )
            with slippage_col:
                st.caption("Slippage")
                slippage = st.text_input(
                    "Slippage",
                    value=self._stringify(configuration.get("slippage", "0.01")),
                    key="backtest_comparison_slippage",
                    label_visibility="collapsed",
                )
        with run_col:
            st.caption(" ")
            run_requested = st.button("Run Comparison", use_container_width=True, key="run_comparison_button")

        if run_requested:
            self._comparison_run_request = {
                "symbols": symbols,
                "date_range": date_range,
                "capital": capital,
                "commission": commission,
                "spread": spread,
                "slippage": slippage,
                "strategy_ids": selected_strategy_ids,
            }

        if selected_strategy_ids:
            selected_names = [self._stringify(strategy_lookup.get(strategy_id, {}).get("name", strategy_id)) for strategy_id in selected_strategy_ids]
            st.caption(f"Selected: {', '.join(selected_names)}")

    def _render_strategy_comparison_summary(self, comparison: dict[str, Any]) -> None:
        summary = comparison.get("summary", {}) if isinstance(comparison, dict) else {}
        configuration = comparison.get("configuration", {}) if isinstance(comparison, dict) else {}
        rows = [
            {"Field": "Status", "Value": self._stringify(summary.get("status", "pending"))},
            {"Field": "Strategies", "Value": self._stringify(summary.get("strategy_count", 0))},
            {"Field": "Requested Symbols", "Value": ", ".join(configuration.get("requested_symbols", [])) or "N/A"},
            {"Field": "Loaded Symbols", "Value": ", ".join(configuration.get("loaded_symbols", [])) or "N/A"},
            {"Field": "Failed Symbols", "Value": ", ".join(configuration.get("failed_symbols", {}).keys()) or "N/A"},
            {"Field": "Recommended Timeframes", "Value": ", ".join(configuration.get("recommended_timeframes", [])) or "N/A"},
            {"Field": "Timeframe Warning", "Value": "Yes" if configuration.get("timeframe_warning") else "No"},
        ]
        render_table(rows=rows, columns=["Field", "Value"])

    def _render_strategy_comparison_table(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            empty_state("No comparison results available")
            return

        table_rows = []
        for row in rows:
            table_rows.append(
                {
                    "Strategy": self._stringify(row.get("strategy_name", row.get("strategy_id", "N/A"))),
                    "Net Profit": self._format_currency(row.get("net_profit", 0.0)),
                    "Return %": self._format_percent(row.get("total_return", 0.0)),
                    "Win Rate": self._format_percent(row.get("win_rate", 0.0), already_percent=True),
                    "Profit Factor": self._format_number(row.get("profit_factor", 0.0), decimals=2),
                    "Max Drawdown": self._format_percent(row.get("maximum_drawdown", 0.0), already_percent=True),
                    "Expectancy": self._format_currency(row.get("expectancy", 0.0)),
                    "Trades": self._stringify(row.get("total_trades", 0)),
                    "Wins": self._stringify(row.get("winning_trades", 0)),
                    "Losses": self._stringify(row.get("losing_trades", 0)),
                }
            )

        render_table(
            rows=table_rows,
            columns=["Strategy", "Net Profit", "Return %", "Win Rate", "Profit Factor", "Max Drawdown", "Expectancy", "Trades", "Wins", "Losses"],
        )

    def _render_equity_comparison_curve(self, points: Any) -> None:
        frame = self._comparison_points_to_dataframe(points)
        if frame.empty:
            empty_state("No equity comparison data available")
            return

        chart = (
            alt.Chart(frame)
            .mark_line(strokeWidth=2.5, point=True)
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Value:Q", title="Equity"),
                color=alt.Color("Strategy:N", title="Strategy"),
                tooltip=[
                    alt.Tooltip("Strategy:N", title="Strategy"),
                    alt.Tooltip("Date:T", title="Date"),
                    alt.Tooltip("Value:Q", title="Equity", format=",.2f"),
                ],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

    def _render_drawdown_comparison_curve(self, points: Any) -> None:
        frame = self._comparison_points_to_dataframe(points)
        if frame.empty:
            empty_state("No drawdown comparison data available")
            return

        chart = (
            alt.Chart(frame)
            .mark_line(strokeWidth=2.5)
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Value:Q", title="Drawdown %"),
                color=alt.Color("Strategy:N", title="Strategy"),
                tooltip=[
                    alt.Tooltip("Strategy:N", title="Strategy"),
                    alt.Tooltip("Date:T", title="Date"),
                    alt.Tooltip("Value:Q", title="Drawdown", format=",.2f"),
                ],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

    def _render_monthly_returns_comparison(self, points: Any) -> None:
        frame = self._comparison_monthly_dataframe(points)
        if frame.empty:
            empty_state("No monthly comparison data available")
            return

        chart = (
            alt.Chart(frame)
            .mark_line(point=True, strokeWidth=2.5)
            .encode(
                x=alt.X("Month:N", title="Month", sort=None),
                y=alt.Y("Value:Q", title="Monthly Return %"),
                color=alt.Color("Strategy:N", title="Strategy"),
                tooltip=[
                    alt.Tooltip("Strategy:N", title="Strategy"),
                    alt.Tooltip("Month:N", title="Month"),
                    alt.Tooltip("Value:Q", title="Return", format=",.2f"),
                ],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

    def _render_trade_count_comparison(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            empty_state("No trade count comparison data available")
            return

        table_rows = []
        chart_rows = []
        for row in rows:
            strategy = self._stringify(row.get("strategy_name", row.get("strategy_id", "N/A")))
            total = int(self._to_float(row.get("total_trades", 0)))
            wins = int(self._to_float(row.get("winning_trades", 0)))
            losses = int(self._to_float(row.get("losing_trades", 0)))
            table_rows.append(
                {
                    "Strategy": strategy,
                    "Total Trades": self._stringify(total),
                    "Winning Trades": self._stringify(wins),
                    "Losing Trades": self._stringify(losses),
                }
            )
            chart_rows.extend(
                [
                    {"Strategy": strategy, "Type": "Total", "Count": total},
                    {"Strategy": strategy, "Type": "Wins", "Count": wins},
                    {"Strategy": strategy, "Type": "Losses", "Count": losses},
                ]
            )

        render_table(rows=table_rows, columns=["Strategy", "Total Trades", "Winning Trades", "Losing Trades"])

        frame = pd.DataFrame(chart_rows)
        if frame.empty:
            return

        chart = (
            alt.Chart(frame)
            .mark_bar()
            .encode(
                x=alt.X("Strategy:N", title="Strategy"),
                y=alt.Y("Count:Q", title="Trade Count"),
                color=alt.Color("Type:N", title="Trade Type"),
                tooltip=[
                    alt.Tooltip("Strategy:N", title="Strategy"),
                    alt.Tooltip("Type:N", title="Type"),
                    alt.Tooltip("Count:Q", title="Count", format=",.0f"),
                ],
            )
            .properties(height=280)
        )
        st.altair_chart(chart, use_container_width=True)

    def _render_strategy_information(self, strategy_definition: dict[str, Any] | None) -> None:
        if not isinstance(strategy_definition, dict):
            empty_state("No strategy information available")
            return

        row = {
            "Name": self._stringify(strategy_definition.get("name", "N/A")),
            "Asset Class": self._stringify(strategy_definition.get("asset_class", "N/A")),
            "Primary Timeframe": self._stringify(strategy_definition.get("primary_timeframe", "N/A")),
            "Category": self._stringify(strategy_definition.get("category", "N/A")),
            "Version": self._stringify(strategy_definition.get("version", "N/A")),
            "Author": self._stringify(strategy_definition.get("author", "N/A")),
            "Supported Assets": ", ".join(strategy_definition.get("supported_assets", [])) or "N/A",
            "Supported Timeframes": ", ".join(strategy_definition.get("supported_timeframes", [])) or "N/A",
            "Supports Long": "Yes" if bool(strategy_definition.get("supports_long", False)) else "No",
            "Supports Short": "Yes" if bool(strategy_definition.get("supports_short", False)) else "No",
            "Risk Profile": self._stringify(strategy_definition.get("risk_profile", "N/A")),
            "Best Market": self._stringify(strategy_definition.get("best_market", "N/A")),
            "Best Timeframes": ", ".join(strategy_definition.get("best_timeframes", [])) or "N/A",
            "Strengths": " | ".join(strategy_definition.get("strengths", [])) or "N/A",
            "Weaknesses": " | ".join(strategy_definition.get("weaknesses", [])) or "N/A",
            "Recommended Risk": self._stringify(strategy_definition.get("recommended_risk", "N/A")),
        }
        rows = [{"Field": key, "Value": value} for key, value in row.items()]
        render_table(rows=rows, columns=["Field", "Value"])

    def _strategy_definitions(self) -> list[dict[str, Any]]:
        if self.data_provider is None:
            return []
        service = getattr(self.data_provider, "service", None)
        if service is None or not hasattr(service, "get_strategy_definitions"):
            return []
        definitions = service.get_strategy_definitions()
        if not isinstance(definitions, list):
            return []
        return definitions

    def _render_strategy_parameters(
        self,
        *,
        selected_strategy_id: str,
        selected_definition: dict[str, Any] | None,
        existing_parameters: Any,
    ) -> dict[str, Any]:
        if selected_definition is None:
            return {}

        parameters = selected_definition.get("parameters", [])
        if not isinstance(parameters, list) or not parameters:
            return {}

        initial_values = existing_parameters if isinstance(existing_parameters, dict) else {}
        cols = st.columns(min(4, max(1, len(parameters))), gap="small")

        resolved: dict[str, Any] = {}
        for index, parameter in enumerate(parameters):
            if not isinstance(parameter, dict):
                continue
            with cols[index % len(cols)]:
                key = self._stringify(parameter.get("key", f"param_{index}"))
                label = self._stringify(parameter.get("label", key))
                param_type = self._stringify(parameter.get("type", "str")).lower()
                default = initial_values.get(key, parameter.get("default"))
                control_key = f"backtest_param_{selected_strategy_id}_{key}"

                if param_type == "bool":
                    value = st.checkbox(label, value=bool(default), key=control_key)
                elif param_type == "int":
                    value = st.number_input(
                        label,
                        min_value=int(parameter.get("minimum", -1000000)),
                        max_value=int(parameter.get("maximum", 1000000)),
                        step=int(parameter.get("step", 1)),
                        value=int(default if default is not None else 0),
                        key=control_key,
                    )
                elif param_type == "float":
                    value = st.number_input(
                        label,
                        min_value=float(parameter.get("minimum", -1000000.0)),
                        max_value=float(parameter.get("maximum", 1000000.0)),
                        step=float(parameter.get("step", 0.1)),
                        value=float(default if default is not None else 0.0),
                        format="%.4f",
                        key=control_key,
                    )
                elif param_type == "choice":
                    options = parameter.get("options", [])
                    if not isinstance(options, list) or not options:
                        options = [self._stringify(default)]
                    normalized = [self._stringify(item) for item in options]
                    selected = self._stringify(default)
                    option_index = normalized.index(selected) if selected in normalized else 0
                    value = st.selectbox(label, options=normalized, index=option_index, key=control_key)
                else:
                    value = st.text_input(label, value=self._stringify(default), key=control_key)

                resolved[key] = value

                description = self._stringify(parameter.get("description", ""))
                if description and description != "N/A":
                    st.caption(description)

        return resolved

    def _render_backtest_status(self, status: dict[str, Any]) -> None:
        requested = status.get("requested_symbols", [])
        loaded = status.get("loaded_symbols", [])
        failed = status.get("failed_symbols", {})

        status_rows = [
            {"Label": "Symbols Requested", "Value": ", ".join(requested) if requested else "N/A"},
            {"Label": "Symbols Loaded", "Value": ", ".join(loaded) if loaded else "N/A"},
            {"Label": "Symbols Failed", "Value": ", ".join(failed.keys()) if failed else "N/A"},
            {"Label": "Completion Status", "Value": self._stringify(status.get("completion_status", self.data.get("summary", {}).get("status", "pending"))).replace("_", " ").title()},
        ]
        render_table(rows=status_rows, columns=["Label", "Value"])

        if failed:
            failure_rows = [{"Symbol": symbol, "Reason": reason} for symbol, reason in failed.items()]
            render_panel_header("Failed Symbols")
            render_table(rows=failure_rows, columns=["Symbol", "Reason"])

    def _render_progress_panel(self, progress: dict[str, Any]) -> None:
        current_stage = self._stringify(progress.get("current_stage", "Not started"))
        error = self._stringify(progress.get("error", ""))
        st.caption("Current Stage")
        st.write(current_stage)

        rows = []
        for stage in progress.get("stages", []):
            rows.append(
                {
                    "Stage": self._stringify(stage.get("stage", "")),
                    "Status": self._stringify(stage.get("status", "Pending")),
                }
            )
        if not rows:
            rows = [{"Stage": "No stages", "Status": "Pending"}]

        render_table(rows=rows, columns=["Stage", "Status"])
        if error:
            st.caption(f"Last Error: {error}")

    def _render_summary_kpis(self, metrics: dict[str, Any]) -> None:
        max_drawdown = metrics.get("maximum_drawdown", metrics.get("max_drawdown", 0))
        kpis = [
            {
                "title": "Net Profit",
                "value": self._format_currency(metrics.get("net_profit", 0.0)),
                "support": "P&L",
                "klass": self._semantic_signed(metrics.get("net_profit", 0.0)),
            },
            {
                "title": "Return %",
                "value": self._format_percent(metrics.get("total_return", 0.0)),
                "support": "Total Return",
                "klass": self._semantic_signed(metrics.get("total_return", 0.0)),
            },
            {
                "title": "Profit Factor",
                "value": self._format_number(metrics.get("profit_factor", 0.0), decimals=2),
                "support": "Gross Profit / Gross Loss",
                "klass": self._semantic_profit_factor(metrics.get("profit_factor", 0.0)),
            },
            {
                "title": "Win Rate",
                "value": self._format_percent(metrics.get("win_rate", 0.0), already_percent=True),
                "support": "Winning Trades",
                "klass": self._semantic_win_rate(metrics.get("win_rate", 0.0)),
            },
            {
                "title": "Max Drawdown",
                "value": self._format_percent(max_drawdown, already_percent=True),
                "support": "Peak-to-Trough",
                "klass": self._semantic_drawdown(max_drawdown),
            },
            {
                "title": "Expectancy",
                "value": self._format_currency(metrics.get("expectancy", 0.0)),
                "support": "Expected P/L Per Trade",
                "klass": self._semantic_signed(metrics.get("expectancy", 0.0)),
            },
        ]

        cols = st.columns(6, gap="small")
        for col, item in zip(cols, kpis):
            with col:
                st.markdown(
                    (
                        f"<div class='tp-kpi-card tp-kpi-card--backtest {escape(item['klass'])}'>"
                        f"<div class='tp-kpi-title'>{escape(item['title'])}</div>"
                        f"<div class='tp-kpi-value'>{escape(item['value'])}</div>"
                        f"<div class='tp-kpi-supporting'>{escape(item['support'])}</div>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

    def _render_equity_curve(self, points: Any) -> None:
        frame = self._points_to_dataframe(points)
        if frame.empty:
            empty_state("No equity curve data available")
            return

        chart = (
            alt.Chart(frame)
            .mark_line(color="#2563EB", strokeWidth=2.8, point=True)
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Value:Q", title="Equity"),
                tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip("Value:Q", title="Equity", format=",.2f")],
            )
            .properties(height=320)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

    def _render_drawdown_curve(self, points: Any) -> None:
        frame = self._points_to_dataframe(points)
        if frame.empty:
            empty_state("No drawdown data available")
            return

        area = (
            alt.Chart(frame)
            .mark_area(color="#DC2626", opacity=0.28)
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Value:Q", title="Drawdown %"),
                tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip("Value:Q", title="Drawdown", format=",.2f")],
            )
        )
        line = area.mark_line(color="#B91C1C", strokeWidth=2)
        st.altair_chart((area + line).properties(height=280).interactive(), use_container_width=True)

    def _render_performance_breakdown(self, breakdown: dict[str, Any], charts: dict[str, Any]) -> None:
        monthly_returns = breakdown.get("monthly_returns", charts.get("monthly_returns", []))
        exit_reasons = breakdown.get(
            "exit_reasons",
            {"Stop Loss": 0, "Take Profit": 0, "Strategy Exit": 0, "End of Test": 0},
        )
        c1, c2 = st.columns(2, gap="small")
        with c1:
            render_panel_header("Monthly Returns")
            self._render_monthly_returns_chart(monthly_returns)
        with c2:
            render_panel_header("Exit Reasons")
            self._render_exit_reasons_chart(exit_reasons)

    def _render_monthly_returns_chart(self, monthly_returns: Any) -> None:
        rows: list[dict[str, Any]] = []
        if isinstance(monthly_returns, list):
            for point in monthly_returns:
                if isinstance(point, (tuple, list)) and len(point) >= 2:
                    rows.append(
                        {
                            "Month": self._stringify(point[0]),
                            "Return": float(self._to_float(point[1])),
                        }
                    )

        if not rows:
            empty_state("No monthly return data available")
            return

        frame = pd.DataFrame(rows)
        chart = (
            alt.Chart(frame)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("Month:N", title="Month", sort=None),
                y=alt.Y("Return:Q", title="Monthly Return %"),
                color=alt.condition(alt.datum.Return >= 0, alt.value("#16A34A"), alt.value("#DC2626")),
                tooltip=[alt.Tooltip("Month:N", title="Month"), alt.Tooltip("Return:Q", title="Return", format=",.2f")],
            )
            .properties(height=280)
        )
        st.altair_chart(chart, use_container_width=True)

    def _render_exit_reasons_chart(self, exit_reasons: dict[str, Any]) -> None:
        rows = []
        for reason, count in exit_reasons.items():
            rows.append({"Reason": self._stringify(reason), "Count": max(0.0, float(self._to_float(count)))})

        if not rows or all(item["Count"] == 0 for item in rows):
            empty_state("No exit reason data available")
            return

        frame = pd.DataFrame(rows)
        donut = (
            alt.Chart(frame)
            .mark_arc(innerRadius=68)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Reason:N", legend=alt.Legend(title="Reason")),
                tooltip=[alt.Tooltip("Reason:N", title="Reason"), alt.Tooltip("Count:Q", title="Trades", format=",.0f")],
            )
            .properties(height=280)
        )
        st.altair_chart(donut, use_container_width=True)

    def _render_trade_history(self, trade_history: list[dict[str, Any]]) -> None:
        rows = []
        for item in trade_history:
            direction = self._stringify(item.get("direction", item.get("side", "N/A")))
            pnl_value = self._to_float(item.get("net_pnl", item.get("pnl", 0.0)))
            side_class = self._trade_side_class(direction)
            pnl_class = "tp-pl-positive" if pnl_value >= 0 else "tp-pl-negative"
            rows.append(
                {
                    "symbol": self._stringify(item.get("symbol", "N/A")),
                    "direction": direction,
                    "entry_date": self._stringify(item.get("entry_date", item.get("entry", "N/A"))),
                    "entry_price": self._format_number(item.get("entry_price", "N/A"), decimals=2),
                    "exit_date": self._stringify(item.get("exit_date", item.get("exit", "N/A"))),
                    "exit_price": self._format_number(item.get("exit_price", "N/A"), decimals=2),
                    "quantity": self._stringify(item.get("quantity", "N/A")),
                    "net_pnl": self._format_currency(pnl_value),
                    "exit_reason": self._stringify(item.get("exit_reason", "N/A")),
                    "side_class": side_class,
                    "pnl_class": pnl_class,
                }
            )

        if not rows:
            empty_state("No completed trades")
            return

        headers = [
            "Symbol",
            "Direction",
            "Entry Date",
            "Entry Price",
            "Exit Date",
            "Exit Price",
            "Quantity",
            "Net P/L",
            "Exit Reason",
        ]
        body = []
        for row in rows:
            body.append(
                "".join(
                    [
                        f"<tr class='tp-trade-row {escape(row['side_class'])}'>",
                        f"<td>{escape(row['symbol'])}</td>",
                        f"<td>{escape(row['direction'])}</td>",
                        f"<td>{escape(row['entry_date'])}</td>",
                        f"<td class='tp-num'>{escape(row['entry_price'])}</td>",
                        f"<td>{escape(row['exit_date'])}</td>",
                        f"<td class='tp-num'>{escape(row['exit_price'])}</td>",
                        f"<td class='tp-num'>{escape(row['quantity'])}</td>",
                        f"<td class='tp-num {escape(row['pnl_class'])}'>{escape(row['net_pnl'])}</td>",
                        f"<td>{escape(row['exit_reason'])}</td>",
                        "</tr>",
                    ]
                )
            )

        table_html = (
            "<div class='tp-trade-history-wrap'>"
            "<table class='tp-trade-history'>"
            "<thead><tr>"
            + "".join(f"<th>{escape(header)}</th>" for header in headers)
            + "</tr></thead>"
            + "<tbody>"
            + "".join(body)
            + "</tbody></table></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    def _render_signal_explainability(self, signals: list[dict[str, Any]]) -> None:
        if not signals:
            empty_state("No signal explainability available")
            return

        rows: list[dict[str, Any]] = []
        for item in signals[-20:]:
            reasons = item.get("reasons", [])
            reasons_text = " | ".join(str(reason) for reason in reasons) if isinstance(reasons, list) else self._stringify(reasons)
            indicator_snapshot = self._extract_indicator_snapshot(reasons, item)
            rows.append(
                {
                    "Action": self._stringify(item.get("signal", "N/A")),
                    "Confidence": self._stringify(item.get("confidence", "N/A")),
                    "Indicators": indicator_snapshot,
                    "Suggested Stop": self._format_number(item.get("stop_loss", 0), decimals=2),
                    "Suggested Target": self._format_number(item.get("target", 0), decimals=2),
                    "Reasons": reasons_text,
                }
            )

        render_table(
            rows=rows,
            columns=["Action", "Confidence", "Indicators", "Suggested Stop", "Suggested Target", "Reasons"],
        )

    def _extract_indicator_snapshot(self, reasons: Any, item: dict[str, Any]) -> str:
        if isinstance(reasons, list):
            for reason in reasons:
                text = self._stringify(reason)
                if text.startswith("INDICATORS:"):
                    return text.replace("INDICATORS:", "", 1).strip()

        return ", ".join(
            [
                f"RSI={self._format_number(item.get('rsi', 0), decimals=2)}",
                f"EMA Fast={self._format_number(item.get('ema12', 0), decimals=2)}",
                f"EMA Slow={self._format_number(item.get('ema26', 0), decimals=2)}",
            ]
        )

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "N/A"
        return str(value)

    def _to_float(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().replace("$", "").replace(",", "")
        if text.endswith("%"):
            text = text[:-1]
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _format_currency(self, value: Any) -> str:
        amount = self._to_float(value)
        return f"${amount:,.2f}"

    def _format_number(self, value: Any, decimals: int = 2) -> str:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.upper() == "N/A":
                return "N/A"
        return f"{self._to_float(value):,.{decimals}f}"

    def _format_percent(self, value: Any, already_percent: bool = False) -> str:
        numeric = self._to_float(value)
        if not already_percent and abs(numeric) <= 1.0:
            numeric *= 100.0
        return f"{numeric:,.2f}%"

    def _semantic_signed(self, value: Any) -> str:
        numeric = self._to_float(value)
        if numeric > 0:
            return "tp-kpi-card--positive"
        if numeric < 0:
            return "tp-kpi-card--negative"
        return "tp-kpi-card--neutral"

    def _semantic_profit_factor(self, value: Any) -> str:
        numeric = self._to_float(value)
        if numeric > 2.0:
            return "tp-kpi-card--positive"
        if numeric >= 1.0:
            return "tp-kpi-card--warning"
        return "tp-kpi-card--negative"

    def _semantic_win_rate(self, value: Any) -> str:
        numeric = self._to_float(value)
        if numeric >= 55.0:
            return "tp-kpi-card--positive"
        if numeric >= 45.0:
            return "tp-kpi-card--warning"
        return "tp-kpi-card--negative"

    def _semantic_drawdown(self, value: Any) -> str:
        numeric = abs(self._to_float(value))
        if numeric <= 10.0:
            return "tp-kpi-card--positive"
        if numeric <= 20.0:
            return "tp-kpi-card--warning"
        return "tp-kpi-card--negative"

    def _trade_side_class(self, direction: str) -> str:
        normalized = direction.strip().lower()
        if normalized in {"buy", "long"}:
            return "tp-side-buy"
        if normalized in {"sell", "short"}:
            return "tp-side-sell"
        return "tp-side-neutral"

    def _normalize_chart_timestamps(self, values: Any) -> pd.Series:
        """Convert presentation timestamps to UTC for charting only."""
        if isinstance(values, pd.Series):
            raw_values = values.tolist()
            index = values.index
        elif isinstance(values, (list, tuple)):
            raw_values = list(values)
            index = None
        else:
            raw_values = [values]
            index = None

        try:
            series = pd.to_datetime(raw_values, errors="coerce", utc=True, format="mixed")
        except TypeError:
            series = pd.to_datetime(raw_values, errors="coerce", utc=True)

        if not isinstance(series, pd.Series):
            series = pd.Series(series)
        if index is not None:
            series.index = index
        return series

    def _points_to_dataframe(self, points: Any) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        if isinstance(points, list):
            for point in points:
                if isinstance(point, (tuple, list)) and len(point) >= 2:
                    rows.append({"Date": str(point[0]), "Value": float(self._to_float(point[1]))})
        if not rows:
            return pd.DataFrame(columns=["Date", "Value"])

        frame = pd.DataFrame(rows)
        frame["Date"] = self._normalize_chart_timestamps(frame["Date"])
        frame = frame.dropna(subset=["Date"]).sort_values("Date")
        return frame

    def _comparison_points_to_dataframe(self, points: Any) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        if isinstance(points, list):
            for point in points:
                if isinstance(point, dict):
                    rows.append(
                        {
                            "Strategy": self._stringify(point.get("strategy_name", point.get("strategy_id", "N/A"))),
                            "Date": self._stringify(point.get("timestamp", point.get("date", ""))),
                            "Value": float(self._to_float(point.get("value", 0.0))),
                        }
                    )
                elif isinstance(point, (tuple, list)) and len(point) >= 3:
                    rows.append(
                        {
                            "Strategy": self._stringify(point[0]),
                            "Date": self._stringify(point[1]),
                            "Value": float(self._to_float(point[2])),
                        }
                    )
        if not rows:
            return pd.DataFrame(columns=["Strategy", "Date", "Value"])

        frame = pd.DataFrame(rows)
        frame["Date"] = self._normalize_chart_timestamps(frame["Date"])
        frame = frame.dropna(subset=["Date"]).sort_values(["Strategy", "Date"])
        return frame

    def _comparison_monthly_dataframe(self, points: Any) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        if isinstance(points, list):
            for point in points:
                if isinstance(point, dict):
                    rows.append(
                        {
                            "Strategy": self._stringify(point.get("strategy_name", point.get("strategy_id", "N/A"))),
                            "Month": self._stringify(point.get("month", "")),
                            "Value": float(self._to_float(point.get("value", 0.0))),
                        }
                    )
                elif isinstance(point, (tuple, list)) and len(point) >= 3:
                    rows.append(
                        {
                            "Strategy": self._stringify(point[0]),
                            "Month": self._stringify(point[1]),
                            "Value": float(self._to_float(point[2])),
                        }
                    )
        if not rows:
            return pd.DataFrame(columns=["Strategy", "Month", "Value"])

        frame = pd.DataFrame(rows)
        return frame.sort_values(["Strategy", "Month"])

    def _apply_backtesting_styles(self) -> None:
        st.markdown(
            """
            <style>
            .tp-kpi-card--backtest {
                min-height: 172px;
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
            }
            .tp-kpi-card--backtest .tp-kpi-title {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #6B7280;
            }
            .tp-kpi-card--backtest .tp-kpi-value {
                font-size: clamp(1.45rem, 2vw, 2.35rem);
                font-weight: 800;
                line-height: 1.05;
            }
            .tp-kpi-card--backtest .tp-kpi-supporting {
                font-size: 0.74rem;
                color: #94A3B8;
            }
            .tp-kpi-card--positive {
                border-color: rgba(22, 163, 74, 0.35);
            }
            .tp-kpi-card--positive .tp-kpi-value {
                color: #166534;
            }
            .tp-kpi-card--warning {
                border-color: rgba(217, 119, 6, 0.35);
            }
            .tp-kpi-card--warning .tp-kpi-value {
                color: #B45309;
            }
            .tp-kpi-card--negative {
                border-color: rgba(220, 38, 38, 0.35);
            }
            .tp-kpi-card--negative .tp-kpi-value {
                color: #B91C1C;
            }
            .tp-kpi-card--neutral .tp-kpi-value {
                color: #111827;
            }

            .tp-trade-history-wrap {
                max-height: 420px;
                overflow: auto;
                border: 1px solid #D5DFEA;
                border-radius: 12px;
                background: #FFFFFF;
            }
            .tp-trade-history {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                min-width: 920px;
            }
            .tp-trade-history thead th {
                position: sticky;
                top: 0;
                z-index: 2;
                background: #EEF2F7;
                color: #111827;
                font-size: 0.82rem;
                font-weight: 800;
                padding: 10px 12px;
                border-bottom: 1px solid #D5DFEA;
                text-align: left;
            }
            .tp-trade-history td {
                padding: 9px 12px;
                border-bottom: 1px solid rgba(213, 223, 234, 0.65);
                font-size: 0.86rem;
                color: #111827;
            }
            .tp-trade-history .tp-num {
                text-align: right;
                font-variant-numeric: tabular-nums;
            }
            .tp-trade-history tbody tr:nth-child(even) {
                background: #F8FAFC;
            }
            .tp-trade-history tbody tr:hover {
                background: #EEF2F7;
            }
            .tp-trade-history tbody tr.tp-side-buy {
                background: rgba(22, 163, 74, 0.08);
            }
            .tp-trade-history tbody tr.tp-side-sell {
                background: rgba(220, 38, 38, 0.08);
            }
            .tp-trade-history tbody tr.tp-side-buy:nth-child(even) {
                background: rgba(22, 163, 74, 0.12);
            }
            .tp-trade-history tbody tr.tp-side-sell:nth-child(even) {
                background: rgba(220, 38, 38, 0.12);
            }
            .tp-trade-history .tp-pl-positive {
                color: #166534;
                font-weight: 700;
            }
            .tp-trade-history .tp-pl-negative {
                color: #B91C1C;
                font-weight: 700;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _resolve_container(self) -> Any | None:
        if self.data_provider is None:
            return None
        return getattr(self.data_provider, "container", None)
