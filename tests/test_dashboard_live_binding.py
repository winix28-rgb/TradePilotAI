from tradepilotai_os.core.container import Container
from tradepilotai_os.dashboard.data_provider import DashboardDataProvider
from tradepilotai_os.dashboard.page import DashboardPage


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
        self.state = type("State", (), {"cash": 5000.0, "exposure": 1200.0, "positions": {"AAPL": object()}, "realised_pnl": 200.0, "unrealised_pnl": 100.0})()


class StubBroker:
    def __init__(self) -> None:
        self.portfolio = type("Portfolio", (), {"cash": 4500.0, "exposure": 1100.0, "positions": {"MSFT": object()}, "realised_pnl": 300.0})()
        self.executed_trades = [type("Trade", (), {"ticker": "AAPL", "direction": "BUY", "entry_price": 100.0})()]


def test_dashboard_data_provider_uses_container_services():
    container = Container()
    container.register_singleton("data_engine", StubDataEngine())
    container.register_singleton("broker", StubBroker())
    container.register_singleton("config", StubConfig())
    container.register_singleton("portfolio_manager", StubPortfolioManager())
    container.register_singleton("scanner", type("Scanner", (), {"get_watchlist": lambda self: ["AAPL", "MSFT"]})())

    provider = DashboardDataProvider(container=container, app=type("App", (), {"last_run_summary": {"signals_generated": 2, "orders_executed": 1}})())
    data = provider.get_dashboard_data()

    assert data["system_status"]["status"] == "ONLINE"
    assert data["kpis"]["Equity"] == "$5,300.00"
    assert data["pipeline_summary"]["signals_generated"] == 2
    assert data["portfolio_snapshot"]["positions"] == 1
    assert data["scanner_summary"][0]["symbol"] == "AAPL"
    assert data["recent_trades"][0]["symbol"] == "AAPL"


def test_dashboard_page_uses_injected_provider_when_present():
    container = Container()
    container.register_singleton("data_engine", StubDataEngine())
    container.register_singleton("broker", StubBroker())
    container.register_singleton("config", StubConfig())
    container.register_singleton("portfolio_manager", StubPortfolioManager())
    container.register_singleton("scanner", type("Scanner", (), {"get_watchlist": lambda self: ["AAPL"]})())

    provider = DashboardDataProvider(container=container, app=type("App", (), {"last_run_summary": {"signals_generated": 3, "orders_executed": 2}})())
    page = DashboardPage(data_provider=provider)
    rendered = page.render()

    assert "TRADEPILOTAI OS DASHBOARD" in rendered
    assert "System Status" in rendered
    assert "Pipeline Summary" in rendered
    assert "AAPL" in rendered
