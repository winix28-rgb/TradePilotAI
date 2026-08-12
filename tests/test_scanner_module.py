from datetime import datetime

import pandas as pd

from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.scanner import ScannerDataProvider, ScannerPage, ScannerService


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


class StubSignal:
    def __init__(self) -> None:
        self.signal = "BUY"
        self.confidence = 80
        self.reasons = ["stub"]
        self.price = 100.0
        self.rsi = 25.0
        self.ema12 = 101.0
        self.ema26 = 100.0


class StubIndicatorEngine:
    def add_indicators(self, data):
        return data


class StubStrategyEngine:
    def __init__(self) -> None:
        self.strategy = type("StrategyMetadata", (), {"primary_timeframe": "1h"})()

    def evaluate(self, symbol, data):
        return StubSignal()


class StubMarketDataProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def history(self, symbol: str, period: str = "6mo", interval: str | None = None):
        self.calls.append({"symbol": symbol, "period": period, "interval": interval or ""})
        return pd.DataFrame(
            {
                "Close": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0, 126.0, 127.0, 128.0, 129.0],
                "RSI": [25.0] * 30,
                "EMA12": [101.0] * 30,
                "EMA26": [100.0] * 30,
            }
        )


def test_scanner_page_renders_workspace_sections():
    container = StubContainer()
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())

    provider = ScannerDataProvider(container=container, scanner_service=ScannerService())
    page = ScannerPage(data_provider=provider)
    rendered = page.render()

    assert "SCANNER WORKSPACE" in rendered
    assert "Top Summary" in rendered
    assert "Pipeline Status" in rendered
    assert "Buy Candidates" in rendered
    assert "Sell Candidates" in rendered
    assert "Signal Detail" in rendered
    assert "AAPL" in rendered


def test_scanner_page_supports_navigation_and_shell():
    navigation = NavigationService()
    page = ScannerPage(data_provider=ScannerDataProvider())
    navigation.register("scanner", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("scanner")
    rendered = shell.render()

    assert "SCANNER WORKSPACE" in rendered
    assert "Dashboard / Scanner" in rendered
    assert "Status Bar" in rendered


def test_scanner_service_volatility_handles_multiindex_close_column():
    service = ScannerService()
    data = pd.DataFrame(
        [[100.0, 99.0], [101.0, 100.0], [102.0, 101.0]],
        columns=pd.MultiIndex.from_tuples([("Close", "RR"), ("Open", "RR")]),
    )

    volatility = service._volatility(data)

    assert volatility >= 0.0


def test_scanner_service_uses_strategy_primary_timeframe():
    data_provider = StubMarketDataProvider()
    service = ScannerService(
        data_provider=data_provider,
        strategy_engine=StubStrategyEngine(),
        indicator_engine=StubIndicatorEngine(),
    )

    service.scan(watchlist=["AAPL"])

    assert data_provider.calls[0]["interval"] == "1h"


def test_scanner_service_stores_utc_scan_timestamp():
    service = ScannerService(
        data_provider=StubMarketDataProvider(),
        strategy_engine=StubStrategyEngine(),
        indicator_engine=StubIndicatorEngine(),
    )

    service.scan(watchlist=["AAPL"])

    parsed = datetime.fromisoformat(service.last_scan_time)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0
