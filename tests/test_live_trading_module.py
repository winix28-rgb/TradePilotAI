from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.live_trading import LiveTradingDataProvider, LiveTradingPage, LiveTradingService


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


def test_live_trading_page_renders_workspace_sections():
    container = StubContainer()
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())
    container.register_singleton(LiveTradingService, LiveTradingService())

    provider = LiveTradingDataProvider(container=container)
    page = LiveTradingPage(data_provider=provider)
    rendered = page.render()

    assert "LIVE TRADING WORKSPACE" in rendered
    assert "Account Value" in rendered
    assert "Order Ticket" in rendered
    assert "Pre-Trade Validation" in rendered
    assert "Order Timeline" in rendered


def test_live_trading_page_supports_navigation_and_shell():
    navigation = NavigationService()
    page = LiveTradingPage(data_provider=LiveTradingDataProvider())
    navigation.register("live_trading", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("live_trading")
    rendered = shell.render()

    assert "LIVE TRADING WORKSPACE" in rendered
    assert "Dashboard / Live Trading" in rendered
    assert "Status Bar" in rendered


def test_live_trading_service_submits_and_refreshes():
    service = LiveTradingService()
    service.refresh()
    assert service.refresh_count() == 1
