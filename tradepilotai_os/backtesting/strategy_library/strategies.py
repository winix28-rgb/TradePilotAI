"""Built-in strategies for the backtesting strategy library."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.signals.signal_engine import SignalEngine

from .interface import BacktestStrategy
from .models import StrategyParameter


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


RSI_WAITING = "WAITING"
RSI_LONG_ARMED = "LONG_ARMED"
RSI_LONG_IN_TRADE = "LONG_IN_TRADE"
RSI_SHORT_ARMED = "SHORT_ARMED"
RSI_SHORT_IN_TRADE = "SHORT_IN_TRADE"


@dataclass(slots=True)
class _RSIMeanReversionState:
    state: str = RSI_WAITING
    entry_price: float | None = None
    stop_loss: float | None = None
    target: float | None = None


class RSIMeanReversionBacktestStrategy(BacktestStrategy):
    strategy_id = "rsi_mean_reversion"
    name = "TradePilotAI RSI Mean Reversion"
    description = "Mean reversion strategy using RSI extremes with EMA crossover confirmation."
    category = "Mean Reversion"
    version = "1.0"
    author = "TradePilotAI"
    asset_class = "Equities"
    primary_timeframe = "1h"
    supported_timeframes = ["1h", "2h"]
    supported_assets = ["Equities", "ETFs"]
    supports_long = True
    supports_short = True
    risk_profile = "Medium"
    indicators = ["RSI", "EMA Fast", "EMA Slow", "EMA200"]

    WAITING = RSI_WAITING
    LONG_ARMED = RSI_LONG_ARMED
    LONG_IN_TRADE = RSI_LONG_IN_TRADE
    SHORT_ARMED = RSI_SHORT_ARMED
    SHORT_IN_TRADE = RSI_SHORT_IN_TRADE

    def __init__(self, parameters: dict[str, Any] | None = None) -> None:
        self._params = self._merge_defaults(parameters)
        self._validate_parameters()
        self._states: dict[str, _RSIMeanReversionState] = {}

    @property
    def parameters(self) -> list[StrategyParameter]:
        return [
            StrategyParameter("rsi_period", "RSI Period", "int", 14, minimum=2, maximum=200, step=1),
            StrategyParameter("oversold", "Oversold", "float", 30.0, minimum=1.0, maximum=49.0, step=1.0),
            StrategyParameter("overbought", "Overbought", "float", 70.0, minimum=51.0, maximum=99.0, step=1.0),
            StrategyParameter("exit_rsi", "Exit RSI", "float", 50.0, minimum=2.0, maximum=98.0, step=1.0),
            StrategyParameter("fast_ema", "Fast EMA", "int", 12, minimum=2, maximum=199, step=1),
            StrategyParameter("slow_ema", "Slow EMA", "int", 26, minimum=3, maximum=300, step=1),
            StrategyParameter("trend_filter_enabled", "Trend Filter Enabled", "bool", False),
            StrategyParameter("stop_loss_pct", "Stop Loss %", "float", 2.0, minimum=0.1, maximum=20.0, step=0.1),
            StrategyParameter("target_pct", "Target %", "float", 4.0, minimum=0.1, maximum=40.0, step=0.1),
        ]

    def evaluate(self, symbol: str, data: Any) -> dict[str, Any]:
        frame = data.copy() if hasattr(data, "copy") else data
        if hasattr(frame, "columns") and hasattr(frame.columns, "nlevels") and frame.columns.nlevels > 1:
            frame.columns = frame.columns.get_level_values(0)

        if not hasattr(frame, "iloc") or len(frame) < 2:
            raise ValueError("RSI Mean Reversion requires at least 2 candles for crossover detection.")

        rsi_period = _safe_int(self._params.get("rsi_period"), 14)
        fast_period = _safe_int(self._params.get("fast_ema"), 12)
        slow_period = _safe_int(self._params.get("slow_ema"), 26)

        close_series = frame["Close"].astype(float)
        fast_col = f"EMA{fast_period}"
        slow_col = f"EMA{slow_period}"

        if fast_col not in frame.columns:
            frame[fast_col] = close_series.ewm(span=max(2, fast_period), adjust=False).mean()
        if slow_col not in frame.columns:
            frame[slow_col] = close_series.ewm(span=max(3, slow_period), adjust=False).mean()
        if "EMA200" not in frame.columns:
            frame["EMA200"] = close_series.ewm(span=200, adjust=False).mean()
        if "RSI" not in frame.columns:
            frame["RSI"] = self._calculate_rsi(close_series, period=max(2, rsi_period))

        latest = frame.iloc[-1]
        previous = frame.iloc[-2]

        price = _safe_float(latest.get("Close"), 0.0)
        prev_rsi = _safe_float(previous.get("RSI"), 50.0)
        rsi = _safe_float(latest.get("RSI"), prev_rsi)
        prev_ema_fast = _safe_float(previous.get(fast_col), price)
        prev_ema_slow = _safe_float(previous.get(slow_col), price)
        ema_fast = _safe_float(latest.get(fast_col), prev_ema_fast)
        ema_slow = _safe_float(latest.get(slow_col), prev_ema_slow)
        ema200 = _safe_float(latest.get("EMA200"), price)

        oversold = _safe_float(self._params.get("oversold"), 30.0)
        overbought = _safe_float(self._params.get("overbought"), 70.0)
        exit_rsi = _safe_float(self._params.get("exit_rsi"), 50.0)
        trend_filter_enabled = bool(self._params.get("trend_filter_enabled", False))
        state = self._get_state(symbol)

        bullish_crossover = prev_ema_fast <= prev_ema_slow and ema_fast > ema_slow
        bearish_crossover = prev_ema_fast >= prev_ema_slow and ema_fast < ema_slow

        oversold_hit = rsi < oversold
        overbought_hit = rsi > overbought

        trend_long_ok = price > ema200
        trend_short_ok = price < ema200

        long_entry_ok = oversold_hit and bullish_crossover and (trend_long_ok if trend_filter_enabled else True)
        short_entry_ok = overbought_hit and bearish_crossover and (trend_short_ok if trend_filter_enabled else True)

        long_exit_ready = rsi >= exit_rsi
        short_exit_ready = rsi <= exit_rsi

        return {
            "price": price,
            "rsi": rsi,
            "previous_rsi": prev_rsi,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "previous_ema_fast": prev_ema_fast,
            "previous_ema_slow": prev_ema_slow,
            "ema200": ema200,
            "oversold_hit": oversold_hit,
            "overbought_hit": overbought_hit,
            "bullish_crossover": bullish_crossover,
            "bearish_crossover": bearish_crossover,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_long_ok": trend_long_ok,
            "trend_short_ok": trend_short_ok,
            "long_entry_ok": long_entry_ok,
            "short_entry_ok": short_entry_ok,
            "long_exit_ready": long_exit_ready,
            "short_exit_ready": short_exit_ready,
            "fsm_state": state.state,
            "in_position_long": state.state == self.LONG_IN_TRADE,
            "in_position_short": state.state == self.SHORT_IN_TRADE,
            "entry_price": state.entry_price,
            "position_stop_loss": state.stop_loss,
            "position_target": state.target,
            "parameters": dict(self._params),
        }

    def generate_signal(self, symbol: str, context: dict[str, Any]) -> TradeSignal:
        state = self._get_state(symbol)
        price = _safe_float(context.get("price"), 0.0)
        rsi = _safe_float(context.get("rsi"), 50.0)
        ema_fast = _safe_float(context.get("ema_fast"), price)
        ema_slow = _safe_float(context.get("ema_slow"), price)
        ema200 = _safe_float(context.get("ema200"), price)

        oversold = _safe_float(self._params.get("oversold"), 30.0)
        overbought = _safe_float(self._params.get("overbought"), 70.0)
        exit_rsi = _safe_float(self._params.get("exit_rsi"), 50.0)
        stop_pct = max(0.1, _safe_float(self._params.get("stop_loss_pct"), 2.0)) / 100.0
        target_pct = max(0.1, _safe_float(self._params.get("target_pct"), 4.0)) / 100.0

        bullish_crossover = bool(context.get("bullish_crossover", False))
        bearish_crossover = bool(context.get("bearish_crossover", False))
        oversold_hit = bool(context.get("oversold_hit", rsi < oversold))
        overbought_hit = bool(context.get("overbought_hit", rsi > overbought))
        trend_filter_enabled = bool(context.get("trend_filter_enabled", self._params.get("trend_filter_enabled", False)))
        trend_long_ok = bool(context.get("trend_long_ok", price > ema200))
        trend_short_ok = bool(context.get("trend_short_ok", price < ema200))
        long_exit_ready = bool(context.get("long_exit_ready", rsi >= exit_rsi))
        short_exit_ready = bool(context.get("short_exit_ready", rsi <= exit_rsi))

        signal = "HOLD"
        confidence = 40
        reasons: list[str] = []

        if state.state == self.WAITING:
            if oversold_hit:
                state.state = self.LONG_ARMED
                reasons.append("STATE_TRANSITION: WAITING -> LONG_ARMED")
            elif overbought_hit:
                state.state = self.SHORT_ARMED
                reasons.append("STATE_TRANSITION: WAITING -> SHORT_ARMED")

        if state.state == self.LONG_ARMED:
            reasons.append("STATE: LONG_ARMED")
            long_entry_ok = bullish_crossover and (trend_long_ok if trend_filter_enabled else True)
            if long_entry_ok:
                signal = "BUY"
                confidence = self._entry_confidence(
                    checks=[True, True, trend_long_ok if trend_filter_enabled else True],
                    trend_filter_enabled=trend_filter_enabled,
                )
                reasons.append("CHECK_RSI_OVERSOLD: pass")
                reasons.append("CHECK_EMA_BULLISH_CROSSOVER: pass")
                if trend_filter_enabled:
                    reasons.append("CHECK_TREND_FILTER_LONG: pass")
                self._enter_long(state, price, stop_pct, target_pct)
                reasons.append("STATE_TRANSITION: LONG_ARMED -> LONG_IN_TRADE")
            else:
                confidence = self._hold_confidence(
                    oversold_hit=oversold_hit,
                    overbought_hit=overbought_hit,
                    bullish_crossover=bullish_crossover,
                    bearish_crossover=bearish_crossover,
                    trend_filter_enabled=trend_filter_enabled,
                    trend_long_ok=trend_long_ok,
                    trend_short_ok=trend_short_ok,
                )
                reasons.append("CHECK_ENTRY_CONDITIONS: not_met")
        elif state.state == self.SHORT_ARMED:
            reasons.append("STATE: SHORT_ARMED")
            short_entry_ok = bearish_crossover and (trend_short_ok if trend_filter_enabled else True)
            if short_entry_ok:
                signal = "SELL"
                confidence = self._entry_confidence(
                    checks=[True, True, trend_short_ok if trend_filter_enabled else True],
                    trend_filter_enabled=trend_filter_enabled,
                )
                reasons.append("CHECK_RSI_OVERBOUGHT: pass")
                reasons.append("CHECK_EMA_BEARISH_CROSSOVER: pass")
                if trend_filter_enabled:
                    reasons.append("CHECK_TREND_FILTER_SHORT: pass")
                self._enter_short(state, price, stop_pct, target_pct)
                reasons.append("STATE_TRANSITION: SHORT_ARMED -> SHORT_IN_TRADE")
            else:
                confidence = self._hold_confidence(
                    oversold_hit=oversold_hit,
                    overbought_hit=overbought_hit,
                    bullish_crossover=bullish_crossover,
                    bearish_crossover=bearish_crossover,
                    trend_filter_enabled=trend_filter_enabled,
                    trend_long_ok=trend_long_ok,
                    trend_short_ok=trend_short_ok,
                )
                reasons.append("CHECK_ENTRY_CONDITIONS: not_met")
        elif state.state == self.LONG_IN_TRADE:
            reasons.append("STATE: LONG_IN_TRADE")
            stop_loss = state.stop_loss if state.stop_loss is not None else round(price * (1.0 - stop_pct), 2)
            target = state.target if state.target is not None else round(price * (1.0 + target_pct), 2)
            if price <= stop_loss:
                signal = "SELL"
                confidence = 65
                reasons.append("CHECK_STOP_LOSS_LONG: pass")
                self._clear_position(state)
                reasons.append("STATE_TRANSITION: LONG_IN_TRADE -> WAITING")
            elif price >= target:
                signal = "SELL"
                confidence = 65
                reasons.append("CHECK_TAKE_PROFIT_LONG: pass")
                self._clear_position(state)
                reasons.append("STATE_TRANSITION: LONG_IN_TRADE -> WAITING")
            elif long_exit_ready:
                signal = "SELL"
                confidence = 60
                reasons.append("CHECK_EXIT_RSI_LONG: pass")
                self._clear_position(state)
                reasons.append("STATE_TRANSITION: LONG_IN_TRADE -> WAITING")
            else:
                confidence = self._hold_confidence(
                    oversold_hit=oversold_hit,
                    overbought_hit=overbought_hit,
                    bullish_crossover=bullish_crossover,
                    bearish_crossover=bearish_crossover,
                    trend_filter_enabled=trend_filter_enabled,
                    trend_long_ok=trend_long_ok,
                    trend_short_ok=trend_short_ok,
                )
                reasons.append("CHECK_EXIT_CONDITIONS: not_met")
        elif state.state == self.SHORT_IN_TRADE:
            reasons.append("STATE: SHORT_IN_TRADE")
            stop_loss = state.stop_loss if state.stop_loss is not None else round(price * (1.0 + stop_pct), 2)
            target = state.target if state.target is not None else round(price * (1.0 - target_pct), 2)
            if price >= stop_loss:
                signal = "BUY"
                confidence = 65
                reasons.append("CHECK_STOP_LOSS_SHORT: pass")
                self._clear_position(state)
                reasons.append("STATE_TRANSITION: SHORT_IN_TRADE -> WAITING")
            elif price <= target:
                signal = "BUY"
                confidence = 65
                reasons.append("CHECK_TAKE_PROFIT_SHORT: pass")
                self._clear_position(state)
                reasons.append("STATE_TRANSITION: SHORT_IN_TRADE -> WAITING")
            elif short_exit_ready:
                signal = "BUY"
                confidence = 60
                reasons.append("CHECK_EXIT_RSI_SHORT: pass")
                self._clear_position(state)
                reasons.append("STATE_TRANSITION: SHORT_IN_TRADE -> WAITING")
            else:
                confidence = self._hold_confidence(
                    oversold_hit=oversold_hit,
                    overbought_hit=overbought_hit,
                    bullish_crossover=bullish_crossover,
                    bearish_crossover=bearish_crossover,
                    trend_filter_enabled=trend_filter_enabled,
                    trend_long_ok=trend_long_ok,
                    trend_short_ok=trend_short_ok,
                )
                reasons.append("CHECK_EXIT_CONDITIONS: not_met")

        if signal == "HOLD" and not reasons:
            confidence = self._hold_confidence(
                oversold_hit=oversold_hit,
                overbought_hit=overbought_hit,
                bullish_crossover=bullish_crossover,
                bearish_crossover=bearish_crossover,
                trend_filter_enabled=trend_filter_enabled,
                trend_long_ok=trend_long_ok,
                trend_short_ok=trend_short_ok,
            )
            reasons.append("CHECK_ENTRY_CONDITIONS: not_met")

        if not trend_filter_enabled:
            reasons.append("CHECK_TREND_FILTER: disabled")
        if trend_filter_enabled and signal == "HOLD":
            if not trend_long_ok and not trend_short_ok:
                reasons.append("CHECK_TREND_FILTER: blocked")

        reasons.append(
            (
                "INDICATORS: "
                f"RSI={rsi:.2f}, "
                f"EMA_FAST={ema_fast:.4f}, "
                f"EMA_SLOW={ema_slow:.4f}, "
                f"EMA200={ema200:.4f}, "
                f"OVERSOLD={oversold:.2f}, "
                f"EXIT_RSI={exit_rsi:.2f}, "
                f"OVERBOUGHT={overbought:.2f}"
            )
        )

        stop_loss = round(price * (1.0 - stop_pct), 2)
        target = round(price * (1.0 + target_pct), 2)

        return TradeSignal(
            symbol=symbol,
            signal=signal,
            confidence=min(100, max(0, confidence)),
            price=price,
            rsi=rsi,
            ema12=ema_fast,
            ema26=ema_slow,
            stop_loss=stop_loss,
            target=target,
            reasons=reasons,
        )

    def reset_state(self, symbol: str | None = None) -> None:
        if symbol is None:
            self._states.clear()
            return
        self._states.pop(symbol, None)

    def _calculate_rsi(self, close_series: Any, period: int) -> Any:
        delta = close_series.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def _entry_confidence(self, checks: list[bool], trend_filter_enabled: bool) -> int:
        required = 3 if trend_filter_enabled else 2
        met = sum(1 for check in checks if check)
        ratio = met / max(1, required)
        return int(round(55 + (ratio * 40)))

    def _enter_long(self, state: _RSIMeanReversionState, price: float, stop_pct: float, target_pct: float) -> None:
        state.state = self.LONG_IN_TRADE
        state.entry_price = price
        state.stop_loss = round(price * (1.0 - stop_pct), 2)
        state.target = round(price * (1.0 + target_pct), 2)

    def _enter_short(self, state: _RSIMeanReversionState, price: float, stop_pct: float, target_pct: float) -> None:
        state.state = self.SHORT_IN_TRADE
        state.entry_price = price
        state.stop_loss = round(price * (1.0 + stop_pct), 2)
        state.target = round(price * (1.0 - target_pct), 2)

    def _clear_position(self, state: _RSIMeanReversionState) -> None:
        state.state = self.WAITING
        state.entry_price = None
        state.stop_loss = None
        state.target = None

    def _get_state(self, symbol: str) -> _RSIMeanReversionState:
        state = self._states.get(symbol)
        if state is None:
            state = _RSIMeanReversionState()
            self._states[symbol] = state
        return state

    def _hold_confidence(
        self,
        *,
        oversold_hit: bool,
        overbought_hit: bool,
        bullish_crossover: bool,
        bearish_crossover: bool,
        trend_filter_enabled: bool,
        trend_long_ok: bool,
        trend_short_ok: bool,
    ) -> int:
        agreement = 0
        agreement += 1 if oversold_hit or overbought_hit else 0
        agreement += 1 if bullish_crossover or bearish_crossover else 0
        if trend_filter_enabled:
            agreement += 1 if trend_long_ok or trend_short_ok else 0
        total = 3 if trend_filter_enabled else 2
        return int(round(30 + (agreement / total) * 30))

    def _validate_parameters(self) -> None:
        rsi_period = _safe_int(self._params.get("rsi_period"), 14)
        oversold = _safe_float(self._params.get("oversold"), 30.0)
        exit_rsi = _safe_float(self._params.get("exit_rsi"), 50.0)
        overbought = _safe_float(self._params.get("overbought"), 70.0)
        fast_ema = _safe_int(self._params.get("fast_ema"), 12)
        slow_ema = _safe_int(self._params.get("slow_ema"), 26)

        if rsi_period <= 1:
            raise ValueError("Invalid RSI Mean Reversion configuration: rsi_period must be > 1.")
        if not (oversold < exit_rsi):
            raise ValueError("Invalid RSI Mean Reversion configuration: oversold must be < exit_rsi.")
        if not (exit_rsi < overbought):
            raise ValueError("Invalid RSI Mean Reversion configuration: exit_rsi must be < overbought.")
        if not (fast_ema < slow_ema):
            raise ValueError("Invalid RSI Mean Reversion configuration: fast_ema must be < slow_ema.")

    def _merge_defaults(self, overrides: dict[str, Any] | None) -> dict[str, Any]:
        merged = {item.key: item.default for item in self.parameters}
        if overrides:
            for key, value in overrides.items():
                if key in merged:
                    merged[key] = value
        return merged


class EMATrendFollowingBacktestStrategy(BacktestStrategy):
    strategy_id = "ema_trend_following"
    name = "TradePilotAI EMA Trend Following"
    description = "Trend-following strategy using EMA crossovers with optional EMA200 and ADX confirmation."
    category = "Trend Following"
    version = "1.0"
    author = "TradePilotAI"
    asset_class = "Equities"
    primary_timeframe = "4h"
    supported_timeframes = ["1h", "4h"]
    supported_assets = ["Equities", "ETFs", "Indices"]
    supports_long = True
    supports_short = True
    risk_profile = "Medium"
    indicators = ["EMA Fast", "EMA Slow", "EMA Trend", "ADX"]
    best_market = "Trending"
    best_timeframes = ["Daily", "4 Hour"]
    strengths = ["Captures sustained trends", "Simple rules", "Low signal noise"]
    weaknesses = ["Can underperform in sideways markets", "Late entries after reversals"]
    recommended_risk = "Medium"

    def __init__(self, parameters: dict[str, Any] | None = None) -> None:
        self._params = self._merge_defaults(parameters)
        self._validate_parameters()

    @property
    def parameters(self) -> list[StrategyParameter]:
        return [
            StrategyParameter("fast_ema", "Fast EMA", "int", 20, minimum=2, maximum=150, step=1),
            StrategyParameter("slow_ema", "Slow EMA", "int", 50, minimum=3, maximum=300, step=1),
            StrategyParameter("trend_ema", "Trend EMA", "int", 200, minimum=20, maximum=500, step=1),
            StrategyParameter("adx_period", "ADX Period", "int", 14, minimum=2, maximum=100, step=1),
            StrategyParameter("adx_threshold", "ADX Threshold", "float", 20.0, minimum=10.0, maximum=50.0, step=1.0),
            StrategyParameter("trend_filter_enabled", "Trend Filter Enabled", "bool", True),
            StrategyParameter("adx_filter_enabled", "ADX Filter Enabled", "bool", True),
            StrategyParameter("stop_loss_pct", "Stop Loss %", "float", 2.0, minimum=0.1, maximum=20.0, step=0.1),
            StrategyParameter("target_pct", "Target %", "float", 4.0, minimum=0.1, maximum=40.0, step=0.1),
        ]

    def evaluate(self, symbol: str, data: Any) -> dict[str, Any]:
        frame = data.copy() if hasattr(data, "copy") else data
        if hasattr(frame, "columns") and hasattr(frame.columns, "nlevels") and frame.columns.nlevels > 1:
            frame.columns = frame.columns.get_level_values(0)

        if not hasattr(frame, "iloc") or len(frame) < 2:
            raise ValueError("EMA Trend Following requires at least 2 candles for crossover detection.")

        fast_period = _safe_int(self._params.get("fast_ema"), 20)
        slow_period = _safe_int(self._params.get("slow_ema"), 50)
        trend_period = _safe_int(self._params.get("trend_ema"), 200)
        adx_period = _safe_int(self._params.get("adx_period"), 14)
        adx_threshold = _safe_float(self._params.get("adx_threshold"), 20.0)
        trend_filter_enabled = bool(self._params.get("trend_filter_enabled", True))
        adx_filter_enabled = bool(self._params.get("adx_filter_enabled", True))

        close_series = frame["Close"].astype(float)
        high_series = frame["High"].astype(float) if "High" in frame.columns else close_series
        low_series = frame["Low"].astype(float) if "Low" in frame.columns else close_series

        fast_col = f"EMA{fast_period}"
        slow_col = f"EMA{slow_period}"
        trend_col = f"EMA{trend_period}"
        adx_col = f"ADX{adx_period}"

        if fast_col not in frame.columns:
            frame[fast_col] = close_series.ewm(span=max(2, fast_period), adjust=False).mean()
        if slow_col not in frame.columns:
            frame[slow_col] = close_series.ewm(span=max(3, slow_period), adjust=False).mean()
        if trend_col not in frame.columns:
            frame[trend_col] = close_series.ewm(span=max(20, trend_period), adjust=False).mean()
        if adx_col not in frame.columns:
            frame[adx_col] = self._calculate_adx(high_series, low_series, close_series, period=max(2, adx_period))

        latest = frame.iloc[-1]
        previous = frame.iloc[-2]

        price = _safe_float(latest.get("Close"), 0.0)
        ema_fast = _safe_float(latest.get(fast_col), price)
        ema_slow = _safe_float(latest.get(slow_col), price)
        ema_trend = _safe_float(latest.get(trend_col), price)
        adx = _safe_float(latest.get(adx_col), adx_threshold)

        previous_ema_fast = _safe_float(previous.get(fast_col), ema_fast)
        previous_ema_slow = _safe_float(previous.get(slow_col), ema_slow)

        bullish_crossover = previous_ema_fast <= previous_ema_slow and ema_fast > ema_slow
        bearish_crossover = previous_ema_fast >= previous_ema_slow and ema_fast < ema_slow

        trend_long_ok = price > ema_trend
        trend_short_ok = price < ema_trend
        adx_ok = adx > adx_threshold

        long_entry_ok = bullish_crossover
        short_entry_ok = bearish_crossover
        if trend_filter_enabled:
            long_entry_ok = long_entry_ok and trend_long_ok
            short_entry_ok = short_entry_ok and trend_short_ok
        if adx_filter_enabled:
            long_entry_ok = long_entry_ok and adx_ok
            short_entry_ok = short_entry_ok and adx_ok

        long_exit_ready = bearish_crossover
        short_exit_ready = bullish_crossover

        return {
            "price": price,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "ema_trend": ema_trend,
            "adx": adx,
            "adx_threshold": adx_threshold,
            "previous_ema_fast": previous_ema_fast,
            "previous_ema_slow": previous_ema_slow,
            "bullish_crossover": bullish_crossover,
            "bearish_crossover": bearish_crossover,
            "trend_filter_enabled": trend_filter_enabled,
            "adx_filter_enabled": adx_filter_enabled,
            "trend_long_ok": trend_long_ok,
            "trend_short_ok": trend_short_ok,
            "adx_ok": adx_ok,
            "long_entry_ok": long_entry_ok,
            "short_entry_ok": short_entry_ok,
            "long_exit_ready": long_exit_ready,
            "short_exit_ready": short_exit_ready,
            "parameters": dict(self._params),
        }

    def generate_signal(self, symbol: str, context: dict[str, Any]) -> TradeSignal:
        price = _safe_float(context.get("price"), 0.0)
        ema_fast = _safe_float(context.get("ema_fast"), price)
        ema_slow = _safe_float(context.get("ema_slow"), price)
        ema_trend = _safe_float(context.get("ema_trend"), price)
        adx = _safe_float(context.get("adx"), 0.0)
        adx_threshold = _safe_float(context.get("adx_threshold"), _safe_float(self._params.get("adx_threshold"), 20.0))

        trend_filter_enabled = bool(context.get("trend_filter_enabled", self._params.get("trend_filter_enabled", True)))
        adx_filter_enabled = bool(context.get("adx_filter_enabled", self._params.get("adx_filter_enabled", True)))

        bullish_crossover = bool(context.get("bullish_crossover", False))
        bearish_crossover = bool(context.get("bearish_crossover", False))
        trend_long_ok = bool(context.get("trend_long_ok", price > ema_trend))
        trend_short_ok = bool(context.get("trend_short_ok", price < ema_trend))
        adx_ok = bool(context.get("adx_ok", adx > adx_threshold))
        long_entry_ok = bool(context.get("long_entry_ok", False))
        short_entry_ok = bool(context.get("short_entry_ok", False))
        long_exit_ready = bool(context.get("long_exit_ready", bearish_crossover))
        short_exit_ready = bool(context.get("short_exit_ready", bullish_crossover))
        in_position_long = bool(context.get("in_position_long", False))
        in_position_short = bool(context.get("in_position_short", False))

        stop_pct = max(0.1, _safe_float(self._params.get("stop_loss_pct"), 2.0)) / 100.0
        target_pct = max(0.1, _safe_float(self._params.get("target_pct"), 4.0)) / 100.0

        signal = "HOLD"
        confidence = 35
        reasons: list[str] = []

        if long_entry_ok:
            signal = "BUY"
            confidence = self._entry_confidence(
                checks=[bullish_crossover, trend_long_ok if trend_filter_enabled else True, adx_ok if adx_filter_enabled else True],
                trend_filter_enabled=trend_filter_enabled,
                adx_filter_enabled=adx_filter_enabled,
            )
            reasons.append("CHECK_EMA_BULLISH_CROSSOVER: pass")
            if trend_filter_enabled:
                reasons.append("CHECK_TREND_FILTER_LONG: pass")
            if adx_filter_enabled:
                reasons.append("CHECK_ADX_FILTER: pass")
        elif short_entry_ok:
            signal = "SELL"
            confidence = self._entry_confidence(
                checks=[bearish_crossover, trend_short_ok if trend_filter_enabled else True, adx_ok if adx_filter_enabled else True],
                trend_filter_enabled=trend_filter_enabled,
                adx_filter_enabled=adx_filter_enabled,
            )
            reasons.append("CHECK_EMA_BEARISH_CROSSOVER: pass")
            if trend_filter_enabled:
                reasons.append("CHECK_TREND_FILTER_SHORT: pass")
            if adx_filter_enabled:
                reasons.append("CHECK_ADX_FILTER: pass")
        elif in_position_long and long_exit_ready and not short_entry_ok:
            signal = "SELL"
            confidence = 62
            reasons.append("CHECK_EXIT_EMA_CROSS_LONG: pass")
        elif in_position_short and short_exit_ready and not long_entry_ok:
            signal = "BUY"
            confidence = 62
            reasons.append("CHECK_EXIT_EMA_CROSS_SHORT: pass")
        else:
            confidence = self._hold_confidence(
                bullish_crossover=bullish_crossover,
                bearish_crossover=bearish_crossover,
                trend_filter_enabled=trend_filter_enabled,
                trend_long_ok=trend_long_ok,
                trend_short_ok=trend_short_ok,
                adx_filter_enabled=adx_filter_enabled,
                adx_ok=adx_ok,
            )
            reasons.append("CHECK_ENTRY_CONDITIONS: not_met")

        if not trend_filter_enabled:
            reasons.append("CHECK_TREND_FILTER: disabled")
        elif signal == "HOLD" and not trend_long_ok and not trend_short_ok:
            reasons.append("CHECK_TREND_FILTER: blocked")

        if not adx_filter_enabled:
            reasons.append("CHECK_ADX_FILTER: disabled")
        elif signal == "HOLD" and not adx_ok:
            reasons.append("CHECK_ADX_FILTER: blocked")

        reasons.append(
            (
                "INDICATORS: "
                f"EMA_FAST={ema_fast:.4f}, "
                f"EMA_SLOW={ema_slow:.4f}, "
                f"EMA_TREND={ema_trend:.4f}, "
                f"ADX={adx:.2f}, "
                f"ADX_THRESHOLD={adx_threshold:.2f}"
            )
        )

        stop_loss = round(price * (1.0 - stop_pct), 2)
        target = round(price * (1.0 + target_pct), 2)

        return TradeSignal(
            symbol=symbol,
            signal=signal,
            confidence=min(100, max(0, confidence)),
            price=price,
            rsi=adx,
            ema12=ema_fast,
            ema26=ema_slow,
            stop_loss=stop_loss,
            target=target,
            reasons=reasons,
        )

    def _calculate_adx(self, high: Any, low: Any, close: Any, period: int) -> Any:
        up_move = high.diff()
        down_move = -low.diff()

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

        tr_components = [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ]
        tr = tr_components[0]
        for component in tr_components[1:]:
            tr = tr.combine(component, max)

        atr = tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        plus_di = 100 * plus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr.replace(0, float("nan"))
        minus_di = 100 * minus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr.replace(0, float("nan"))

        dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, float("nan"))).fillna(0.0)
        adx = dx.ewm(alpha=1 / period, min_periods=period, adjust=False).mean().fillna(20.0)
        return adx

    def _entry_confidence(self, *, checks: list[bool], trend_filter_enabled: bool, adx_filter_enabled: bool) -> int:
        required = 1
        required += 1 if trend_filter_enabled else 0
        required += 1 if adx_filter_enabled else 0
        met = sum(1 for check in checks if check)
        ratio = met / max(1, required)
        return int(round(55 + (ratio * 40)))

    def _hold_confidence(
        self,
        *,
        bullish_crossover: bool,
        bearish_crossover: bool,
        trend_filter_enabled: bool,
        trend_long_ok: bool,
        trend_short_ok: bool,
        adx_filter_enabled: bool,
        adx_ok: bool,
    ) -> int:
        agreement = 1 if bullish_crossover or bearish_crossover else 0
        total = 1
        if trend_filter_enabled:
            total += 1
            agreement += 1 if trend_long_ok or trend_short_ok else 0
        if adx_filter_enabled:
            total += 1
            agreement += 1 if adx_ok else 0
        return int(round(25 + (agreement / max(1, total)) * 30))

    def _validate_parameters(self) -> None:
        fast_ema = _safe_int(self._params.get("fast_ema"), 20)
        slow_ema = _safe_int(self._params.get("slow_ema"), 50)
        trend_ema = _safe_int(self._params.get("trend_ema"), 200)
        adx_period = _safe_int(self._params.get("adx_period"), 14)
        adx_threshold = _safe_float(self._params.get("adx_threshold"), 20.0)

        if not (fast_ema < slow_ema):
            raise ValueError("Invalid EMA Trend Following configuration: fast_ema must be < slow_ema.")
        if not (slow_ema < trend_ema):
            raise ValueError("Invalid EMA Trend Following configuration: slow_ema must be < trend_ema.")
        if adx_period <= 1:
            raise ValueError("Invalid EMA Trend Following configuration: adx_period must be > 1.")
        if not (10.0 <= adx_threshold <= 50.0):
            raise ValueError("Invalid EMA Trend Following configuration: adx_threshold must be between 10 and 50.")

    def _merge_defaults(self, overrides: dict[str, Any] | None) -> dict[str, Any]:
        merged = {item.key: item.default for item in self.parameters}
        if overrides:
            for key, value in overrides.items():
                if key in merged:
                    merged[key] = value
        return merged


class MACDMomentumBacktestStrategy(BacktestStrategy):
    strategy_id = "macd_momentum"
    name = "TradePilotAI MACD Momentum"
    description = "Momentum strategy using MACD crossovers with optional trend and histogram confirmation."
    category = "Momentum"
    version = "1.0"
    author = "TradePilotAI"
    asset_class = "Equities"
    primary_timeframe = "4h"
    supported_timeframes = ["1h", "4h"]
    supported_assets = ["Equities", "ETFs", "Indices"]
    supports_long = True
    supports_short = True
    risk_profile = "Medium"
    indicators = ["MACD", "Signal", "Histogram", "EMA200"]
    best_market = "Strong Trending Markets"
    best_timeframes = ["Daily", "4 Hour"]
    strengths = ["Captures sustained momentum", "Reduces false trend entries", "Excellent for swing trading"]
    weaknesses = ["Can lag after sharp reversals", "May generate fewer signals"]
    recommended_risk = "Medium"

    def __init__(self, parameters: dict[str, Any] | None = None) -> None:
        self._params = self._merge_defaults(parameters)
        self._validate_parameters()

    @property
    def parameters(self) -> list[StrategyParameter]:
        return [
            StrategyParameter("macd_fast_ema", "MACD Fast EMA", "int", 12, minimum=2, maximum=150, step=1),
            StrategyParameter("macd_slow_ema", "MACD Slow EMA", "int", 26, minimum=3, maximum=300, step=1),
            StrategyParameter("signal_period", "Signal Period", "int", 9, minimum=2, maximum=100, step=1),
            StrategyParameter("trend_ema", "Trend EMA", "int", 200, minimum=20, maximum=500, step=1),
            StrategyParameter("trend_filter_enabled", "Trend Filter Enabled", "bool", True),
            StrategyParameter("histogram_confirmation", "Histogram Confirmation", "bool", True),
        ]

    def evaluate(self, symbol: str, data: Any) -> dict[str, Any]:
        frame = data.copy() if hasattr(data, "copy") else data
        if hasattr(frame, "columns") and hasattr(frame.columns, "nlevels") and frame.columns.nlevels > 1:
            frame.columns = frame.columns.get_level_values(0)

        if not hasattr(frame, "iloc") or len(frame) < 2:
            raise ValueError("MACD Momentum requires at least 2 candles for crossover detection.")

        fast_period = _safe_int(self._params.get("macd_fast_ema"), 12)
        slow_period = _safe_int(self._params.get("macd_slow_ema"), 26)
        signal_period = _safe_int(self._params.get("signal_period"), 9)
        trend_period = _safe_int(self._params.get("trend_ema"), 200)

        close_series = frame["Close"].astype(float)
        fast_col = f"EMA{fast_period}"
        slow_col = f"EMA{slow_period}"
        trend_col = f"EMA{trend_period}"
        macd_col = f"MACD{fast_period}_{slow_period}"
        signal_col = f"MACD_SIGNAL{signal_period}"
        histogram_col = f"MACD_HISTOGRAM{signal_period}"

        if fast_col not in frame.columns:
            frame[fast_col] = close_series.ewm(span=max(2, fast_period), adjust=False).mean()
        if slow_col not in frame.columns:
            frame[slow_col] = close_series.ewm(span=max(3, slow_period), adjust=False).mean()
        if trend_col not in frame.columns:
            frame[trend_col] = close_series.ewm(span=max(20, trend_period), adjust=False).mean()

        macd_series = frame[fast_col].astype(float) - frame[slow_col].astype(float)
        signal_series = macd_series.ewm(span=max(2, signal_period), adjust=False).mean()
        histogram_series = macd_series - signal_series

        frame[macd_col] = macd_series
        frame[signal_col] = signal_series
        frame[histogram_col] = histogram_series

        latest = frame.iloc[-1]
        previous = frame.iloc[-2]

        price = _safe_float(latest.get("Close"), 0.0)
        ema_fast = _safe_float(latest.get(fast_col), price)
        ema_slow = _safe_float(latest.get(slow_col), price)
        ema_trend = _safe_float(latest.get(trend_col), price)
        macd_value = _safe_float(latest.get(macd_col), 0.0)
        macd_signal = _safe_float(latest.get(signal_col), 0.0)
        histogram = _safe_float(latest.get(histogram_col), macd_value - macd_signal)
        previous_macd = _safe_float(previous.get(macd_col), macd_value)
        previous_signal = _safe_float(previous.get(signal_col), macd_signal)
        previous_histogram = _safe_float(previous.get(histogram_col), histogram)

        return {
            "price": price,
            "ema12": ema_fast,
            "ema26": ema_slow,
            "ema_trend": ema_trend,
            "macd": macd_value,
            "macd_signal": macd_signal,
            "macd_histogram": histogram,
            "previous_macd": previous_macd,
            "previous_macd_signal": previous_signal,
            "previous_macd_histogram": previous_histogram,
            "macd_cross_up": previous_macd <= previous_signal and macd_value > macd_signal,
            "macd_cross_down": previous_macd >= previous_signal and macd_value < macd_signal,
            "macd_above_zero": macd_value > 0,
            "macd_below_zero": macd_value < 0,
            "histogram_increasing": histogram > previous_histogram,
            "histogram_decreasing": histogram < previous_histogram,
            "trend_filter_enabled": bool(self._params.get("trend_filter_enabled", True)),
            "histogram_confirmation": bool(self._params.get("histogram_confirmation", True)),
            "trend_long_ok": price > ema_trend,
            "trend_short_ok": price < ema_trend,
            "parameters": dict(self._params),
        }

    def generate_signal(self, symbol: str, context: dict[str, Any]) -> TradeSignal:
        price = _safe_float(context.get("price"), 0.0)
        ema12 = _safe_float(context.get("ema12"), price)
        ema26 = _safe_float(context.get("ema26"), price)
        ema_trend = _safe_float(context.get("ema_trend"), price)
        macd_value = _safe_float(context.get("macd"), 0.0)
        macd_signal = _safe_float(context.get("macd_signal"), 0.0)
        histogram = _safe_float(context.get("macd_histogram"), macd_value - macd_signal)
        previous_macd = _safe_float(context.get("previous_macd"), macd_value)
        previous_signal = _safe_float(context.get("previous_macd_signal"), macd_signal)
        previous_histogram = _safe_float(context.get("previous_macd_histogram"), histogram)

        trend_filter_enabled = bool(context.get("trend_filter_enabled", self._params.get("trend_filter_enabled", True)))
        histogram_confirmation = bool(context.get("histogram_confirmation", self._params.get("histogram_confirmation", True)))

        macd_cross_up = bool(context.get("macd_cross_up", previous_macd <= previous_signal and macd_value > macd_signal))
        macd_cross_down = bool(context.get("macd_cross_down", previous_macd >= previous_signal and macd_value < macd_signal))
        macd_above_zero = bool(context.get("macd_above_zero", macd_value > 0))
        macd_below_zero = bool(context.get("macd_below_zero", macd_value < 0))
        histogram_increasing = bool(context.get("histogram_increasing", histogram > previous_histogram))
        histogram_decreasing = bool(context.get("histogram_decreasing", histogram < previous_histogram))
        trend_long_ok = bool(context.get("trend_long_ok", price > ema_trend))
        trend_short_ok = bool(context.get("trend_short_ok", price < ema_trend))
        in_position_long = bool(context.get("in_position_long", False))
        in_position_short = bool(context.get("in_position_short", False))

        long_entry_checks = [macd_cross_up, macd_above_zero]
        short_entry_checks = [macd_cross_down, macd_below_zero]
        if trend_filter_enabled:
            long_entry_checks.append(trend_long_ok)
            short_entry_checks.append(trend_short_ok)
        if histogram_confirmation:
            long_entry_checks.append(histogram_increasing)
            short_entry_checks.append(histogram_decreasing)

        long_entry_ok = all(long_entry_checks)
        short_entry_ok = all(short_entry_checks)
        long_exit_ready = macd_cross_down
        short_exit_ready = macd_cross_up

        signal = "HOLD"
        confidence = 38
        reasons: list[str] = []

        if long_entry_ok:
            signal = "BUY"
            confidence = self._entry_confidence(
                checks=long_entry_checks,
                trend_filter_enabled=trend_filter_enabled,
                histogram_confirmation=histogram_confirmation,
            )
            reasons.append("CHECK_MACD_BULLISH_CROSSOVER: pass")
            reasons.append("CHECK_MACD_ABOVE_ZERO: pass")
            if trend_filter_enabled:
                reasons.append("CHECK_TREND_FILTER_LONG: pass")
            if histogram_confirmation:
                reasons.append("CHECK_HISTOGRAM_LONG: pass")
        elif short_entry_ok:
            signal = "SELL"
            confidence = self._entry_confidence(
                checks=short_entry_checks,
                trend_filter_enabled=trend_filter_enabled,
                histogram_confirmation=histogram_confirmation,
            )
            reasons.append("CHECK_MACD_BEARISH_CROSSOVER: pass")
            reasons.append("CHECK_MACD_BELOW_ZERO: pass")
            if trend_filter_enabled:
                reasons.append("CHECK_TREND_FILTER_SHORT: pass")
            if histogram_confirmation:
                reasons.append("CHECK_HISTOGRAM_SHORT: pass")
        elif in_position_long and long_exit_ready and not short_entry_ok:
            signal = "SELL"
            confidence = 60
            reasons.append("CHECK_EXIT_MACD_CROSS_LONG: pass")
        elif in_position_short and short_exit_ready and not long_entry_ok:
            signal = "BUY"
            confidence = 60
            reasons.append("CHECK_EXIT_MACD_CROSS_SHORT: pass")
        else:
            confidence = self._hold_confidence(
                macd_cross_up=macd_cross_up,
                macd_cross_down=macd_cross_down,
                macd_above_zero=macd_above_zero,
                macd_below_zero=macd_below_zero,
                trend_filter_enabled=trend_filter_enabled,
                trend_long_ok=trend_long_ok,
                trend_short_ok=trend_short_ok,
                histogram_confirmation=histogram_confirmation,
                histogram_increasing=histogram_increasing,
                histogram_decreasing=histogram_decreasing,
            )
            reasons.append("CHECK_ENTRY_CONDITIONS: not_met")

        if not trend_filter_enabled:
            reasons.append("CHECK_TREND_FILTER: disabled")
        elif signal == "HOLD" and not trend_long_ok and not trend_short_ok:
            reasons.append("CHECK_TREND_FILTER: blocked")

        if not histogram_confirmation:
            reasons.append("CHECK_HISTOGRAM: disabled")
        elif signal == "HOLD" and not histogram_increasing and not histogram_decreasing:
            reasons.append("CHECK_HISTOGRAM: blocked")

        reasons.append(
            (
                "INDICATORS: "
                f"MACD={macd_value:.4f}, "
                f"SIGNAL={macd_signal:.4f}, "
                f"HISTOGRAM={histogram:.4f}, "
                f"EMA200={ema_trend:.4f}"
            )
        )

        stop_loss = round(price * 0.98, 2)
        target = round(price * 1.06, 2)

        return TradeSignal(
            symbol=symbol,
            signal=signal,
            confidence=min(100, max(0, confidence)),
            price=price,
            rsi=macd_value,
            ema12=ema12,
            ema26=ema26,
            stop_loss=stop_loss,
            target=target,
            reasons=reasons,
        )

    def _merge_defaults(self, overrides: dict[str, Any] | None) -> dict[str, Any]:
        merged = {item.key: item.default for item in self.parameters}
        if overrides:
            for key, value in overrides.items():
                if key in merged:
                    merged[key] = value
        return merged

    def _entry_confidence(self, *, checks: list[bool], trend_filter_enabled: bool, histogram_confirmation: bool) -> int:
        required = 2
        required += 1 if trend_filter_enabled else 0
        required += 1 if histogram_confirmation else 0
        met = sum(1 for check in checks if check)
        ratio = met / max(1, required)
        return int(round(55 + (ratio * 40)))

    def _hold_confidence(
        self,
        *,
        macd_cross_up: bool,
        macd_cross_down: bool,
        macd_above_zero: bool,
        macd_below_zero: bool,
        trend_filter_enabled: bool,
        trend_long_ok: bool,
        trend_short_ok: bool,
        histogram_confirmation: bool,
        histogram_increasing: bool,
        histogram_decreasing: bool,
    ) -> int:
        total = 2
        agreement = 1 if macd_cross_up or macd_cross_down else 0
        agreement += 1 if macd_above_zero or macd_below_zero else 0
        if trend_filter_enabled:
            total += 1
            agreement += 1 if trend_long_ok or trend_short_ok else 0
        if histogram_confirmation:
            total += 1
            agreement += 1 if histogram_increasing or histogram_decreasing else 0
        return int(round(28 + (agreement / max(1, total)) * 34))

    def _validate_parameters(self) -> None:
        fast_ema = _safe_int(self._params.get("macd_fast_ema"), 12)
        slow_ema = _safe_int(self._params.get("macd_slow_ema"), 26)
        signal_period = _safe_int(self._params.get("signal_period"), 9)
        trend_ema = _safe_int(self._params.get("trend_ema"), 200)

        if not (fast_ema < slow_ema):
            raise ValueError("Invalid MACD Momentum configuration: macd_fast_ema must be < macd_slow_ema.")
        if signal_period <= 1:
            raise ValueError("Invalid MACD Momentum configuration: signal_period must be > 1.")
        if not (trend_ema > slow_ema):
            raise ValueError("Invalid MACD Momentum configuration: trend_ema must be > macd_slow_ema.")
