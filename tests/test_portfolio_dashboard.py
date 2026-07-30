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
                "exposure": 60000.0,
                "positions": {
                    "AAPL": type(
                        "Position",
                        (),
                        {
                            "symbol": "AAPL",
                            "quantity": 10,
                            "average_price": 100.0,
                            "market_price": 110.0,
                            "exposure": 1100.0,
                            "metadata": {"stop_loss": 95.0, "target": 120.0, "holding_time": "3d"},
                        },
                    )()
                },
            },
        )()


def test_portfolio_page_renders_summary_and_positions():
    page = PortfolioPage(portfolio_service=StubPortfolioService())
    rendered = page.render()

    assert "PORTFOLIO DASHBOARD" in rendered
    assert "Portfolio Value" in rendered
    assert "AAPL" in rendered
    assert "Open Positions" in rendered


def test_position_detail_page_renders_selected_position():
    detail = PositionDetailPage(position=StubPortfolioService().state.positions["AAPL"])
    rendered = detail.render()

    assert "Position Detail" in rendered
    assert "AAPL" in rendered
    assert "Target" in rendered
