from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.risk import RiskDashboardPage, RiskDataProvider, RiskDashboardService


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


def test_risk_dashboard_page_renders_workspace_sections():
    container = StubContainer()
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())
    container.register_singleton(RiskDashboardService, RiskDashboardService())

    provider = RiskDataProvider(container=container)
    page = RiskDashboardPage(data_provider=provider)
    rendered = page.render()

    assert "RISK DASHBOARD" in rendered
    assert "Portfolio Risk Score" in rendered
    assert "Total Exposure" in rendered
    assert "Portfolio Exposure" in rendered
    assert "Risk Rules" in rendered
    assert "Risk Timeline" in rendered


def test_risk_dashboard_page_supports_navigation_and_shell():
    navigation = NavigationService()
    page = RiskDashboardPage(data_provider=RiskDataProvider())
    navigation.register("risk", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("risk")
    rendered = shell.render()

    assert "RISK DASHBOARD" in rendered
    assert "Dashboard / Risk" in rendered
    assert "Status Bar" in rendered


def test_risk_dashboard_service_refreshes_and_subscribes():
    service = RiskDashboardService()
    service.refresh()
    assert service.refresh_count() == 1
