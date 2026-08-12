from tradepilotai_os.paper_trading import PaperTradingDataProvider
from tradepilotai_os.paper_trading import PaperTradingPage
from tradepilotai_os.paper_trading import PaperTradingService


def test_paper_trading_service_returns_engine_backed_workspace_data():
    service = PaperTradingService()

    payload = service.get_workspace_data()

    assert payload["summary"]["portfolio_value"] == 100000.0
    assert payload["summary"]["cash"] == 100000.0
    assert payload["summary"]["buying_power"] == 100000.0
    assert payload["summary"]["open_positions"] == 0
    assert payload["summary"]["closed_trades"] == 0
    assert len(payload["open_positions"]) == 0
    assert len(payload["closed_trades"]) == 0
    assert payload["statistics"]["total_trades"] == 0
    assert payload["statistics"]["cash_allocation"] == 100.0


def test_paper_trading_data_provider_loads_workspace_data():
    provider = PaperTradingDataProvider(service=PaperTradingService())

    payload = provider.get_paper_trading_data()

    assert payload["statistics"]["total_trades"] == 0
    assert payload["statistics"]["winning_trades"] == 0
    assert payload["statistics"]["losing_trades"] == 0


def test_paper_trading_page_renders_workspace_sections():
    page = PaperTradingPage(data_provider=PaperTradingDataProvider(service=PaperTradingService()))

    rendered = page.render()

    assert "PAPER TRADING WORKSPACE" in rendered
    assert "Portfolio Summary" in rendered
    assert "Open Positions" in rendered
    assert "Closed Trades" in rendered
    assert "Portfolio Statistics" in rendered