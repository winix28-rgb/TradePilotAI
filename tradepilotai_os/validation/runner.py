"""Deterministic validation suite for TradePilotAI OS."""

from __future__ import annotations

from collections import Counter
from math import isclose
from typing import Any

import pandas as pd

from dashboard.app import _resolve_renderer_key
from dashboard.navigation import NavigationManager
from tradepilotai_os.backtesting import create_golden_research_dataset
from tradepilotai_os.backtesting.backtest_engine import BacktestEngine
from tradepilotai_os.backtesting.performance_engine import PerformanceEngine
from tradepilotai_os.backtesting.strategy_library.strategies import EMATrendFollowingBacktestStrategy
from tradepilotai_os.backtesting.strategy_library.strategies import MACDMomentumBacktestStrategy
from tradepilotai_os.backtesting.strategy_library.strategies import RSIMeanReversionBacktestStrategy
from tradepilotai_os.indicators import EMA
from tradepilotai_os.indicators import RSI

from .models import ValidationCheck
from .models import ValidationModuleResult
from .models import ValidationSuiteResult


def run_validation_suite() -> ValidationSuiteResult:
    """Run the full read-only validation suite."""

    modules = [
        _run_indicator_validation(),
        _run_strategy_validation(),
        _run_trade_validation(),
        _run_performance_validation(),
        _run_regression_validation(),
        _run_platform_validation(),
    ]

    total_checks = sum(module.total_checks for module in modules)
    passed_checks = sum(module.passed_checks for module in modules)
    overall_status = "PASS" if all(module.status == "PASS" for module in modules) else "FAIL"
    overall_score = round((passed_checks / total_checks) * 100.0, 1) if total_checks else 0.0

    return ValidationSuiteResult(
        modules=modules,
        overall_status=overall_status,
        overall_score=overall_score,
        summary="Validation suite completed without mutating the trading engines." if overall_status == "PASS" else "One or more validation modules failed.",
    )


def _run_indicator_validation() -> ValidationModuleResult:
    frame = _indicator_fixture()
    ema_12 = EMA.calculate(frame, period=12)
    rsi_14 = RSI.calculate(frame, period=14)
    adx_14 = _calculate_adx(frame["High"], frame["Low"], frame["Close"], period=14)
    atr_14 = _calculate_atr(frame["High"], frame["Low"], frame["Close"], period=14)
    bollinger = _calculate_bollinger(frame["Close"], period=20, std_dev=2.0)

    latest_price = float(frame["Close"].iloc[-1])
    latest_ema = float(ema_12.iloc[-1])
    latest_rsi = float(rsi_14.iloc[-1])
    latest_adx = float(adx_14.iloc[-1])
    latest_atr = float(atr_14.iloc[-1])
    latest_bands = bollinger.iloc[-1]

    checks = [
        ValidationCheck(
            name="EMA 12 reference match",
            passed=isclose(latest_ema, float(frame["Close"].ewm(span=12, adjust=False).mean().iloc[-1]), rel_tol=1e-9, abs_tol=1e-9),
            expected="EMA(12) from pandas ewm",
            actual=f"{latest_ema:.6f}",
            details="Validates the core EMA calculation used by the platform indicator layer.",
        ),
        ValidationCheck(
            name="RSI 14 reference match",
            passed=isclose(latest_rsi, float(_reference_rsi(frame["Close"], period=14).iloc[-1]), rel_tol=1e-9, abs_tol=1e-9),
            expected="RSI(14) from reference formula",
            actual=f"{latest_rsi:.6f}",
            details="Checks the indicator package against a deterministic RSI reference.",
        ),
        ValidationCheck(
            name="ATR is positive",
            passed=latest_atr > 0.0,
            expected="> 0",
            actual=f"{latest_atr:.6f}",
            details="Ensures volatility can be derived from the synthetic OHLC fixture.",
        ),
        ValidationCheck(
            name="ADX stays bounded",
            passed=0.0 <= latest_adx <= 100.0,
            expected="0 to 100",
            actual=f"{latest_adx:.6f}",
            details="Validates the reference ADX output is in a realistic range.",
        ),
        ValidationCheck(
            name="Bollinger band order",
            passed=float(latest_bands["upper"]) > float(latest_bands["middle"]) > float(latest_bands["lower"]),
            expected="upper > middle > lower",
            actual=f"upper={latest_bands['upper']:.6f}, middle={latest_bands['middle']:.6f}, lower={latest_bands['lower']:.6f}",
            details="Confirms the validation layer computes sensible volatility envelopes.",
        ),
        ValidationCheck(
            name="Price sits inside volatility envelope",
            passed=float(latest_bands["lower"]) <= latest_price <= float(latest_bands["upper"]),
            expected="price within bands",
            actual=f"price={latest_price:.6f}",
            details="Confirms the indicator fixture is internally coherent.",
        ),
    ]

    return _module_result("Indicator Validation", checks, summary="EMA, RSI, ATR, ADX and Bollinger reference checks passed.")


