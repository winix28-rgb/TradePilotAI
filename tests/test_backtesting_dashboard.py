from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.backtesting import BacktestingPage, BacktestingDataProvider, BacktestingService
from tradepilotai_os.backtesting.result import BacktestResult, BacktestTradeRecord
from tradepilotai_os.backtesting.strategy_library import StrategyLibraryEngine
from tradepilotai_os.backtesting.strategy_library import StrategyRegistry
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.backtesting.portfolio_simulator import PortfolioSimulator
from tradepilotai_os.backtesting.performance_engine import PerformanceEngine
import pandas as pd


class StubContainer:
    def __init__(self) -> None:
        self._services = {}

    def register_singleton(self, name: str, instance: object) -> None:
        self._services[name] = instance

    def resolve(self, name: str) -> object:
        return self._services[name]

    def contains(self, name: str) -> bool:
        return name in self._services


class StubRefreshManager:
    def __init__(self) -> None:
        self.current_mode = "30s"
        self.interval_seconds = 30
        self.refresh_calls = 0

    def refresh(self) -> None:
        self.refresh_calls += 1


class StubNotifications:
    def __init__(self) -> None:
        self.count = 2


class StubBacktestingService:
    def run_backtest(self, configuration, progress_callback=None):
        stages = [
            "Loading historical data...",
            "Generating signals...",
            "Executing trades...",
            "Calculating performance...",
            "Building report...",
        ]
        for stage in stages:
            if progress_callback is not None:
                progress_callback(stage)

        result = BacktestResult(initial_cash=100000.0)
        result.equity_curve = [
            ("2024-01-02", 100000.0),
            ("2024-01-31", 101500.0),
            ("2024-02-28", 102250.0),
        ]
        result.drawdown_series = [
            ("2024-01-02", 0.0),
            ("2024-01-31", -0.25),
            ("2024-02-28", -0.1),
        ]
        result.closed_trades = [
            BacktestTradeRecord(
                symbol="AAPL",
                direction="Long",
                entry_date="2024-01-10",
                entry_price=190.0,
                exit_date="2024-01-25",
                exit_price=195.0,
                quantity=10,
                gross_pnl=50.0,
                costs=3.0,
                net_pnl=47.0,
                exit_reason="Take Profit",
            )
        ]
        result.trades = list(result.closed_trades)
        result.symbol_results = {"AAPL": {"status": "completed", "signals": 35, "closed_trades": 1}}
        result.requested_symbols = ["AAPL"]
        result.loaded_symbols = ["AAPL"]
        result.failed_symbols = {}
        result.completion_status = "success"
        result.metrics = {
            "net_profit": 47.0,
            "total_return": 0.05,
            "profit_factor": 1.6,
            "win_rate": 100.0,
            "maximum_drawdown": -0.25,
            "expectancy": 47.0,
            "long_trades": 1,
            "short_trades": 0,
            "long_win_rate": 100.0,
            "short_win_rate": 0.0,
            "exit_reason_breakdown": {
                "Stop Loss": 0,
                "Take Profit": 1,
                "Strategy Exit": 0,
                "End of Test": 0,
            },
        }
        result.portfolio.metadata.update(
            {
                "commission_rate": 0.0005,
                "bid_ask_spread": 0.02,
                "slippage": 0.01,
            }
        )
        return result


class FakeMarketData:
    def __init__(self, empty: bool = False) -> None:
        self.empty = empty


class FakeDataEngine:
    def __init__(self, available: dict[str, bool]) -> None:
        self.available = available
        self.calls: list[dict[str, str]] = []

    def download_data(self, ticker: str, interval: str, period: str):
        self.calls.append({"ticker": ticker, "interval": interval, "period": period})
        if not self.available.get(ticker, False):
            return None
        return FakeMarketData(empty=False)


class FakeBacktestEngine:
    def __init__(self, data_engine: FakeDataEngine) -> None:
        self.trade_simulator = type("TradeSimulatorState", (), {"commission_rate": 0.0, "bid_ask_spread": 0.0, "slippage": 0.0})()
        self.portfolio_simulator = PortfolioSimulator(initial_cash=100000.0)
        self.performance_engine = PerformanceEngine()
        self.data_engine = data_engine
        self.calls = []

    def run_backtest(self, symbols, market_data, interval, period, progress_callback=None):
        self.calls.append({"symbols": symbols, "market_data": market_data, "interval": interval, "period": period})
        result = BacktestResult(initial_cash=self.portfolio_simulator.initial_cash)
        result.requested_symbols = list(symbols)
        result.loaded_symbols = list(symbols)
        result.failed_symbols = {}
        result.completion_status = "success"
        result.symbol_results = {symbol: {"status": "completed"} for symbol in symbols}
        result.equity_curve = [("2024-01-01", 100000.0)]
        result.drawdown_series = [("2024-01-01", 0.0)]
        result.portfolio.metadata.update({"commission_rate": 0.0005, "bid_ask_spread": 0.02, "slippage": 0.01})
        return result


def test_backtesting_page_renders_kpis_and_charts():
    container = StubContainer()
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())

    provider = BacktestingDataProvider(container=container)
    page = BacktestingPage(data_provider=provider)
    rendered = page.render()

    assert rendered == "backtesting"


