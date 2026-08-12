"""Read-only service facade for the professional performance dashboard."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from tradepilotai_os.backtesting.data_provider import BacktestingDataProvider
from tradepilotai_os.paper_trading.journal_service import JournalService
from tradepilotai_os.paper_trading.service import PaperTradingService

from .engine import PerformanceEngine


class PerformanceService:
    """Aggregate inputs from portfolio, journal, and backtesting into one dashboard payload."""

    def __init__(
        self,
        *,
        engine: PerformanceEngine | None = None,
        paper_trading_service: PaperTradingService | None = None,
        journal_service: JournalService | None = None,
        backtesting_data_provider: BacktestingDataProvider | None = None,
        state: dict[str, Any] | None = None,
    ) -> None:
        self.engine = engine or PerformanceEngine()
        self.paper_trading_service = paper_trading_service or PaperTradingService(journal_service=journal_service)
        self.journal_service = journal_service or getattr(self.paper_trading_service, "journal_service", None)
        self.backtesting_data_provider = backtesting_data_provider or BacktestingDataProvider(state=state or {})

    def get_dashboard_data(self) -> dict[str, Any]:
        paper_payload = self.paper_trading_service.get_workspace_data()
        backtest_payload = self.backtesting_data_provider.get_backtest_data()
        comparison_payload = self.backtesting_data_provider.get_comparison_data()

        dashboard = self.engine.build_dashboard(
            paper_portfolio=paper_payload.get("summary", {}),
            paper_closed_trades=paper_payload.get("closed_trades", []),
            trade_journal_entries=paper_payload.get("trade_journal", {}).get("entries", []),
            backtest_payload=backtest_payload,
            strategy_comparison_payload=comparison_payload,
        )
        payload = dashboard.to_dict()
        payload["comparison"] = comparison_payload
        return payload

    def export(self, *, format_name: str) -> tuple[bytes, str, str]:
        payload = self.get_dashboard_data()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if format_name.lower() == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "source",
                    "trade_id",
                    "strategy_name",
                    "symbol",
                    "direction",
                    "entry_date",
                    "exit_date",
                    "net_profit",
                    "exit_reason",
                    "asset_class",
                ],
            )
            writer.writeheader()
            for row in payload.get("trades", []):
                writer.writerow(
                    {
                        "source": row.get("source", ""),
                        "trade_id": row.get("trade_id", ""),
                        "strategy_name": row.get("strategy_name", ""),
                        "symbol": row.get("symbol", ""),
                        "direction": row.get("direction", ""),
                        "entry_date": row.get("entry_date", ""),
                        "exit_date": row.get("exit_date", ""),
                        "net_profit": row.get("net_profit", 0.0),
                        "exit_reason": row.get("exit_reason", ""),
                        "asset_class": row.get("asset_class", ""),
                    }
                )
            return output.getvalue().encode("utf-8"), f"performance_dashboard_{timestamp}.csv", "text/csv"

        if format_name.lower() in {"excel", "xlsx"}:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Section", "Key", "Value"])
            for section_name in (
                "portfolio_overview",
                "performance_kpis",
                "drawdown",
                "trade_analysis",
                "risk_analysis",
            ):
                section = payload.get(section_name, {})
                if isinstance(section, dict):
                    for key, value in section.items():
                        writer.writerow([section_name, key, value])
            return output.getvalue().encode("utf-8"), f"performance_dashboard_{timestamp}.xls", "application/vnd.ms-excel"

        return json.dumps(payload, indent=2).encode("utf-8"), f"performance_dashboard_{timestamp}.json", "application/json"