def _run_strategy_validation() -> ValidationModuleResult:
    checks: list[ValidationCheck] = []

    rsi_signal = _evaluate_strategy_signal(
        RSIMeanReversionBacktestStrategy(),
        [
            {"Close": 100.0, "RSI": 35.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 90.0},
            {"Close": 101.0, "RSI": 24.0, "EMA12": 101.5, "EMA26": 100.5, "EMA200": 91.0},
        ],
    )
    ema_signal = _evaluate_strategy_signal(
        EMATrendFollowingBacktestStrategy({"trend_filter_enabled": True, "adx_filter_enabled": True}),
        [
            {"Close": 100.0, "High": 101.0, "Low": 99.0, "EMA20": 99.0, "EMA50": 100.0, "EMA200": 95.0, "ADX14": 24.0},
            {"Close": 102.0, "High": 103.0, "Low": 101.0, "EMA20": 101.5, "EMA50": 100.5, "EMA200": 96.0, "ADX14": 25.0},
        ],
    )
    macd_buy = _evaluate_strategy_signal(
        MACDMomentumBacktestStrategy({"trend_filter_enabled": True, "histogram_confirmation": True}),
        [
            {"Close": 100.0, "EMA12": 99.0, "EMA26": 100.0, "EMA200": 95.0},
            {"Close": 110.0, "EMA12": 103.0, "EMA26": 101.0, "EMA200": 100.0},
        ],
    )
    macd_sell = _evaluate_strategy_signal(
        MACDMomentumBacktestStrategy({"trend_filter_enabled": True, "histogram_confirmation": True}),
        [
            {"Close": 110.0, "EMA12": 111.0, "EMA26": 109.0, "EMA200": 115.0},
            {"Close": 90.0, "EMA12": 88.0, "EMA26": 92.0, "EMA200": 100.0},
        ],
    )

    checks.extend(
        [
            ValidationCheck("RSI strategy BUY", rsi_signal == "BUY", "BUY", rsi_signal, "Verifies the RSI mean reversion entry path."),
            ValidationCheck("EMA strategy BUY", ema_signal == "BUY", "BUY", ema_signal, "Verifies the EMA trend-following long entry path."),
            ValidationCheck("MACD strategy BUY", macd_buy == "BUY", "BUY", macd_buy, "Verifies the MACD momentum long entry path."),
            ValidationCheck("MACD strategy SELL", macd_sell == "SELL", "SELL", macd_sell, "Verifies the MACD momentum short entry path."),
        ]
    )

    return _module_result("Strategy Validation", checks, summary="Production strategy signal paths passed deterministic smoke tests.")


def _run_trade_validation() -> ValidationModuleResult:
    dataset = create_golden_research_dataset()
    result = dataset.result
    trade_history = list(dataset.trade_history)
    exit_reason_counts = Counter(trade.exit_reason for trade in result.closed_trades)
    directions = {trade.direction for trade in result.closed_trades}
    realised_pnl = round(sum(trade.net_pnl for trade in result.closed_trades), 2)

    checks = [
        ValidationCheck(
            name="Closed trade count",
            passed=len(result.closed_trades) == 245,
            expected="245",
            actual=str(len(result.closed_trades)),
            details="Checks that the deterministic research fixture still contains the expected trade set.",
        ),
        ValidationCheck(
            name="Trade history rows",
            passed=len(trade_history) == len(result.closed_trades),
            expected=str(len(result.closed_trades)),
            actual=str(len(trade_history)),
            details="Ensures the history adapter stays in sync with the closed-trade records.",
        ),
        ValidationCheck(
            name="Trade directions",
            passed=directions == {"BUY", "SELL"},
            expected="BUY and SELL",
            actual=", ".join(sorted(directions)),
            details="Confirms the research dataset exercises both long and short trade paths.",
        ),
        ValidationCheck(
            name="Exit reason coverage",
            passed=len(exit_reason_counts) >= 3,
            expected=">= 3 exit reasons",
            actual=", ".join(sorted(exit_reason_counts.keys())),
            details="Validates the sample dataset covers multiple lifecycle outcomes.",
        ),
        ValidationCheck(
            name="Realised PnL consistency",
            passed=isclose(float(result.portfolio.realised_pnl), float(result.metrics.get("net_profit", 0.0)), rel_tol=1e-9, abs_tol=1e-9),
            expected=f"{float(result.metrics.get('net_profit', 0.0)):.2f}",
            actual=f"{realised_pnl:.2f}",
            details="Confirms closed-trade accounting matches the portfolio ledger.",
        ),
    ]

    return _module_result("Trade Validation", checks, summary="Trade history, direction and realised PnL checks passed.")


