from tradepilotai_os.ui_library import StatusBar


class StubBroker:
    def __init__(self, connected: bool = True) -> None:
        self.connected = connected


class StubDataEngine:
    def __init__(self, running: bool = True) -> None:
        self._running = running

    def is_running(self) -> bool:
        return self._running


class StubRefreshManager:
    def __init__(self) -> None:
        self.current_mode = "30s"
        self.interval_seconds = 30
        self.last_refresh = "2026-07-30T00:00:00"
        self.refresh_calls = 0

    def refresh(self) -> None:
        self.refresh_calls += 1


class StubNotifications:
    def __init__(self, count: int = 2) -> None:
        self.count = count


class StubContainer:
    def __init__(self) -> None:
        self._services = {}

    def register_singleton(self, name: str, instance: object) -> None:
        self._services[name] = instance

    def resolve(self, name: str) -> object:
        return self._services[name]

    def contains(self, name: str) -> bool:
        return name in self._services


def test_status_bar_renders_runtime_state_and_warning_colors():
    container = StubContainer()
    container.register_singleton("broker", StubBroker(connected=False))
    container.register_singleton("data_engine", StubDataEngine(running=False))
    container.register_singleton("refresh_manager", StubRefreshManager())
    container.register_singleton("notifications", StubNotifications(count=3))

    bar = StatusBar(container=container, version="1.2.3")
    rendered = bar.render()

    assert "Broker Status" in rendered
    assert "Market Status" in rendered
    assert "Refresh Interval" in rendered
    assert "Runtime" in rendered
    assert "Notification Count" in rendered
    assert "Version Number" in rendered
    assert "Disconnected" in rendered
    assert "Idle" in rendered
    assert "1.2.3" in rendered
    assert "\033[31m" in rendered


def test_status_bar_refreshes_through_refresh_manager():
    container = StubContainer()
    container.register_singleton("broker", StubBroker(connected=True))
    container.register_singleton("data_engine", StubDataEngine(running=True))
    refresh_manager = StubRefreshManager()
    container.register_singleton("refresh_manager", refresh_manager)
    container.register_singleton("notifications", StubNotifications(count=1))

    bar = StatusBar(container=container, version="0.9.0")
    bar.refresh()

    assert refresh_manager.refresh_calls == 1
    assert "Connected" in bar.render()
