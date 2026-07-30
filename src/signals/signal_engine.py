"""
===========================================================
FTSE Quant Trader V2
Signal Engine
===========================================================

Stage 2

Detects EMA crossover signals and reports
the current market status.
"""

import pandas as pd

from models.signal import Signal
from models.market_status import MarketStatus


class SignalEngine:
    """
    Detect trading signals.
    """

    def __init__(self):
        print("Signal Engine Initialised")

    # =========================================================
    # Reusable Crossover Helpers
    # =========================================================

    def is_bullish_crossover(self, previous, current):
        """
        Returns True if EMA12 has crossed ABOVE EMA26.
        """

        return (
            previous["EMA12"] <= previous["EMA26"]
            and current["EMA12"] > current["EMA26"]
        )

    def is_bearish_crossover(self, previous, current):
        """
        Returns True if EMA12 has crossed BELOW EMA26.
        """

        return (
            previous["EMA12"] >= previous["EMA26"]
            and current["EMA12"] < current["EMA26"]
        )

    # =========================================================
    # Historical Signal Detection
    # =========================================================

    def find_signals(self, data: pd.DataFrame, ticker: str):
        """
        Find every historical EMA crossover.
        """

        signals = []

        for i in range(1, len(data)):

            previous = data.iloc[i - 1]
            current = data.iloc[i]

            if self.is_bullish_crossover(previous, current):

                signals.append(
                    Signal(
                        ticker=ticker,
                        signal_type="BUY",
                        entry_price=current["Close"],
                        stop_loss=current["Low"],
                        rsi=current["RSI"],
                        ema12=current["EMA12"],
                        ema26=current["EMA26"],
                    )
                )

            elif self.is_bearish_crossover(previous, current):

                signals.append(
                    Signal(
                        ticker=ticker,
                        signal_type="SELL",
                        entry_price=current["Close"],
                        stop_loss=current["High"],
                        rsi=current["RSI"],
                        ema12=current["EMA12"],
                        ema26=current["EMA26"],
                    )
                )

        return signals

    # =========================================================
    # Current Market Status
    # =========================================================

    def get_market_status(self, data: pd.DataFrame, ticker: str):
        """
        Return the current state of the market.
        """

        latest = data.iloc[-1]

        if latest["EMA12"] > latest["EMA26"]:
            trend = "Bullish"

        elif latest["EMA12"] < latest["EMA26"]:
            trend = "Bearish"

        else:
            trend = "Neutral"

        signal_type = "NONE"
        signal_age = -1

        for i in range(len(data) - 1, 0, -1):

            previous = data.iloc[i - 1]
            current = data.iloc[i]

            if self.is_bullish_crossover(previous, current):
                signal_type = "BUY"
                signal_age = len(data) - 1 - i
                break

            if self.is_bearish_crossover(previous, current):
                signal_type = "SELL"
                signal_age = len(data) - 1 - i
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