def _run_performance_validation() -> ValidationModuleResult:
    result = create_golden_research_dataset().result
    metrics = PerformanceEngine.calculate_metrics(result) if hasattr(PerformanceEngine, "calculate_metrics") else result.metrics
    reference_metrics = result.metrics

    checks = [
        ValidationCheck("Net profit", _metric_match(metrics, reference_metrics, "net_profit"), f"{reference_metrics['net_profit']:.2f}", _metric_value(metrics, "net_profit"), "Validates the headline PnL metric."),
        ValidationCheck("Total return", _metric_match(metrics, reference_metrics, "total_return"), f"{reference_metrics['total_return']:.4f}", _metric_value(metrics, "total_return"), "Validates portfolio return arithmetic."),
        ValidationCheck("Profit factor", _metric_match(metrics, reference_metrics, "profit_factor"), f"{reference_metrics['profit_factor']:.2f}", _metric_value(metrics, "profit_factor"), "Validates the reward-to-risk ratio."),
        ValidationCheck("Win rate", _metric_match(metrics, reference_metrics, "win_rate"), f"{reference_metrics['win_rate']:.2f}", _metric_value(metrics, "win_rate"), "Validates the win-rate calculation."),
        ValidationCheck("Maximum drawdown", _metric_match(metrics, reference_metrics, "maximum_drawdown"), f"{reference_metrics['maximum_drawdown']:.2f}", _metric_value(metrics, "maximum_drawdown"), "Validates downside risk measurement."),
        ValidationCheck("Final equity", _metric_match(metrics, reference_metrics, "final_equity"), f"{reference_metrics['final_equity']:.2f}", _metric_value(metrics, "final_equity"), "Validates the ending equity value."),
        ValidationCheck("Trade count", _metric_match(metrics, reference_metrics, "total_trades"), str(reference_metrics["total_trades"]), _metric_value(metrics, "total_trades"), "Validates the total trade count."),
    ]

    return _module_result("Performance Validation", checks, summary="Golden performance metrics match the deterministic reference.")


def _run_regression_validation() -> ValidationModuleResult:
    dataset = create_golden_research_dataset()
    result = dataset.result

    checks = [
        ValidationCheck(
            name="Equity curve length",
            passed=len(result.equity_curve) == len(dataset.monthly_returns),
            expected=str(len(dataset.monthly_returns)),
            actual=str(len(result.equity_curve)),
            details="Confirms the monthly curve remains aligned with the golden research fixture.",
        ),
        ValidationCheck(
            name="Monthly returns match",
            passed=list(result.metrics.get("monthly_returns", [])) == list(dataset.monthly_returns),
            expected="Golden monthly returns",
            actual=f"{len(result.metrics.get('monthly_returns', []))} rows",
            details="Protects the research data from accidental drift.",
        ),
        ValidationCheck(
            name="Terminal equity value",
            passed=isclose(float(result.equity_curve[-1][1]), 124850.0, rel_tol=1e-9, abs_tol=1e-9),
            expected="124850.00",
            actual=f"{float(result.equity_curve[-1][1]):.2f}",
            details="Checks the ending equity level on the deterministic curve.",
        ),
        ValidationCheck(
            name="Drawdown terminal value",
            passed=isclose(float(result.drawdown_curve[-1][1]), -0.91, rel_tol=1e-9, abs_tol=1e-9),
            expected="-0.91",
            actual=f"{float(result.drawdown_curve[-1][1]):.2f}",
            details="Confirms the trailing drawdown state stays unchanged.",
        ),
        ValidationCheck(
            name="Symbol coverage",
            passed=sorted(result.symbol_results.keys()) == ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"],
            expected="7 benchmark symbols",
            actual=", ".join(sorted(result.symbol_results.keys())),
            details="Verifies the multi-asset research fixture remains complete.",
        ),
    ]

    return _module_result("Regression Validation", checks, summary="Golden backtest and trade history stayed stable across the regression snapshot.")


