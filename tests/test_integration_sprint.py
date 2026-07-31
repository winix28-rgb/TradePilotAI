from tradepilotai_os.application import Application
from tradepilotai_os.backtesting.page import BacktestingPage
from tradepilotai_os.broker import BrokerInterface, PaperBroker
from tradepilotai_os.broker.ig_broker_adapter import IGBrokerAdapter
from tradepilotai_os.dashboard.page import DashboardPage
from tradepilotai_os.live_trading.page import LiveTradingPage
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.orchestration import ApplicationOrchestrator
from tradepilotai_os.portfolio.page import PortfolioPage
from tradepilotai_os.risk.module.page import RiskDashboardPage
from tradepilotai_os.scanner.module.page import ScannerPage
from tradepilotai_os.strategy.page import StrategyPage
from tradepilotai_os.trade_history.page import TradeHistoryPage
from tradepilotai_os.workspace import WorkspacePage


class StubScanner:
    def __init__(self) -> None:
        self.watchlist = ["AAPL"]

    def get_watchlist(self) -> list[str]:
        return list(self.watchlist)


class StubRiskEngine:
    def __init__(self) -> None:
        self.assessed = []

    def assess_trade(self, trade) -> object:
        self.assessed.append(trade)
        return type("Assessment", (), {"permitted": True, "position_size": 5.0})()


class StubBroker:
    def __init__(self) -> None:
        self.executed = []

    def execute(self, trade) -> object:
        self.executed.append(trade)
        return type("Result", (), {"success": True, "message": "ok"})()


class StubPortfolioService:
    def __init__(self) -> None:
        self.state = type("State", (), {"positions": {}, "cash": 1000.0, "unrealised_pnl": 0.0, "realised_pnl": 0.0, "buying_power": 1000.0, "today_pnl": 0.0, "total_return": 0.0})()


class StubHistoryService:
    def __init__(self) -> None:
        self.trades = []

    def add_trade(self, trade) -> None:
        self.trades.append(trade)


class StubRefreshManager:
    def __init__(self) -> None:
        self.refresh_calls = 0

    def refresh(self) -> None:
        self.refresh_calls += 1


class StubNotifications:
    def __init__(self) -> None:
        self.count = 0


def test_workspace_pages_share_common_base_class():
    pages = [DashboardPage(), PortfolioPage(), ScannerPage(), BacktestingPage(), TradeHistoryPage(), RiskDashboardPage(), LiveTradingPage(), StrategyPage()]
    for page in pages:
        assert isinstance(page, WorkspacePage)


def test_broker_interfaces_and_adapters_are_consistent():
    assert issubclass(PaperBroker, BrokerInterface)
    adapter = IGBrokerAdapter()
    assert isinstance(adapter, BrokerInterface)


def test_application_orchestrator_runs_complete_workflow():
    scanner = StubScanner()
    risk_engine = StubRiskEngine()
    broker = StubBroker()
    portfolio = StubPortfolioService()
    history = StubHistoryService()
    refresh_manager = StubRefreshManager()
    notifications = StubNotifications()

    orchestrator = ApplicationOrchestrator(
        scanner=scanner,
        risk_engine=risk_engine,
        broker=broker,
        portfolio_service=portfolio,
        trade_history_service=history,
        refresh_manager=refresh_manager,
        notifications=notifications,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "completed"
    assert broker.executed
    assert history.trades
    assert refresh_manager.refresh_calls >= 1
    assert notifications.count >= 1


def test_dashboard_navigation_routes_are_registered():
    navigation = NavigationService()
    dashboard = DashboardPage(navigation_service=navigation)
    dashboard.render()

    for route in ["portfolio", "scanner", "backtesting", "trade_history", "risk", "live_trading", "strategy"]:
        assert navigation.navigate(route) == route
