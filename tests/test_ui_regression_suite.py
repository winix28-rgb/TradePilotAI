from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.core.container import Container
from tradepilotai_os.dashboard.data_provider import DashboardDataProvider
from tradepilotai_os.dashboard.page import DashboardPage
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.portfolio.page import PortfolioPage
from tradepilotai_os.portfolio.position_detail import PositionDetailPage
from tradepilotai_os.sidebar.component import Sidebar
from tradepilotai_os.ui_library import (
    Breadcrumb,
    Card,
    DataTable,
    KPIChartCard,
    StatusBadge,
)


class StubConfig:
    def __init__(self) -> None:
        self._data = {"strategy": {"timeframe": "1h"}}

    def get(self, key: str, default=None):
        return self._data.get(key, default)


class StubDataEngine:
    def __init__(self) -> None:
        self._running = True
        self.last_sync = "1h"

    def is_running(self) -> bool:
        return self._running


class StubPortfolioManager:
    def __init__(self) -> None:
        self.state = type(
            "State",
            (),
            {
                "cash": 5000.0,
                "exposure": 1200.0,
                "positions": {"AAPL": object()},
                "realised_pnl": 200.0,
                "unrealised_pnl": 100.0,
            },
        )()


class StubBroker:
    def __init__(self) -> None:
        self.portfolio = type(
            "Portfolio",
            (),
            {"cash": 4500.0, "exposure": 1100.0, "positions": {"MSFT": object()}, "realised_pnl": 300.0},
        )()
        self.executed_trades = [type("Trade", (), {"ticker": "AAPL", "direction": "BUY", "entry_price": 100.0})()]
        self.connected = True


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


class StubPortfolioService:
    def __init__(self) -> None:
        self.state = type(
            "State",
            (),
            {
                "cash": 25000.0,
                "buying_power": 50000.0,
                "today_pnl": 250.0,
                "total_return": 0.08,
                "unrealised_pnl": 1250.0,
                "realised_pnl": 500.0,
                "positions": {
                    "AAPL": type(
                        "Position",
                        (),
                        {
                            "symbol": "AAPL",
                            "quantity": 10,
                            "average_price": 100.0,
                            "market_price": 110.0,
                            "metadata": {"stop_loss": 95.0, "target": 120.0, "holding_time": "3d"},
                        },
                    )()
                },
            },
        )()


class StubEventBus:
    def __init__(self) -> None:
        self.subscriptions = []

    def subscribe(self, event_name: str, handler) -> None:
        self.subscriptions.append((event_name, handler))

    def publish(self, event_name: str, payload=None) -> None:
        for _, handler in self.subscriptions:
            handler(event_name, payload)


def _build_dashboard_page() -> DashboardPage:
    container = Container()
    container.register_singleton("data_engine", StubDataEngine())
    container.register_singleton("broker", StubBroker())
    container.register_singleton("config", StubConfig())
    container.register_singleton("portfolio_manager", StubPortfolioManager())
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())
    container.register_singleton("scanner", type("Scanner", (), {"get_watchlist": lambda self: ["AAPL", "MSFT"]})())
    provider = DashboardDataProvider(container=container, app=type("App", (), {"last_run_summary": {"signals_generated": 2, "orders_executed": 1}})())
    return DashboardPage(data_provider=provider)


def test_dashboard_regression_suite():
    page = _build_dashboard_page()
    rendered = page.render()

    assert "TRADEPILOTAI OS DASHBOARD" in rendered
    assert "System Status" in rendered
    assert "Pipeline Summary" in rendered
    assert "Portfolio Snapshot" in rendered
    assert "Market Scanner Summary" in rendered
    assert "Strategy Performance" in rendered
    assert "AAPL" in rendered
    assert "Refresh Interval" in rendered
    assert "Notification Count" in rendered


def test_dashboard_live_binding_and_event_flow():
    page = _build_dashboard_page()
    rendered = page.render()

    assert "$5,300.00" in rendered or "$5,300.00" in rendered
    assert "Signals generated: 2" in rendered
    assert "Broker Status" in rendered


def test_portfolio_regression_suite():
    service = StubPortfolioService()
    page = PortfolioPage(portfolio_service=service)
    rendered = page.render()

    assert "PORTFOLIO DASHBOARD" in rendered
    assert "$26,250.00" in rendered
    assert "$25,000.00" in rendered
    assert "$50,000.00" in rendered
    assert "8.00%" in rendered
    assert "AAPL" in rendered


def test_position_detail_navigation_and_breadcrumbs():
    navigation = NavigationService()
    portfolio_page = PortfolioPage(portfolio_service=StubPortfolioService(), navigation_service=navigation)
    detail_page = PositionDetailPage(position=StubPortfolioService().state.positions["AAPL"])

    navigation.register("portfolio", portfolio_page)
    navigation.register("position_detail", detail_page)

    assert navigation.navigate("portfolio") is portfolio_page
    assert navigation.navigate("position_detail") is detail_page
    assert navigation.breadcrumbs("portfolio")[0] == "Dashboard"
    assert navigation.breadcrumbs("portfolio")[1] is portfolio_page

    rendered = detail_page.render()
    assert "Position Detail" in rendered
    assert "AAPL" in rendered
    assert "Target" in rendered


def test_navigation_resolves_routes_and_handles_invalid_paths():
    navigation = NavigationService()
    page = DashboardPage()
    navigation.register("dashboard", page)
    navigation.register("portfolio", PortfolioPage())

    assert navigation.navigate("dashboard") is page
    assert navigation.navigate("portfolio") is not None
    assert navigation.navigate("missing") is None
    assert navigation.breadcrumbs("dashboard")[0] == "Dashboard"
    assert navigation.breadcrumbs("dashboard")[1] is page


def test_application_shell_renders_core_sections():
    navigation = NavigationService()
    dashboard_page = DashboardPage()
    navigation.register("dashboard", dashboard_page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("dashboard")
    rendered = shell.render()

    assert "Header" in rendered
    assert "Sidebar" in rendered
    assert "Main Content" in rendered
    assert "Status Bar" in rendered
    assert "TRADEPILOTAI OS DASHBOARD" in rendered


def test_ui_component_library_renders_shared_components():
    assert "Test" in Card(title="Test", body=["Test"]).render()
    assert "Live" in StatusBadge(label="Live", status="success").render()
    assert "Home / Portfolio" in Breadcrumb(items=["Home", "Portfolio"]).render()
    assert "AAPL" in DataTable(headers=["Symbol"], rows=[["AAPL"]]).render()
    assert "Equity" in KPIChartCard(title="Equity", value="100", subtitle="Up").render()
