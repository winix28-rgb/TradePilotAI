from __future__ import annotations

from datetime import datetime, timezone

from tradepilotai_os.models.trade import Trade
from tradepilotai_os.paper_trading import PaperPortfolioEngine
from tradepilotai_os.paper_trading import PaperTradingDataProvider
from tradepilotai_os.paper_trading import PaperTradingPage
from tradepilotai_os.paper_trading import PaperTradingService
from tradepilotai_os.paper_trading import PositionMonitor
from tradepilotai_os.risk.risk_engine import RiskEngine


class StubMarketDataProvider:
    def __init__(self, quotes: dict[str, object]) -> None:
        self.quotes = quotes

    def quote(self, symbol: str):
        value = self.quotes[symbol]
        if isinstance(value, Exception):
            raise value
        return value


def _trade(symbol: str, entry_price: float, stop_loss: float, direction: str = "BUY") -> Trade:
    return Trade(
        ticker=symbol,
        direction=direction,
        entry_time=datetime.now(timezone.utc),
        entry_price=entry_price,
        stop_loss=stop_loss,
        quantity=1,
        take_profit=130.0,
    )


def _open_position(engine: PaperPortfolioEngine, symbol: str, entry_price: float, stop_loss: float, direction: str = "BUY") -> None:
    trade = _trade(symbol, entry_price, stop_loss, direction)
    risk_engine = RiskEngine(account_balance=100000.0, risk_per_trade=0.01, max_position_size=1000.0)
    engine.open_position(
        trade=trade,
        strategy_id="strategy-rsi",
        strategy_name="RSI Mean Reversion",
        decision_id=f"DEC-{symbol}",
        risk_assessment=risk_engine.assess_trade(trade),
    )


def test_single_position_refresh_updates_live_metrics() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", entry_price=100.0, stop_loss=95.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider({"AAPL": {"symbol": "AAPL", "price": 110.0, "open": 108.0}}),
    )

    result = monitor.refresh()
    position = engine.get_open_positions()[0]

    assert result["failed_symbols"] == []
    assert position.current_price == 110.0
    assert position.market_value == 22000.0
    assert position.unrealised_pnl == 2000.0
    assert position.unrealised_pnl_percent == 10.0
    assert position.todays_change == 2.0
    assert position.price_status == "LIVE"
    assert position.last_updated
    assert engine.get_summary()["current_equity"] == 102000.0
    assert engine.get_statistics().current_exposure == 22000.0
    assert any(event["event"] == "MARKET_PRICE_UPDATED" for event in engine.get_audit_events())


def test_multiple_position_refresh_updates_winners_losers_and_exposure() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", entry_price=100.0, stop_loss=95.0)
    _open_position(engine, "MSFT", entry_price=200.0, stop_loss=190.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider(
            {
                "AAPL": {"symbol": "AAPL", "price": 112.0, "open": 109.0},
                "MSFT": {"symbol": "MSFT", "price": 190.0, "open": 194.0},
            }
        ),
    )

    result = monitor.refresh()
    statistics = engine.get_statistics()

    assert len(result["refreshed_positions"]) == 2
    assert engine.get_summary()["open_positions"] == 2
    assert engine.get_summary()["current_exposure"] == 41400.0
    assert statistics.largest_winner == 2400.0
    assert statistics.largest_loser == -1000.0
    assert statistics.largest_position == 22400.0
    assert statistics.smallest_position == 19000.0
    assert statistics.average_position_size == 20700.0


def test_market_price_decrease_updates_unrealised_loss() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "TSLA", entry_price=100.0, stop_loss=95.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider({"TSLA": {"symbol": "TSLA", "price": 92.0, "open": 98.0}}),
    )

    monitor.refresh()
    position = engine.get_open_positions()[0]

    assert position.unrealised_pnl == -1600.0
    assert position.todays_change == -6.0
    assert position.price_status == "LIVE"


def test_failed_price_lookup_does_not_stop_other_updates() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", entry_price=100.0, stop_loss=95.0)
    _open_position(engine, "MSFT", entry_price=200.0, stop_loss=190.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider(
            {
                "AAPL": RuntimeError("lookup failed"),
                "MSFT": {"symbol": "MSFT", "price": 210.0, "open": 205.0},
            }
        ),
    )

    result = monitor.refresh()
    aapl = next(item for item in engine.get_open_positions() if item.symbol == "AAPL")
    msft = next(item for item in engine.get_open_positions() if item.symbol == "MSFT")

    assert len(result["failed_symbols"]) == 1
    assert result["failed_symbols"][0]["symbol"] == "AAPL"
    assert aapl.price_status == "STALE"
    assert aapl.price_stale is True
    assert msft.current_price == 210.0
    assert msft.price_status == "LIVE"


def test_refresh_with_no_positions_keeps_portfolio_intact() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    monitor = PositionMonitor(portfolio_engine=engine, market_data_provider=StubMarketDataProvider({}))

    result = monitor.refresh()

    assert result["refreshed_positions"] == []
    assert result["failed_symbols"] == []
    assert engine.get_summary()["open_positions"] == 0
    assert engine.get_summary()["current_equity"] == 100000.0


def test_service_refresh_updates_workspace_payload() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", entry_price=100.0, stop_loss=95.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider({"AAPL": {"symbol": "AAPL", "price": 109.0, "open": 108.0}}),
    )
    service = PaperTradingService(portfolio_engine=engine, position_monitor=monitor)
    provider = PaperTradingDataProvider(service=service)

    payload = provider.refresh()

    assert payload["summary"]["current_equity"] == 101800.0
    assert payload["summary"]["current_exposure"] == 21800.0
    assert payload["open_positions"][0]["current_price"] == 109.0
    assert payload["open_positions"][0]["price_status"] == "LIVE"


def test_page_refresh_uses_updated_service_payload() -> None:
    engine = PaperPortfolioEngine(initial_capital=100000.0)
    _open_position(engine, "AAPL", entry_price=100.0, stop_loss=95.0)
    monitor = PositionMonitor(
        portfolio_engine=engine,
        market_data_provider=StubMarketDataProvider({"AAPL": {"symbol": "AAPL", "price": 109.0, "open": 108.0}}),
    )
    service = PaperTradingService(portfolio_engine=engine, position_monitor=monitor)
    page = PaperTradingPage(data_provider=PaperTradingDataProvider(service=service))

    page.refresh()

    assert page.data["summary"]["current_equity"] == 101800.0
    assert page.data["open_positions"][0]["current_price"] == 109.0
    assert page.data["open_positions"][0]["todays_change"] == 1.0