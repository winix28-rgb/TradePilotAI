from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.backtesting import BacktestingPage, BacktestingDataProvider
from tradepilotai_os.navigation import NavigationService


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


def test_backtesting_page_renders_kpis_and_charts():
    container = StubContainer()
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications())

    provider = BacktestingDataProvider(container=container)
    page = BacktestingPage(data_provider=provider)
    rendered = page.render()

    assert "BACKTESTING DASHBOARD" in rendered
    assert "Total Return" in rendered
    assert "Net Profit" in rendered
    assert "CAGR" in rendered
    assert "Win Rate" in rendered
    assert "Profit Factor" in rendered
    assert "Sharpe Ratio" in rendered
    assert "Maximum Drawdown" in rendered
    assert "Total Trades" in rendered
    assert "Equity Curve" in rendered
    assert "Drawdown Curve" in rendered
    assert "Monthly Returns" in rendered
    assert "Win/Loss Distribution" in rendered
    assert "Best Trades" in rendered
    assert "Worst Trades" in rendered
    assert "Trade Statistics" in rendered
    assert "AAPL" in rendered


def test_backtesting_page_supports_navigation_and_shell():
    navigation = NavigationService()
    page = BacktestingPage(data_provider=BacktestingDataProvider())
    navigation.register("backtesting", page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("backtesting")
    rendered = shell.render()

    assert "BACKTESTING DASHBOARD" in rendered
    assert "Dashboard / Backtesting" in rendered
    assert "Status Bar" in rendered
