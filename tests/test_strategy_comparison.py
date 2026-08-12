from __future__ import annotations

from tradepilotai_os.backtesting import BacktestingDataProvider
from tradepilotai_os.backtesting.comparison import StrategyComparisonEngine
from tradepilotai_os.backtesting.comparison import StrategyComparisonResult
from tradepilotai_os.backtesting.comparison import StrategyComparisonRun
from tradepilotai_os.backtesting.result import BacktestResult
from tradepilotai_os.backtesting.strategy_library import StrategyRegistry
import pandas as pd


class FakeStrategy:
    def __init__(self, strategy_name: str) -> None:
        self.name = strategy_name


class FakeDataEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def download_data(self, ticker: str, interval: str, period: str):
        self.calls.append((ticker, interval, period))
        return pd.DataFrame(
            {
                "Close": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0, 126.0, 127.0, 128.0, 129.0],
                "High": [100.5] * 30,
                "Low": [99.5] * 30,
            }
        )


class FakeBacktestEngine:
    def __init__(self, strategy_name: str) -> None:
        self.strategy_name = strategy_name

    def run_backtest(self, symbols, market_data, interval, period, progress_callback=None):
        result = BacktestResult(initial_cash=100000.0)
        result.requested_symbols = list(symbols)
        result.loaded_symbols = list(symbols)
        result.failed_symbols = {}
        result.completion_status = "success"
        result.equity_curve = [
            ("2024-01-01", 100000.0),
            ("2024-02-01", 100000.0 + len(self.strategy_name) * 100.0),
        ]
        result.drawdown_curve = [
            ("2024-01-01", 0.0),
            ("2024-02-01", -1.0),
        ]
        result.metrics = {
            "net_profit": float(len(self.strategy_name) * 100),
            "total_return": float(len(self.strategy_name)) / 10.0,
            "win_rate": 100.0,
            "profit_factor": 1.8,
            "maximum_drawdown": -1.0,
            "expectancy": 25.0,
            "total_trades": 1,
            "winning_trades": 1,
            "losing_trades": 0,
        }
        return result


def _engine_factory(strategy, initial_cash, commission_rate, spread, slippage, data_engine, scanner, risk_engine):
    return FakeBacktestEngine(strategy.name)


class StubComparisonService:
    def __init__(self, result: StrategyComparisonResult) -> None:
        self.result = result
        self.calls = []

    def run_strategy_comparison(self, configuration, progress_callback=None):
        self.calls.append(configuration)
        return self.result


def test_strategy_comparison_engine_runs_each_selected_strategy() -> None:
    base_engine = type("BaseEngine", (), {"data_engine": FakeDataEngine(), "scanner": None, "risk_engine": None})()
    engine = StrategyComparisonEngine(strategy_registry=StrategyRegistry(), base_engine=base_engine, engine_factory=_engine_factory)

    result = engine.compare(
        strategy_ids=["rsi_mean_reversion", "ema_trend_following"],
        market_data={"AAPL": object()},
        symbols=["AAPL"],
        initial_cash=100000.0,
        commission_rate=0.0005,
        spread=0.02,
        slippage=0.01,
    )

    assert result.completion_status == "success"
    assert [run.strategy_id for run in result.comparison_runs] == ["rsi_mean_reversion", "ema_trend_following"]
    assert result.comparison_runs[0].total_trades == 1
    assert result.comparison_runs[0].primary_timeframe == "1h"
    assert result.comparison_runs[1].primary_timeframe == "4h"
    assert result.to_dict()["configuration"]["timeframe_warning"] is True
    assert result.to_dict()["table"][0]["strategy_name"] == "TradePilotAI RSI Mean Reversion"
    assert result.to_dict()["charts"]["equity_curve"]
    assert base_engine.data_engine.calls[0][1] == "1h"
    assert base_engine.data_engine.calls[1][1] == "4h"


def test_backtesting_data_provider_returns_comparison_payload() -> None:
    comparison_result = StrategyComparisonResult(
        initial_cash=100000.0,
        requested_symbols=["AAPL"],
        loaded_symbols=["AAPL"],
        completion_status="success",
        comparison_runs=[
            StrategyComparisonRun(
                strategy_id="ema_trend_following",
                strategy_name="EMA Trend Following",
                metrics={
                    "net_profit": 1250.0,
                    "total_return": 1.25,
                    "win_rate": 66.67,
                    "profit_factor": 1.9,
                    "maximum_drawdown": -3.2,
                    "expectancy": 42.0,
                    "total_trades": 3,
                    "winning_trades": 2,
                    "losing_trades": 1,
                },
                equity_curve=[("2024-01-01", 100000.0), ("2024-02-01", 101250.0)],
                drawdown_curve=[("2024-01-01", 0.0), ("2024-02-01", -3.2)],
                monthly_returns=[("2024-01", 1.25)],
                requested_symbols=["AAPL"],
                loaded_symbols=["AAPL"],
                completion_status="success",
            )
        ],
    )
    provider = BacktestingDataProvider(state={}, service=StubComparisonService(comparison_result))

    provider.run_strategy_comparison(
        {
            "symbols": "AAPL",
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
            "strategy_ids": ["ema_trend_following"],
        }
    )
    payload = provider.get_backtest_data()

    assert payload["comparison"]["summary"]["strategy_count"] == 1
    assert payload["comparison"]["table"][0]["strategy_name"] == "EMA Trend Following"
    assert payload["comparison"]["charts"]["trade_counts"][0]["total_trades"] == 3
