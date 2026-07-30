"""
============================================================
TradePilotAI Operating System
Data Engine
============================================================

A service-oriented market data component for the TradePilotAI
OS architecture. It wraps the Yahoo Finance-backed data
retrieval logic from the older trading prototype and exposes
it through the OS service lifecycle.
"""

from __future__ import annotations

from typing import Any

import yfinance as yf

from .service import Service


class DataEngine(Service):
    """
    Downloads historical market data as an OS service.

    This class preserves the trading prototype behavior while
    fitting the TradePilotAI service model.
    """

    def __init__(self) -> None:
        self._initialized = False

    def start(self) -> None:
        self._initialized = True

    def stop(self) -> None:
        self._initialized = False

    def is_running(self) -> bool:
        return self._initialized

    def download_data(self, ticker: str, interval: str, period: str) -> Any:
        """
        Download historical price data.

        Parameters
        ----------
        ticker : str
            Example: RR.L

        interval : str
            Example: 1h

        period : str
            Example: 180d
        """

        try:
            data = yf.download(
                ticker,
                interval=interval,
                period=period,
                auto_adjust=True,
                progress=False,
            )

            if getattr(data, "empty", True):
                return None

            if data.columns.nlevels > 1:
                data.columns = data.columns.get_level_values(0)

            return data

        except Exception:
            return None
