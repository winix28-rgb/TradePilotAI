"""Signal generation components for the TradePilotAI OS."""

from __future__ import annotations

from typing import Any

import pandas as pd

from tradepilotai_os.models.market_status import MarketStatus
from tradepilotai_os.models.signal import Signal


class SignalEngine:
    """Generate standardized signal objects from indicator outputs.

    This engine focuses on signal detection only. It does not apply
    strategy, risk, or execution rules.
    """

    @staticmethod
    def is_bullish_crossover(previous: pd.Series, current: pd.Series) -> bool:
        """Return True when EMA12 crosses above EMA26."""

        return (
            float(previous["EMA12"]) <= float(previous["EMA26"])
            and float(current["EMA12"]) > float(current["EMA26"])
        )

    @staticmethod
    def is_bearish_crossover(previous: pd.Series, current: pd.Series) -> bool:
        """Return True when EMA12 crosses below EMA26."""

        return (
            float(previous["EMA12"]) >= float(previous["EMA26"])
            and float(current["EMA12"]) < float(current["EMA26"])
        )

    def find_signals(self, data: pd.DataFrame, ticker: str) -> list[Signal]:
        """Return historical crossover signals for the supplied dataframe."""

        signals: list[Signal] = []

        for index in range(1, len(data)):
            previous = data.iloc[index - 1]
            current = data.iloc[index]

            if self.is_bullish_crossover(previous, current):
                signals.append(
                    Signal(
                        ticker=ticker,
                        signal_type="BUY",
                        entry_price=float(current["Close"]),
                        stop_loss=float(current["Low"]),
                        rsi=float(current["RSI"]),
                        ema12=float(current["EMA12"]),
                        ema26=float(current["EMA26"]),
                    )
                )
            elif self.is_bearish_crossover(previous, current):
                signals.append(
                    Signal(
                        ticker=ticker,
                        signal_type="SELL",
                        entry_price=float(current["Close"]),
                        stop_loss=float(current["High"]),
                        rsi=float(current["RSI"]),
                        ema12=float(current["EMA12"]),
                        ema26=float(current["EMA26"]),
                    )
                )

        return signals

    def get_market_status(self, data: pd.DataFrame, ticker: str) -> MarketStatus:
        """Return the current market status based on the latest data."""

        latest = data.iloc[-1]

        if float(latest["EMA12"]) > float(latest["EMA26"]):
            trend = "Bullish"
        elif float(latest["EMA12"]) < float(latest["EMA26"]):
            trend = "Bearish"
        else:
            trend = "Neutral"

        signal_type = "NONE"
        signal_age = -1

        for index in range(len(data) - 1, 0, -1):
            previous = data.iloc[index - 1]
            current = data.iloc[index]

            if self.is_bullish_crossover(previous, current):
                signal_type = "BUY"
                signal_age = len(data) - 1 - index
                break

            if self.is_bearish_crossover(previous, current):
                signal_type = "SELL"
                signal_age = len(data) - 1 - index
                break

        return MarketStatus(
            ticker=ticker,
            trend=trend,
            current_signal=signal_type,
            signal_age=signal_age,
            close=float(latest["Close"]),
            ema12=float(latest["EMA12"]),
            ema26=float(latest["EMA26"]),
            rsi=float(latest["RSI"]),
        )
