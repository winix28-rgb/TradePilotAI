from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.broker.paper_broker import PaperBroker
from tradepilotai_os.models.position import Position as PortfolioPosition
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.portfolio.portfolio_manager import PortfolioManager
from tradepilotai_os.risk import RiskDashboardPage, RiskDataProvider, RiskDashboardService
from tradepilotai_os.risk.risk_engine import RiskEngine


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


def test_risk_dashboard_service_uses_live_portfolio_and_risk_engine():
    portfolio_manager = PortfolioManager(initial_cash=100000.0)
    portfolio_manager.state.cash = 50000.0
    portfolio_manager.state.exposure = 10000.0
    portfolio_manager.state.unrealised_pnl = 500.0
    portfolio_manager.state.realised_pnl = 250.0
    portfolio_manager.state.positions["AAPL"] = PortfolioPosition(
        symbol="AAPL",
        quantity=10,
        average_price=100.0,
        market_price=105.0,
        exposure=1050.0,
    )

    broker = PaperBroker(initial_cash=100000.0)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)

    service = RiskDashboardService(portfolio_manager=portfolio_manager, broker=broker, risk_engine=risk_engine)
    snapshot = service.get_snapshot()

    assert snapshot.assessment.open_positions == 1
    assert snapshot.assessment.total_exposure == 10000.0
    assert snapshot.assessment.available_cash == 50000.0
    assert snapshot.positions[0].symbol == "AAPL"
    assert snapshot.positions[0].risk_percent > 0