def test_backtesting_page_supports_navigation_and_shell():
    navigation = NavigationService()
    page = BacktestingPage(data_provider=BacktestingDataProvider())
    navigation.register("backtesting", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("backtesting")
    rendered = shell.render()

    assert "Main Content" in rendered
    assert "backtesting" in rendered
    assert "Status Bar" in rendered


def test_backtesting_provider_runs_backtest_and_populates_workspace():
    state = {}
    provider = BacktestingDataProvider(state=state, service=StubBacktestingService())

    provider.run_backtest(
        {
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
        }
    )
    payload = provider.get_backtest_data()

    assert payload["summary"]["status"] == "completed"
    assert payload["metrics"]["net_profit"] == 47.0
    assert payload["charts"]["equity_curve"]
    assert payload["charts"]["drawdown_curve"]
    assert payload["performance_breakdown"]["monthly_returns"]
    assert payload["performance_breakdown"]["exit_reasons"]["Take Profit"] == 1
    assert payload["trade_history"]
    assert payload["progress"]["current_stage"] == "Completed"
    assert payload["progress"]["stages"][-1]["status"] == "Completed"
    assert payload["backtest_status"]["requested_symbols"] == ["AAPL"]
    assert payload["backtest_status"]["loaded_symbols"] == ["AAPL"]
    assert payload["backtest_status"]["failed_symbols"] == {}
    assert payload["backtest_status"]["completion_status"] == "success"


def test_backtesting_service_records_partial_success_when_some_symbols_fail():
    engine = FakeBacktestEngine(FakeDataEngine({"AAPL": True, "ZZZZ": False}))
    service = BacktestingService(engine=engine)

    result = service.run_backtest(
        {
            "symbols": "AAPL,ZZZZ",
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
        }
    )

    assert result.requested_symbols == ["AAPL", "ZZZZ"]
    assert result.loaded_symbols == ["AAPL"]
    assert result.failed_symbols == {"ZZZZ": "No historical data returned"}
    assert result.completion_status == "partial_success"
    assert engine.calls[0]["symbols"] == ["AAPL"]


def test_backtesting_service_records_failure_when_no_symbols_load():
    engine = FakeBacktestEngine(FakeDataEngine({"ZZZZ": False}))
    service = BacktestingService(engine=engine)

    result = service.run_backtest(
        {
            "symbols": "ZZZZ",
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
        }
    )

    assert result.requested_symbols == ["ZZZZ"]
    assert result.loaded_symbols == []
    assert result.failed_symbols == {"ZZZZ": "No historical data returned"}
    assert result.completion_status == "failed"
    assert engine.calls == []


def test_backtesting_service_uses_strategy_timeframe_and_override():
    data_engine = FakeDataEngine({"AAPL": True})
    engine = FakeBacktestEngine(data_engine)
    service = BacktestingService(engine=engine)

    service.run_backtest(
        {
            "symbols": "AAPL",
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
            "strategy_id": "rsi_mean_reversion",
        }
    )

    assert data_engine.calls[0]["interval"] == "1h"
    assert engine.calls[0]["interval"] == "1h"

    engine.calls.clear()
    data_engine.calls.clear()

    service.run_backtest(
        {
            "symbols": "AAPL",
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
            "strategy_id": "rsi_mean_reversion",
            "timeframe": "2h",
        }
    )

    assert data_engine.calls[0]["interval"] == "2h"
    assert engine.calls[0]["interval"] == "2h"


def test_strategy_registry_exposes_required_default_library_entries():
    registry = StrategyRegistry()

    definitions = registry.list_definitions()
    strategy_ids = {item.strategy_id for item in definitions}

    assert "rsi_mean_reversion" in strategy_ids
    assert "ema_trend_following" in strategy_ids
    assert "macd_momentum" in strategy_ids


def test_backtesting_service_applies_selected_strategy_to_engine():
    engine = FakeBacktestEngine(FakeDataEngine({"AAPL": True}))
    service = BacktestingService(engine=engine)

    result = service.run_backtest(
        {
            "symbols": "AAPL",
            "date_range": "2024-01-01 to 2024-12-31",
            "capital": "$100,000",
            "commission": "0.05%",
            "spread": "0.02",
            "slippage": "0.01",
            "strategy_id": "ema_trend_following",
            "strategy_parameters": {
                "fast_ema": 20,
                "slow_ema": 50,
                "trend_ema": 200,
                "adx_threshold": 20,
                "trend_filter_enabled": True,
                "adx_filter_enabled": True,
            },
        }
    )

    assert isinstance(engine.strategy_engine, StrategyLibraryEngine)
    assert result.portfolio.metadata["strategy_id"] == "ema_trend_following"
    assert result.portfolio.metadata["strategy_parameters"]["fast_ema"] == 20


def test_backtesting_chart_timestamp_normalization_handles_mixed_inputs():
    page = BacktestingPage()

    frame = page._points_to_dataframe(
        [
            ("2024-01-01T00:00:00", 100.0),
            (pd.Timestamp("2024-01-01 01:00:00", tz="UTC"), 101.0),
            ("2024-01-01T02:00:00+01:00", 102.0),
        ]
    )

    assert not frame.empty
    assert str(frame["Date"].dt.tz) == "UTC"
    assert len(frame) == 3


def test_backtesting_comparison_timestamp_normalization_handles_mixed_inputs():
    page = BacktestingPage()

    frame = page._comparison_points_to_dataframe(
        [
            {"strategy_id": "rsi_mean_reversion", "timestamp": "2024-01-01T00:00:00", "value": 100.0},
            {"strategy_id": "ema_trend_following", "timestamp": pd.Timestamp("2024-01-01 01:00:00", tz="UTC"), "value": 101.0},
            ("macd_momentum", "2024-01-01T02:00:00+01:00", 102.0),
        ]
    )

    assert not frame.empty
    assert str(frame["Date"].dt.tz) == "UTC"
    assert set(frame["Strategy"]) == {"rsi_mean_reversion", "ema_trend_following", "macd_momentum"}
