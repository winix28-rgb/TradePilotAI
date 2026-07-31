from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.trade_history import TradeHistoryDataProvider, TradeHistoryPage, TradeHistoryService


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


def test_trade_history_page_renders_workspace_sections():
    container = StubContainer()
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())
    container.register_singleton(TradeHistoryService, TradeHistoryService())

    provider = TradeHistoryDataProvider(container=container)
    page = TradeHistoryPage(data_provider=provider)
    rendered = page.render()

    assert "TRADE HISTORY WORKSPACE" in rendered
    assert "Total Trades" in rendered
    assert "Open Trades" in rendered
    assert "Closed Trades" in rendered
    assert "Filters" in rendered
    assert "TH-1001" in rendered
    assert "Trade Detail" in rendered


def test_trade_history_page_supports_navigation_and_shell():
    navigation = NavigationService()
    page = TradeHistoryPage(data_provider=TradeHistoryDataProvider())
    navigation.register("trade_history", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("trade_history")
    rendered = shell.render()

    assert "TRADE HISTORY WORKSPACE" in rendered
    assert "Dashboard / Trade History" in rendered
    assert "Status Bar" in rendered


def test_trade_history_service_emits_event_and_refreshes():
    service = TradeHistoryService()
    service.subscribe(type("Event", (), {"name": "TradeOpened", "trade_id": "TH-1001"})())
    service.refresh()

    assert service.refresh_count() == 1
