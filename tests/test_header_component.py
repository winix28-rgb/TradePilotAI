from tradepilotai_os.header import Header


class StubBroker:
    def __init__(self) -> None:
        self.connected = True


class StubDataEngine:
    def __init__(self) -> None:
        self._running = True

    def is_running(self) -> bool:
        return self._running


class StubRefreshManager:
    def __init__(self) -> None:
        self.current_mode = "10 seconds"
        self.last_refresh = "2026-07-30T00:00:00"


class StubNavigationService:
    def current_route(self) -> str:
        return "dashboard"


def test_header_renders_required_labels_and_values():
    header = Header(
        broker=StubBroker(),
        data_engine=StubDataEngine(),
        refresh_manager=StubRefreshManager(),
        navigation_service=StubNavigationService(),
    )

    rendered = header.render()

    assert "TradePilotAI OS" in rendered
    assert "Trading Mode" in rendered
    assert "Broker Status" in rendered
    assert "Market Status" in rendered
    assert "Notifications" in rendered
    assert "Refresh Status" in rendered


def test_header_handles_missing_services_gracefully():
    header = Header()
    rendered = header.render()

    assert "Unavailable" in rendered


def test_header_current_time_uses_utc_clock():
    header = Header()
    rendered = header.render()

    current_time_line = next(line for line in rendered.splitlines() if line.startswith("Current Time: "))
    assert current_time_line.endswith("Z")
