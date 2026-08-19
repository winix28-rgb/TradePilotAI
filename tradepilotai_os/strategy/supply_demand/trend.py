"""
===========================================================
TradePilotAI OS
Supply & Demand Trend Engine
===========================================================

Determines Daily and H4 trend information for the
Supply & Demand strategy.

This module does NOT generate trades.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .models import TimeframeTrend, TrendDirection


class SupplyDemandTrendEngine:
    """
    Calculate Daily/H4 moving averages and classify trend.

    The strategy uses:
        - 50-period moving average
        - 200-period moving average
        - candle/price direction relative to the moving averages

    No crossover rule is imposed.
    """

    def analyse(
        self,
        data: pd.DataFrame,
        timeframe: str,
    ) -> TimeframeTrend:
        """
        Analyse one timeframe.

        Expected columns:
            Open
            High
            Low
            Close

        The dataframe should be ordered chronologically.
        """

        if data is None or data.empty:
            return TimeframeTrend(
                timeframe=timeframe,
                direction=TrendDirection.NEUTRAL,
                explanation="No market data available.",
            )

        required_columns = {"Open", "High", "Low", "Close"}

        missing = required_columns.difference(data.columns)

        if missing:
            raise ValueError(
                f"Missing required market-data columns: "
                f"{sorted(missing)}"
            )

        frame = data.copy()

        frame["MA50"] = (
            frame["Close"]
            .rolling(window=50, min_periods=50)
            .mean()
        )

        frame["MA200"] = (
            frame["Close"]
            .rolling(window=200, min_periods=200)
            .mean()
        )

        latest = frame.iloc[-1]

        price = float(latest["Close"])

        ma50 = self._optional_float(latest["MA50"])
        ma200 = self._optional_float(latest["MA200"])

        direction, explanation = self._classify_trend(
            frame=frame,
            price=price,
            ma50=ma50,
            ma200=ma200,
        )

        return TimeframeTrend(
            timeframe=timeframe,
            direction=direction,
            ma50=ma50,
            ma200=ma200,
            price=price,
            candles_with_trend=direction != TrendDirection.NEUTRAL,
            explanation=explanation,
        )

    def analyse_daily(
        self,
        data: pd.DataFrame,
    ) -> TimeframeTrend:
        """Analyse the Daily timeframe."""

        return self.analyse(
            data=data,
            timeframe="Daily",
        )

    def analyse_h4(
        self,
        data: pd.DataFrame,
    ) -> TimeframeTrend:
        """Analyse the H4 timeframe."""

        return self.analyse(
            data=data,
            timeframe="H4",
        )

    def _classify_trend(
        self,
        frame: pd.DataFrame,
        price: float,
        ma50: float | None,
        ma200: float | None,
    ) -> tuple[TrendDirection, str]:
        """
        Classify the current direction.

        We deliberately avoid inventing a crossover rule.

        The current implementation uses the relationship of
        the latest closing price to both moving averages.

        Above both MAs:
            bullish

        Below both MAs:
            bearish

        Between the MAs:
            neutral / unclear

        The actual candle-direction interpretation can be
        refined later using the visual examples supplied by
        the user without changing the rest of the strategy.
        """

        if ma50 is None or ma200 is None:
            return (
                TrendDirection.NEUTRAL,
                "Insufficient data to calculate both moving averages.",
            )

        if price > ma50 and price > ma200:
            return (
                TrendDirection.BULLISH,
                "Price is above both the 50 and 200 moving averages.",
            )

        if price < ma50 and price < ma200:
            return (
                TrendDirection.BEARISH,
                "Price is below both the 50 and 200 moving averages.",
            )

        return (
            TrendDirection.NEUTRAL,
            "Price is between the 50 and 200 moving averages.",
        )

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        """Convert a value to float, preserving missing values."""

        if pd.isna(value):
            return None

        return float(value)