from __future__ import annotations

import pandas as pd
import pytest

from tradepilotai_os.backtesting.strategy_library.strategies import MACDMomentumBacktestStrategy


def _frame(closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(closes), freq="D")
    return pd.DataFrame({"Close": closes}, index=index)


def _evaluate_signal(strategy: MACDMomentumBacktestStrategy, closes: list[float]):
    data = _frame(closes)
    context = strategy.evaluate("AAPL", data)
    return strategy.generate_signal("AAPL", context)


def _base_context() -> dict[str, float | bool]:
    return {
        "price": 105.0,
        "ema12": 104.0,
        "ema26": 103.0,
        "ema_trend": 100.0,
        "macd": 1.2,
        "macd_signal": 1.0,
        "macd_histogram": 0.2,
        "previous_macd": 0.8,
        "previous_macd_signal": 0.9,
        "previous_macd_histogram": 0.1,
        "macd_cross_up": True,
        "macd_cross_down": False,
        "macd_above_zero": True,
        "macd_below_zero": False,
        "histogram_increasing": True,
        "histogram_decreasing": False,
        "trend_filter_enabled": True,
        "histogram_confirmation": True,
        "trend_long_ok": True,
        "trend_short_ok": False,
    }


def test_macd_strategy_generates_buy_signal() -> None:
    strategy = MACDMomentumBacktestStrategy()

    signal = strategy.generate_signal("AAPL", _base_context())

    assert signal.signal == "BUY"
    assert signal.confidence >= 90


def test_macd_strategy_generates_sell_signal() -> None:
    strategy = MACDMomentumBacktestStrategy()
    context = _base_context()
    context.update(
        {
            "price": 95.0,
            "ema12": 94.0,
            "ema26": 96.0,
            "ema_trend": 100.0,
            "macd": -1.4,
            "macd_signal": -1.1,
            "macd_histogram": -0.3,
            "previous_macd": -0.9,
            "previous_macd_signal": -1.0,
            "previous_macd_histogram": -0.1,
            "macd_cross_up": False,
            "macd_cross_down": True,
            "macd_above_zero": False,
            "macd_below_zero": True,
            "histogram_increasing": False,
            "histogram_decreasing": True,
            "trend_long_ok": False,
            "trend_short_ok": True,
        }
    )

    signal = strategy.generate_signal("AAPL", context)

    assert signal.signal == "SELL"
    assert signal.confidence >= 90


def test_macd_strategy_generates_hold_when_conditions_do_not_align() -> None:
    strategy = MACDMomentumBacktestStrategy()
    context = _base_context()
    context.update(
        {
            "macd_cross_up": False,
            "macd_cross_down": False,
            "macd_above_zero": True,
            "macd_below_zero": False,
            "histogram_increasing": False,
            "histogram_decreasing": False,
            "trend_long_ok": True,
            "trend_short_ok": False,
        }
    )

    signal = strategy.generate_signal("AAPL", context)

    assert signal.signal == "HOLD"


def test_macd_strategy_trend_filter_enabled_blocks_long_when_price_below_ema200() -> None:
    strategy = MACDMomentumBacktestStrategy({"trend_filter_enabled": True, "histogram_confirmation": False})
    context = _base_context()
    context.update({"trend_long_ok": False, "trend_short_ok": True})

    signal = strategy.generate_signal("AAPL", context)

    assert signal.signal == "HOLD"


def test_macd_strategy_trend_filter_disabled_allows_long_without_ema200_gate() -> None:
    strategy = MACDMomentumBacktestStrategy({"trend_filter_enabled": False, "histogram_confirmation": False})
    context = _base_context()
    context.update({"trend_filter_enabled": False, "histogram_confirmation": False, "trend_long_ok": False, "trend_short_ok": True})

    signal = strategy.generate_signal("AAPL", context)

    assert signal.signal == "BUY"


def test_macd_strategy_histogram_confirmation_enabled_blocks_signal_when_histogram_not_strengthening() -> None:
    strategy = MACDMomentumBacktestStrategy({"trend_filter_enabled": False, "histogram_confirmation": True})
    context = _base_context()
    context.update({"histogram_increasing": False, "histogram_decreasing": False})

    signal = strategy.generate_signal("AAPL", context)

    assert signal.signal == "HOLD"


def test_macd_strategy_histogram_confirmation_disabled_allows_signal_without_histogram_gate() -> None:
    strategy = MACDMomentumBacktestStrategy({"trend_filter_enabled": False, "histogram_confirmation": False})
    context = _base_context()
    context.update({"trend_filter_enabled": False, "histogram_confirmation": False, "histogram_increasing": False, "histogram_decreasing": False})

    signal = strategy.generate_signal("AAPL", context)

    assert signal.signal == "BUY"


@pytest.mark.parametrize(
    "parameters, message",
    [
        ({"macd_fast_ema": 30, "macd_slow_ema": 20}, "macd_fast_ema must be < macd_slow_ema"),
        ({"signal_period": 1}, "signal_period must be > 1"),
        ({"macd_slow_ema": 30, "trend_ema": 20}, "trend_ema must be > macd_slow_ema"),
    ],
)
def test_macd_strategy_rejects_invalid_parameters(parameters: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        MACDMomentumBacktestStrategy(parameters)


def test_macd_strategy_includes_structured_explainability_payload() -> None:
    strategy = MACDMomentumBacktestStrategy()

    signal = strategy.generate_signal("AAPL", _base_context())

    reason_text = "\n".join(signal.reasons)
    assert "CHECK_MACD_BULLISH_CROSSOVER: pass" in reason_text
    assert "CHECK_MACD_ABOVE_ZERO: pass" in reason_text
    assert "CHECK_TREND_FILTER_LONG: pass" in reason_text
    assert "CHECK_HISTOGRAM_LONG: pass" in reason_text
    assert "INDICATORS:" in reason_text
    assert signal.stop_loss > 0
    assert signal.target > 0


def test_macd_strategy_regression_on_known_deterministic_data() -> None:
    strategy = MACDMomentumBacktestStrategy()

    signal = _evaluate_signal(strategy, [100.0, 110.0])

    assert signal.signal == "BUY"
    assert 80 <= signal.confidence <= 100
