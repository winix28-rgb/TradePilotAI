"""
===========================================================
TradePilotAI OS
Signal Engine
===========================================================

Implements the TradePilotAI trading rules.

LONG
-----
RSI < 30
EMA12 crosses ABOVE EMA26

SHORT
------
RSI > 70
EMA12 crosses BELOW EMA26

EXIT
-----
RSI returns to 50
"""

from __future__ import annotations

from tradepilotai_os.models.trade_signal import TradeSignal


class SignalEngine:

    @staticmethod
    def evaluate(symbol: str, data) -> TradeSignal:

        # -------------------------------------------------
        # Flatten Yahoo Finance MultiIndex columns
        # -------------------------------------------------

        if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:
            data = data.copy()
            data.columns = data.columns.get_level_values(0)

        if len(data) < 30:
            raise ValueError(
                "Not enough market data to evaluate signal."
            )

        latest = data.iloc[-1]

        price = float(latest["Close"])

        rsi = float(latest["RSI"])

        ema12 = float(latest["EMA12"])
        ema26 = float(latest["EMA26"])

        bullish_alignment = ema12 > ema26
        bearish_alignment = ema12 < ema26

        oversold = rsi < 30
        overbought = rsi > 70

        signal = "HOLD"
        confidence = 0
        reasons: list[str] = []

        if bullish_alignment:
            reasons.append("Bullish EMA alignment")
        elif bearish_alignment:
            reasons.append("Bearish EMA alignment")
        else:
            reasons.append("Neutral EMA alignment")

        if oversold:
            reasons.append("RSI Oversold")
        elif overbought:
            reasons.append("RSI Overbought")

        if oversold and bullish_alignment:
            signal = "BUY"
            confidence = 70
            if rsi < 20:
                confidence += 10
            if abs(rsi - 15) < 15:
                confidence += 10
        elif overbought and bearish_alignment:
            signal = "SELL"
            confidence = 70
            if rsi > 80:
                confidence += 10
            if abs(rsi - 85) < 15:
                confidence += 10
        else:
            confidence = 40
            if bullish_alignment:
                confidence += 10
            elif bearish_alignment:
                confidence += 10
            if oversold or overbought:
                confidence += 10
            reasons.append("No qualifying setup")

        confidence = min(100, max(0, confidence))

        stop_loss = round(price * 0.98, 2)
        target = round(price * 1.06, 2)

        return TradeSignal(
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            price=price,
            rsi=rsi,
            ema12=ema12,
            ema26=ema26,
            stop_loss=stop_loss,
            target=target,
            reasons=reasons,
        )