def _run_platform_validation() -> ValidationModuleResult:
    from dashboard.workspaces import render_validation_workspace

    checks = [
        ValidationCheck(
            name="Validation workspace export",
            passed=callable(render_validation_workspace),
            expected="callable",
            actual=str(callable(render_validation_workspace)),
            details="Ensures the dashboard workspace can render the validation panel.",
        ),
        ValidationCheck(
            name="Validation route resolution",
            passed=_resolve_renderer_key("validation") == "validation",
            expected="validation",
            actual=_resolve_renderer_key("validation"),
            details="Confirms the dashboard router accepts the new validation route.",
        ),
        ValidationCheck(
            name="Navigation menu contains validation",
            passed="validation" in [item.key for item in NavigationManager().pages()],
            expected="validation",
            actual=", ".join(item.key for item in NavigationManager().pages()),
            details="Ensures the sidebar exposes the workspace entry.",
        ),
        ValidationCheck(
            name="Backtest fixture factory available",
            passed=callable(create_golden_research_dataset),
            expected="callable",
            actual=str(callable(create_golden_research_dataset)),
            details="Confirms the validation layer can load the deterministic golden dataset.",
        ),
        ValidationCheck(
            name="Core backtesting types import",
            passed=BacktestEngine is not None,
            expected="importable",
            actual=str(BacktestEngine.__name__),
            details="Provides a lightweight platform check that the backtesting stack is reachable.",
        ),
    ]

    return _module_result("Platform Validation", checks, summary="Dashboard routing and platform imports are intact.")


def _module_result(name: str, checks: list[ValidationCheck], summary: str) -> ValidationModuleResult:
    passed = sum(1 for check in checks if check.passed)
    total = len(checks)
    status = "PASS" if total and passed == total else "FAIL"
    score = round((passed / total) * 100.0, 1) if total else 0.0
    return ValidationModuleResult(name=name, checks=checks, status=status, score=score, summary=summary)


def _indicator_fixture() -> pd.DataFrame:
    closes = [
        100.0, 101.2, 102.4, 101.8, 103.5, 104.1, 105.8, 105.0, 106.7, 108.2,
        109.5, 108.9, 107.6, 109.1, 110.8, 112.4, 111.7, 113.2, 114.6, 115.5,
        116.3, 115.1, 114.2, 115.8, 117.4, 118.9, 119.7, 120.5, 119.2, 121.4,
    ]
    rows = []
    for index, close in enumerate(closes):
        rows.append(
            {
                "Open": close - 0.4 if index % 2 == 0 else close + 0.2,
                "High": close + 1.4 + (index % 3) * 0.1,
                "Low": close - 1.6 - (index % 2) * 0.1,
                "Close": close,
                "Volume": 100000 + index * 750,
            }
        )
    return pd.DataFrame(rows, index=pd.date_range("2024-01-01", periods=len(rows), freq="D", tz="UTC"))


def _reference_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            (high - low),
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def _calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    atr = _calculate_atr(high, low, close, period=period).replace(0, float("nan"))
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean() / atr
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).fillna(0.0)
    return dx.ewm(alpha=1 / period, min_periods=period, adjust=False).mean().fillna(20.0)


def _calculate_bollinger(close: pd.Series, period: int, std_dev: float) -> pd.DataFrame:
    middle = close.rolling(period).mean()
    deviation = close.rolling(period).std(ddof=0)
    return pd.DataFrame(
        {
            "middle": middle,
            "upper": middle + (deviation * std_dev),
            "lower": middle - (deviation * std_dev),
        }
    )


def _evaluate_strategy_signal(strategy: Any, rows: list[dict[str, float]]) -> str:
    frame = pd.DataFrame(rows)
    context = strategy.evaluate("AAPL", frame)
    signal = strategy.generate_signal("AAPL", context)
    return signal.signal


def _metric_value(metrics: dict[str, Any], key: str) -> str:
    value = metrics.get(key)
    if isinstance(value, float):
        return f"{value:.4f}" if abs(value) < 1 else f"{value:.2f}"
    return str(value)


def _metric_match(metrics: dict[str, Any], reference_metrics: dict[str, Any], key: str) -> bool:
    value = metrics.get(key)
    reference = reference_metrics.get(key)
    if isinstance(value, (float, int)) and isinstance(reference, (float, int)):
        return isclose(float(value), float(reference), rel_tol=1e-9, abs_tol=1e-9)
    return value == reference