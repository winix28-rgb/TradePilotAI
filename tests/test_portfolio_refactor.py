from tradepilotai_os.application_shell import ApplicationShell
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.portfolio.page import PortfolioPage
from tradepilotai_os.portfolio.position_detail import PositionDetailPage


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


def test_portfolio_page_uses_shell_and_breadcrumbs():
    navigation = NavigationService()
    portfolio_page = PortfolioPage(portfolio_service=StubPortfolioService(), navigation_service=navigation)
    navigation.register("portfolio", portfolio_page)

    shell = ApplicationShell(navigation_service=navigation)
    shell.show("portfolio")
    rendered = shell.render()

    assert "Portfolio Dashboard" in rendered or "PORTFOLIO DASHBOARD" in rendered
    assert "Dashboard / Portfolio" in rendered
    assert "AAPL" in rendered


def test_position_detail_page_still_renders_and_is_shell_ready():
    detail = PositionDetailPage(position=StubPortfolioService().state.positions["AAPL"])
    rendered = detail.render()

    assert "Position Detail" in rendered
    assert "AAPL" in rendered
    assert "Target" in rendered
