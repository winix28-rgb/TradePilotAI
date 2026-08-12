"""Trade Journal workspace page for paper trading."""

from __future__ import annotations

from typing import Any

from dashboard.layout import render_desktop_layout
from dashboard.layout import render_kpi_card
from dashboard.layout import render_panel_header
from dashboard.layout import render_section
from dashboard.layout import render_table
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.workspace.base import WorkspacePage

from .journal_data_provider import JournalDataProvider


class JournalPage(WorkspacePage):
    """Render an interactive, read-only trade journal with notes support."""

    def __init__(self, data_provider: JournalDataProvider | None = None, navigation_service: NavigationService | None = None) -> None:
        super().__init__(page_title="Trade Journal", navigation_service=navigation_service)
        self.data_provider = data_provider
        self.data: dict[str, Any] = {}

    def render(self) -> str:
        streamlit = __import__("streamlit")
        state = streamlit.session_state
        filters_state = state.setdefault(
            "trade_journal_filters",
            {
                "start_date": "",
                "end_date": "",
                "strategy": "",
                "symbol": "",
                "direction": "",
                "exit_reason": "",
                "winner": False,
                "loser": False,
            },
        )
        search = str(state.get("trade_journal_search", ""))
        sort_by = str(state.get("trade_journal_sort_by", "exit_date"))
        ascending = bool(state.get("trade_journal_ascending", False))
        selected_journal_id = str(state.get("trade_journal_selected", ""))

        if self.data_provider is not None:
            self.data = self.data_provider.get_trade_journal_data(
                filters=filters_state,
                search=search,
                sort_by=sort_by,
                ascending=ascending,
                selected_journal_id=selected_journal_id,
            )
        else:
            self.data = {
                "summary": {},
                "entries": [],
                "selected_trade": {},
                "selected_journal_id": "",
                "available_filters": {},
            }

        summary = self.data.get("summary", {})
        entries = self.data.get("entries", [])
        selected_trade = self.data.get("selected_trade", {})
        available = self.data.get("available_filters", {})

        render_desktop_layout()
        render_panel_header("Trade Journal", status="event-driven")
        self._render_summary(summary)

        render_section("Search and Filters", lambda: self._render_filters(available))
        render_section("Journal Entries", lambda: self._render_entries(entries))
        render_section("Trade Detail", lambda: self._render_detail(entries, selected_trade))

        return "TRADE JOURNAL WORKSPACE Dashboard / Trade Journal Summary Filters Search Export Notes"

    def _render_summary(self, summary: dict[str, Any]) -> None:
        items = [
            ("Total Trades", self._stringify(summary.get("total_trades", 0))),
            ("Winners", self._stringify(summary.get("winners", 0))),
            ("Losers", self._stringify(summary.get("losers", 0))),
            ("Win Rate", self._percent(summary.get("win_rate", 0.0))),
            ("Net Profit", self._currency(summary.get("net_profit", 0.0))),
            ("Average Winner", self._currency(summary.get("average_winner", 0.0))),
            ("Average Loser", self._currency(summary.get("average_loser", 0.0))),
            ("Largest Winner", self._currency(summary.get("largest_winner", 0.0))),
            ("Largest Loser", self._currency(summary.get("largest_loser", 0.0))),
        ]

        cols = 3
        for start in range(0, len(items), cols):
            row = __import__("streamlit").columns(cols, gap="small")
            for col, (title, value) in zip(row, items[start : start + cols]):
                with col:
                    render_kpi_card(title=title, value=value, footer_label="Journal", footer_value="Paper")

    def _render_filters(self, available: dict[str, Any]) -> None:
        streamlit = __import__("streamlit")
        state = streamlit.session_state
        filters = state.setdefault(
            "trade_journal_filters",
            {
                "start_date": "",
                "end_date": "",
                "strategy": "",
                "symbol": "",
                "direction": "",
                "exit_reason": "",
                "winner": False,
                "loser": False,
            },
        )

        controls_top = streamlit.columns([2, 1, 1, 1], gap="small")
        with controls_top[0]:
            state["trade_journal_search"] = streamlit.text_input("Search", value=str(state.get("trade_journal_search", "")), key="trade_journal_search_input")
        with controls_top[1]:
            sort_choices = ["exit_date", "entry_date", "net_profit", "symbol", "strategy_name"]
            current_sort = str(state.get("trade_journal_sort_by", "exit_date"))
            if current_sort not in sort_choices:
                current_sort = "exit_date"
            state["trade_journal_sort_by"] = streamlit.selectbox("Sort By", sort_choices, index=sort_choices.index(current_sort), key="trade_journal_sort_by_input")
        with controls_top[2]:
            state["trade_journal_ascending"] = streamlit.checkbox("Ascending", value=bool(state.get("trade_journal_ascending", False)), key="trade_journal_ascending_input")
        with controls_top[3]:
            streamlit.write("")
            streamlit.write("")
            if streamlit.button("Clear", use_container_width=True):
                state["trade_journal_search"] = ""
                state["trade_journal_sort_by"] = "exit_date"
                state["trade_journal_ascending"] = False
                state["trade_journal_filters"] = {
                    "start_date": "",
                    "end_date": "",
                    "strategy": "",
                    "symbol": "",
                    "direction": "",
                    "exit_reason": "",
                    "winner": False,
                    "loser": False,
                }

        controls_bottom = streamlit.columns(6, gap="small")
        strategies = [""] + list(available.get("strategies", []))
        symbols = [""] + list(available.get("symbols", []))
        directions = [""] + list(available.get("directions", []))
        reasons = [""] + list(available.get("exit_reasons", []))

        with controls_bottom[0]:
            filters["start_date"] = streamlit.text_input("Start Date", value=str(filters.get("start_date", "")), key="trade_journal_start_date")
        with controls_bottom[1]:
            filters["end_date"] = streamlit.text_input("End Date", value=str(filters.get("end_date", "")), key="trade_journal_end_date")
        with controls_bottom[2]:
            filters["strategy"] = streamlit.selectbox("Strategy", strategies, index=self._index_of(strategies, str(filters.get("strategy", ""))), key="trade_journal_strategy")
        with controls_bottom[3]:
            filters["symbol"] = streamlit.selectbox("Symbol", symbols, index=self._index_of(symbols, str(filters.get("symbol", ""))), key="trade_journal_symbol")
        with controls_bottom[4]:
            filters["direction"] = streamlit.selectbox("Direction", directions, index=self._index_of(directions, str(filters.get("direction", ""))), key="trade_journal_direction")
        with controls_bottom[5]:
            filters["exit_reason"] = streamlit.selectbox("Exit Reason", reasons, index=self._index_of(reasons, str(filters.get("exit_reason", ""))), key="trade_journal_exit_reason")

        winner_col, loser_col = streamlit.columns(2, gap="small")
        with winner_col:
            filters["winner"] = streamlit.checkbox("Winner", value=bool(filters.get("winner", False)), key="trade_journal_winner")
        with loser_col:
            filters["loser"] = streamlit.checkbox("Loser", value=bool(filters.get("loser", False)), key="trade_journal_loser")

        state["trade_journal_filters"] = filters

    def _render_entries(self, entries: list[dict]) -> None:
        streamlit = __import__("streamlit")
        if entries:
            options = {f"{self._stringify(item.get('journal_id', ''))} | {self._stringify(item.get('symbol', ''))}": self._stringify(item.get("journal_id", "")) for item in entries}
            selected = streamlit.selectbox("Select Trade", list(options.keys()), key="trade_journal_select_entry")
            streamlit.session_state["trade_journal_selected"] = options.get(selected, "")

        rows = [
            {
                "Journal ID": self._stringify(item.get("journal_id", "")),
                "Trade ID": self._stringify(item.get("trade_id", "")),
                "Symbol": self._stringify(item.get("symbol", "")),
                "Strategy": self._stringify(item.get("strategy_name", "")),
                "Direction": self._stringify(item.get("direction", "")),
                "Entry Date": self._stringify(item.get("entry_date", "")),
                "Exit Date": self._stringify(item.get("exit_date", "")),
                "Net Profit": self._currency(item.get("net_profit", 0.0)),
                "Return %": self._percent(item.get("return_percent", 0.0)),
                "Exit Reason": self._stringify(item.get("exit_reason", "")),
                "Tags": ", ".join(item.get("tags", [])),
            }
            for item in entries
        ]
        render_table(
            rows=rows,
            columns=[
                "Journal ID",
                "Trade ID",
                "Symbol",
                "Strategy",
                "Direction",
                "Entry Date",
                "Exit Date",
                "Net Profit",
                "Return %",
                "Exit Reason",
                "Tags",
            ],
        )

        export_cols = streamlit.columns(3, gap="small")
        export_pairs = [
            ("CSV", "csv"),
            ("Excel", "excel"),
            ("JSON", "json"),
        ]
        for col, (label, fmt) in zip(export_cols, export_pairs):
            with col:
                if streamlit.button(f"Export {label}", use_container_width=True, key=f"trade_journal_export_{fmt}"):
                    if self.data_provider is not None:
                        data, filename, mime = self.data_provider.export(
                            format_name=fmt,
                            filters=streamlit.session_state.get("trade_journal_filters", {}),
                            search=str(streamlit.session_state.get("trade_journal_search", "")),
                            sort_by=str(streamlit.session_state.get("trade_journal_sort_by", "exit_date")),
                            ascending=bool(streamlit.session_state.get("trade_journal_ascending", False)),
                        )
                        streamlit.download_button(
                            f"Download {label}",
                            data=data,
                            file_name=filename,
                            mime=mime,
                            use_container_width=True,
                            key=f"trade_journal_download_{fmt}",
                        )

    def _render_detail(self, entries: list[dict], selected_trade: dict[str, Any]) -> None:
        streamlit = __import__("streamlit")
        if not selected_trade and entries:
            selected_trade = entries[0]

        if not selected_trade:
            render_table(rows=[{"Field": "Status", "Value": "No completed journal entries yet."}], columns=["Field", "Value"])
            return

        detail_rows = [
            {"Field": "Journal ID", "Value": self._stringify(selected_trade.get("journal_id", ""))},
            {"Field": "Trade ID", "Value": self._stringify(selected_trade.get("trade_id", ""))},
            {"Field": "Position ID", "Value": self._stringify(selected_trade.get("position_id", ""))},
            {"Field": "Decision ID", "Value": self._stringify(selected_trade.get("decision_id", ""))},
            {"Field": "Strategy ID", "Value": self._stringify(selected_trade.get("strategy_id", ""))},
            {"Field": "Strategy Name", "Value": self._stringify(selected_trade.get("strategy_name", ""))},
            {"Field": "Symbol", "Value": self._stringify(selected_trade.get("symbol", ""))},
            {"Field": "Asset Class", "Value": self._stringify(selected_trade.get("asset_class", ""))},
            {"Field": "Direction", "Value": self._stringify(selected_trade.get("direction", ""))},
            {"Field": "Entry Date", "Value": self._stringify(selected_trade.get("entry_date", ""))},
            {"Field": "Exit Date", "Value": self._stringify(selected_trade.get("exit_date", ""))},
            {"Field": "Holding Period", "Value": self._stringify(selected_trade.get("holding_period", ""))},
            {"Field": "Entry Price", "Value": self._currency(selected_trade.get("entry_price", 0.0))},
            {"Field": "Exit Price", "Value": self._currency(selected_trade.get("exit_price", 0.0))},
            {"Field": "Quantity", "Value": self._stringify(selected_trade.get("quantity", 0))},
            {"Field": "Gross Profit", "Value": self._currency(selected_trade.get("gross_profit", 0.0))},
            {"Field": "Costs", "Value": self._currency(selected_trade.get("costs", 0.0))},
            {"Field": "Net Profit", "Value": self._currency(selected_trade.get("net_profit", 0.0))},
            {"Field": "Return %", "Value": self._percent(selected_trade.get("return_percent", 0.0))},
            {"Field": "Exit Reason", "Value": self._stringify(selected_trade.get("exit_reason", ""))},
            {"Field": "Exit Explanation", "Value": self._stringify(selected_trade.get("exit_explanation", ""))},
            {"Field": "Tags", "Value": ", ".join(selected_trade.get("tags", []))},
        ]
        render_table(rows=detail_rows, columns=["Field", "Value"])

        snapshot_cols = streamlit.columns(2, gap="small")
        with snapshot_cols[0]:
            render_table(
                rows=[{"Field": key, "Value": self._stringify(value)} for key, value in (selected_trade.get("decision_snapshot", {}) or {}).items()],
                columns=["Field", "Value"],
            )
            render_table(
                rows=[{"Field": key, "Value": self._stringify(value)} for key, value in (selected_trade.get("risk_snapshot", {}) or {}).items()],
                columns=["Field", "Value"],
            )
        with snapshot_cols[1]:
            render_table(
                rows=[{"Field": key, "Value": self._stringify(value)} for key, value in (selected_trade.get("market_snapshot", {}) or {}).items()],
                columns=["Field", "Value"],
            )
            render_table(
                rows=[{"Field": key, "Value": self._stringify(value)} for key, value in (selected_trade.get("performance_snapshot", {}) or {}).items()],
                columns=["Field", "Value"],
            )

        evidence_rows = [{"Evidence": self._stringify(item)} for item in (selected_trade.get("supporting_evidence", []) or [])]
        if not evidence_rows:
            evidence_rows = [{"Evidence": "No supporting evidence captured."}]
        render_table(rows=evidence_rows, columns=["Evidence"])

        audit_rows = [
            {
                "Event": self._stringify(item.get("event", "")),
                "Timestamp": self._stringify(item.get("timestamp", "")),
                "Details": self._stringify(item.get("details", {})),
            }
            for item in (selected_trade.get("audit_events", []) or [])
        ]
        if not audit_rows:
            audit_rows = [{"Event": "N/A", "Timestamp": "N/A", "Details": "No related audit events."}]
        render_table(rows=audit_rows, columns=["Event", "Timestamp", "Details"])

        selected_id = self._stringify(selected_trade.get("journal_id", ""))
        note_value = self._stringify(selected_trade.get("notes", ""))
        note_input = streamlit.text_area("User Notes", value=note_value, key=f"trade_journal_note_{selected_id}")
        if streamlit.button("Save Note", use_container_width=True, key=f"trade_journal_note_save_{selected_id}"):
            if self.data_provider is not None:
                self.data_provider.save_note(selected_id, note_input)
                streamlit.success("Note saved.")

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
            return ""
        return str(value)

    def _index_of(self, values: list[str], value: str) -> int:
        try:
            return values.index(value)
        except ValueError:
            return 0
