from __future__ import annotations

import pandas as pd
import pytest

from tradepilotai_os.backtesting.strategy_library.strategies import EMATrendFollowingBacktestStrategy


def _frame(rows: list[dict[str, float]]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(rows), freq="D")
    return pd.DataFrame(rows, index=index)


def _evaluate_signal(strategy: EMATrendFollowingBacktestStrategy, rows: list[dict[str, float]]):
    data = _frame(rows)
    context = strategy.evaluate("AAPL", data)
    return strategy.generate_signal("AAPL", context)


def test_ema_strategy_generates_buy_signal() -> None:
    strategy = EMATrendFollowingBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 95.0, "ADX14": 26.0},
            {"Close": 102.0, "High": 103.0, "Low": 101.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 96.0, "ADX14": 27.0},
        ],
    )

    assert signal.signal == "BUY"
    assert signal.confidence >= 90


def test_ema_strategy_generates_sell_signal() -> None:
    strategy = EMATrendFollowingBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 110.0, "High": 111.0, "Low": 109.0, "EMA20": 111.0, "EMA50": 110.0, "EMA200": 115.0, "ADX14": 28.0},
            {"Close": 108.0, "High": 109.0, "Low": 107.0, "EMA20": 108.5, "EMA50": 109.5, "EMA200": 114.0, "ADX14": 29.0},
        ],
    )

    assert signal.signal == "SELL"
    assert signal.confidence >= 90


def test_ema_strategy_generates_hold_when_conditions_do_not_align() -> None:
    strategy = EMATrendFollowingBacktestStrategy()

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.5, "EMA50": 99.8, "EMA200": 95.0, "ADX14": 18.0},
            {"Close": 100.5, "High": 101.5, "Low": 99.5, "EMA20": 99.7, "EMA50": 99.9, "EMA200": 95.2, "ADX14": 19.0},
        ],
    )

    assert signal.signal == "HOLD"


def test_ema_strategy_trend_filter_enabled_blocks_long_when_price_below_trend_ema() -> None:
    strategy = EMATrendFollowingBacktestStrategy({"trend_filter_enabled": True, "adx_filter_enabled": False})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 110.0, "ADX14": 30.0},
            {"Close": 101.0, "High": 102.0, "Low": 100.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 111.0, "ADX14": 31.0},
        ],
    )

    assert signal.signal == "HOLD"


def test_ema_strategy_trend_filter_disabled_allows_long_without_trend_ema_gate() -> None:
    strategy = EMATrendFollowingBacktestStrategy({"trend_filter_enabled": False, "adx_filter_enabled": False})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 110.0, "ADX14": 30.0},
            {"Close": 101.0, "High": 102.0, "Low": 100.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 111.0, "ADX14": 31.0},
        ],
    )

    assert signal.signal == "BUY"


def test_ema_strategy_adx_filter_enabled_blocks_signal_below_threshold() -> None:
    strategy = EMATrendFollowingBacktestStrategy({"adx_filter_enabled": True, "trend_filter_enabled": False})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 95.0, "ADX14": 16.0},
            {"Close": 101.0, "High": 102.0, "Low": 100.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 96.0, "ADX14": 18.0},
        ],
    )

    assert signal.signal == "HOLD"


def test_ema_strategy_adx_filter_disabled_allows_signal_without_adx_confirmation() -> None:
    strategy = EMATrendFollowingBacktestStrategy({"adx_filter_enabled": False, "trend_filter_enabled": False})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 95.0, "ADX14": 16.0},
            {"Close": 101.0, "High": 102.0, "Low": 100.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 96.0, "ADX14": 18.0},
        ],
    )

    assert signal.signal == "BUY"


@pytest.mark.parametrize(
    "parameters, message",
    [
        ({"fast_ema": 55, "slow_ema": 50}, "fast_ema must be < slow_ema"),
        ({"slow_ema": 250, "trend_ema": 200}, "slow_ema must be < trend_ema"),
        ({"adx_threshold": 9.0}, "adx_threshold must be between 10 and 50"),
        ({"adx_threshold": 51.0}, "adx_threshold must be between 10 and 50"),
    ],
)
def test_ema_strategy_rejects_invalid_parameters(parameters: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        EMATrendFollowingBacktestStrategy(parameters)


def test_ema_strategy_includes_structured_explainability_payload() -> None:
    strategy = EMATrendFollowingBacktestStrategy({"trend_filter_enabled": True, "adx_filter_enabled": True})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 95.0, "ADX14": 24.0},
            {"Close": 102.0, "High": 103.0, "Low": 101.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 96.0, "ADX14": 25.0},
        ],
    )

    reasons = "\n".join(signal.reasons)
    assert "CHECK_EMA_BULLISH_CROSSOVER: pass" in reasons
    assert "CHECK_TREND_FILTER_LONG: pass" in reasons
    assert "CHECK_ADX_FILTER: pass" in reasons
    assert "INDICATORS:" in reasons
    assert signal.stop_loss > 0
    assert signal.target > 0


def test_ema_strategy_regression_on_known_deterministic_data() -> None:
    strategy = EMATrendFollowingBacktestStrategy({"trend_filter_enabled": True, "adx_filter_enabled": True, "adx_threshold": 20.0})

    signal = _evaluate_signal(
        strategy,
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 100.0, "EMA50": 99.8, "EMA200": 95.0, "ADX14": 23.0},
            {"Close": 101.0, "High": 102.0, "Low": 100.0, "EMA20": 100.1, "EMA50": 99.9, "EMA200": 95.2, "ADX14": 21.0},
            {"Close": 101.5, "High": 102.5, "Low": 100.5, "EMA20": 100.2, "EMA50": 100.0, "EMA200": 95.5, "ADX14": 18.0},
            {"Close": 101.8, "High": 102.8, "Low": 100.8, "EMA20": 100.3, "EMA50": 100.1, "EMA200": 95.7, "ADX14": 19.0},
            {"Close": 102.0, "High": 103.0, "Low": 101.0, "EMA20": 100.4, "EMA50": 100.2, "EMA200": 96.0, "ADX14": 19.5},
        ],
    )

    assert signal.signal == "HOLD"
    assert 25 <= signal.confidence <= 70
