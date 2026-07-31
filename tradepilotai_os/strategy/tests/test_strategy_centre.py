from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.strategy import StrategyDataProvider, StrategyPage, StrategyService


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
        self.count = 3


def test_strategy_page_renders_library_and_metrics():
    service = StrategyService()
    provider = StrategyDataProvider(service=service)
    page = StrategyPage(data_provider=provider)
    rendered = page.render()

    assert "STRATEGY CENTRE" in rendered
    assert "Strategy Library" in rendered
    assert "Strategy Configuration" in rendered
    assert "Performance Summary" in rendered
    assert "Version History" in rendered
    assert "Deployment" in rendered


def test_strategy_service_versioning_and_deployment():
    service = StrategyService()
    strategy = service.list_strategies()[0]
    version = strategy.versions[0]
    updated = service.create_version(strategy, version)
    deployment = service.deploy(updated, "Paper Broker")

    assert updated.version == version.version
    assert deployment.target == "Paper Broker"
    assert deployment.status in {"Deployed", "Failed"}


def test_strategy_navigation_and_shell_render():
    navigation = NavigationService()
    page = StrategyPage(data_provider=StrategyDataProvider())
    navigation.register("strategy", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("strategy")
    rendered = shell.render()

    assert "STRATEGY CENTRE" in rendered
    assert "Header" in rendered
    assert "Status Bar" in rendered
