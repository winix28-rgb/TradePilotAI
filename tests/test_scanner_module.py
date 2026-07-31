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
