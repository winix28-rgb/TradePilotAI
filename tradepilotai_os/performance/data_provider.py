"""Data provider for the professional performance workspace."""

from __future__ import annotations

from typing import Any

from tradepilotai_os.backtesting.data_provider import BacktestingDataProvider
from tradepilotai_os.core.container import Container
from tradepilotai_os.paper_trading.journal_service import JournalService
from tradepilotai_os.paper_trading.service import PaperTradingService

from .service import PerformanceService


class PerformanceDataProvider:
    """Resolve performance dashboard data from container/runtime services."""

    def __init__(self, container: Container | None = None, service: PerformanceService | None = None, state: dict[str, Any] | None = None) -> None:
        self.container = container
        self.service = service
        self.state = state or {}

    def get_performance_dashboard_data(self) -> dict[str, Any]:
        return self._resolve_service().get_dashboard_data()

    def export(self, *, format_name: str) -> tuple[bytes, str, str]:
        return self._resolve_service().export(format_name=format_name)

    def _resolve_service(self) -> PerformanceService:
        if self.service is not None:
            return self.service

        runtime_state = dict(self.state)
        try:
            import streamlit as st

            runtime_state.update(dict(st.session_state))
        except Exception:
            pass

        paper_service = None
        journal_service = None

        if self.container is not None:
            try:
                paper_service = self.container.resolve(PaperTradingService)
            except Exception:
                paper_service = None
            try:
                journal_service = self.container.resolve(JournalService)
            except Exception:
                journal_service = None

        if paper_service is None:
            paper_service = runtime_state.get("paper_trading_service")
        if journal_service is None:
            journal_service = runtime_state.get("trade_journal_service")

        backtesting_provider = BacktestingDataProvider(state=runtime_state)
        self.service = PerformanceService(
            paper_trading_service=paper_service,
            journal_service=journal_service,
            backtesting_data_provider=backtesting_provider,
            state=runtime_state,
        )
        return self.service
