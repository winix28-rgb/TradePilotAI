from types import SimpleNamespace

from dashboard import app as dashboard_app


def test_ensure_dashboard_state_injects_scanner_service() -> None:
    state = SimpleNamespace()

    result = dashboard_app._ensure_dashboard_state(state)

    assert result is state
    assert getattr(state, "market_scanner_service", None) is not None
    assert type(state.market_scanner_service).__name__ == "ScannerService"


def test_ensure_dashboard_state_injects_portfolio_service() -> None:
    state = SimpleNamespace()

    result = dashboard_app._ensure_dashboard_state(state)

    assert result is state
    assert getattr(state, "portfolio_service", None) is not None
    assert getattr(state, "portfolio_manager", None) is not None
