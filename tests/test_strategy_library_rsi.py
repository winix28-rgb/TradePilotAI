from __future__ import annotations

import pandas as pd
import pytest

from tradepilotai_os.backtesting.strategy_library.strategies import RSIMeanReversionBacktestStrategy


def _frame(rows: list[dict[str, float]]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(rows), freq="D")
    return pd.DataFrame(rows, index=index)


def _evaluate_signal(strategy: RSIMeanReversionBacktestStrategy, rows: list[dict[str, float]]):
    data = _frame(rows)
    context = strategy.evaluate("AAPL", data)
    return strategy.generate_signal("AAPL", context)


def _evaluate_signal_sequence(strategy: RSIMeanReversionBacktestStrategy, rows: list[dict[str, float]]) -> list[str]:
    signals: list[str] = []
    for index in range(1, len(rows)):
        signal = _evaluate_signal(strategy, rows[: index + 1])
        signals.append(signal.signal)
    return signals


def test_rsi_strategy_generates_buy_signal() -> None:
    strategy = RSIMeanReversionBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "RSI": 35.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 90.0},
            {"Close": 101.0, "RSI": 24.0, "EMA12": 101.5, "EMA26": 100.5, "EMA200": 91.0},
        ],
    )

    assert signal.signal == "BUY"
    assert signal.confidence >= 90


def test_rsi_strategy_keeps_long_armed_after_rsi_recovers_before_crossover() -> None:
    strategy = RSIMeanReversionBacktestStrategy()

    signals = _evaluate_signal_sequence(
        strategy,
        [
            {"Close": 100.0, "RSI": 45.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 90.0},
            {"Close": 99.0, "RSI": 28.0, "EMA12": 98.8, "EMA26": 99.2, "EMA200": 90.5},
            {"Close": 100.2, "RSI": 36.0, "EMA12": 99.0, "EMA26": 99.1, "EMA200": 91.0},
            {"Close": 101.5, "RSI": 42.0, "EMA12": 100.8, "EMA26": 100.1, "EMA200": 92.0},
        ],
    )

    assert signals == ["HOLD", "HOLD", "BUY"]


def test_rsi_strategy_generates_sell_signal() -> None:
    strategy = RSIMeanReversionBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 110.0, "RSI": 60.0, "EMA12": 111.0, "EMA26": 110.0, "EMA200": 120.0},
            {"Close": 109.0, "RSI": 78.0, "EMA12": 108.5, "EMA26": 109.5, "EMA200": 119.0},
        ],
    )

    assert signal.signal == "SELL"
    assert signal.confidence >= 90


def test_rsi_strategy_generates_no_signal_when_conditions_do_not_align() -> None:
    strategy = RSIMeanReversionBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "RSI": 45.0, "EMA12": 99.5, "EMA26": 99.7, "EMA200": 95.0},
            {"Close": 100.2, "RSI": 48.0, "EMA12": 99.6, "EMA26": 99.8, "EMA200": 95.2},
        ],
    )

    assert signal.signal == "HOLD"


@pytest.mark.parametrize(
    "parameters, message",
    [
        ({"rsi_period": 1}, "rsi_period must be > 1"),
        ({"oversold": 55.0, "exit_rsi": 50.0}, "oversold must be < exit_rsi"),
        ({"exit_rsi": 75.0, "overbought": 70.0}, "exit_rsi must be < overbought"),
        ({"fast_ema": 30, "slow_ema": 20}, "fast_ema must be < slow_ema"),
    ],
)
def test_rsi_strategy_rejects_invalid_parameters(parameters: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RSIMeanReversionBacktestStrategy(parameters)


def test_rsi_strategy_trend_filter_enabled_blocks_long_when_below_ema200() -> None:
    strategy = RSIMeanReversionBacktestStrategy({"trend_filter_enabled": True})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "RSI": 40.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 110.0},
            {"Close": 101.0, "RSI": 22.0, "EMA12": 101.8, "EMA26": 100.8, "EMA200": 111.0},
        ],
    )

    assert signal.signal == "HOLD"


def test_rsi_strategy_trend_filter_disabled_allows_long_without_ema200_gate() -> None:
    strategy = RSIMeanReversionBacktestStrategy({"trend_filter_enabled": False})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "RSI": 40.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 110.0},
            {"Close": 101.0, "RSI": 22.0, "EMA12": 101.8, "EMA26": 100.8, "EMA200": 111.0},
        ],
    )

    assert signal.signal == "BUY"


def test_rsi_strategy_includes_structured_explainability_payload() -> None:
    strategy = RSIMeanReversionBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "RSI": 35.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 90.0},
            {"Close": 101.0, "RSI": 24.0, "EMA12": 101.5, "EMA26": 100.5, "EMA200": 91.0},
        ],
    )

    reason_text = "\n".join(signal.reasons)
    assert "CHECK_RSI_OVERSOLD: pass" in reason_text
    assert "CHECK_EMA_BULLISH_CROSSOVER: pass" in reason_text
    assert "INDICATORS:" in reason_text
    assert signal.stop_loss > 0
    assert signal.target > 0


def test_rsi_strategy_regression_on_known_deterministic_data() -> None:
    strategy = RSIMeanReversionBacktestStrategy({"trend_filter_enabled": True})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "RSI": 52.0, "EMA12": 100.0, "EMA26": 99.9, "EMA200": 98.0},
            {"Close": 101.0, "RSI": 49.0, "EMA12": 100.1, "EMA26": 100.0, "EMA200": 99.0},
            {"Close": 102.0, "RSI": 47.0, "EMA12": 100.2, "EMA26": 100.1, "EMA200": 100.0},
            {"Close": 101.5, "RSI": 44.0, "EMA12": 100.3, "EMA26": 100.2, "EMA200": 100.2},
            {"Close": 101.2, "RSI": 46.0, "EMA12": 100.4, "EMA26": 100.3, "EMA200": 100.4},
        ],
    )

    assert signal.signal == "HOLD"
    assert 30 <= signal.confidence <= 70
