"""Reusable UI component library for the TradePilotAI OS dashboards."""

from __future__ import annotations

from typing import Any


class BaseComponent:
    """Shared styling contract for all UI components."""

    def render(self) -> str:
        raise NotImplementedError

    def _frame(self, title: str, body: list[str]) -> str:
        width = 72
        title_text = f"[{title}]"
        lines = [title_text]
        lines.extend(f"- {line}" for line in body)
        return "\n".join(lines)


class Card(BaseComponent):
    """Generic card container with a shared visual shell."""

    def __init__(self, title: str, body: list[str] | None = None) -> None:
        self.title = title
        self.body = body or []

    def render(self) -> str:
        return self._frame(self.title, self.body)


class KPIChartCard(Card):
    """Card for displaying a metric value with optional trend text."""

    def __init__(self, title: str, value: str, subtitle: str | None = None) -> None:
        self.value = value
        self.subtitle = subtitle
        super().__init__(title, [value] if subtitle is None else [value, subtitle])


class ChartCard(Card):
    """Card for a simple chart-like summary."""

    def __init__(self, title: str, points: list[tuple[str, str]] | None = None) -> None:
        self.points = points or [("T1", "0")]
        super().__init__(title, [f"{label}: {value}" for label, value in self.points])


class StatusBadge(BaseComponent):
    """Badge representing a status state."""

    def __init__(self, label: str, status: str = "neutral") -> None:
        self.label = label
        self.status = status

    def render(self) -> str:
        return f"{self.label}[{self.status}]"


class Breadcrumb(BaseComponent):
    """Simple breadcrumb trail."""

    def __init__(self, items: list[str]) -> None:
        self.items = items

    def render(self) -> str:
        return " / ".join(self.items)


class Toolbar(BaseComponent):
    """Toolbar for page actions and controls."""

    def __init__(self, title: str, actions: list[str] | None = None) -> None:
        self.title = title
        self.actions = actions or []

    def render(self) -> str:
        if not self.actions:
            return self.title
        return f"{self.title}: {' | '.join(self.actions)}"


class DataTable(BaseComponent):
    """Simple table with headers and rows."""

    def __init__(self, headers: list[str], rows: list[list[Any]]) -> None:
        self.headers = headers
        self.rows = rows

    def render(self) -> str:
        header_row = " | ".join(self.headers)
        body_rows = [" | ".join(str(cell) for cell in row) for row in self.rows]
        return "\n".join([header_row, *body_rows])


class NotificationPanel(BaseComponent):
    """Panel for stacked alerts or notifications."""

    def __init__(self, items: list[str]) -> None:
        self.items = items

    def render(self) -> str:
        return "\n".join(f"• {item}" for item in self.items)


class SectionHeader(BaseComponent):
    """Section title with a consistent heading style."""

    def __init__(self, title: str, subtitle: str | None = None) -> None:
        self.title = title
        self.subtitle = subtitle

    def render(self) -> str:
        if self.subtitle:
            return f"{self.title} - {self.subtitle}"
        return self.title


class StatusBar(BaseComponent):
    """Reusable runtime status bar backed by services and auto-refresh support."""

    def __init__(self, container: Any | None = None, version: str = "0.0.0") -> None:
        self.container = container
        self.version = version
        self._state: dict[str, Any] = {}

    def render(self) -> str:
        self._state = self._collect_state()
        parts = [
            f"Broker Status: {self._format_status(self._state['broker_status'], warning=self._state['broker_warning'])}",
            f"Market Status: {self._format_status(self._state['market_status'], warning=self._state['market_warning'])}",
            f"Refresh Interval: {self._state['refresh_interval']}",
            f"Runtime: {self._state['runtime']}",
            f"Notification Count: {self._state['notification_count']}",
            f"Version Number: {self.version}",
        ]
        return " | ".join(parts)

    def refresh(self) -> None:
        refresh_manager = self._resolve_service("refresh_manager")
        if refresh_manager is not None and hasattr(refresh_manager, "refresh"):
            refresh_manager.refresh()
        self._state = self._collect_state()

    def _collect_state(self) -> dict[str, Any]:
        broker = self._resolve_service("broker")
        data_engine = self._resolve_service("data_engine")
        refresh_manager = self._resolve_service("refresh_manager")
        notifications = self._resolve_service("notifications")

        broker_status = self._read_broker_status(broker)
        market_status = self._read_market_status(data_engine)
        refresh_interval = self._read_refresh_interval(refresh_manager)
        runtime = self._read_runtime()
        notification_count = self._read_notification_count(notifications)

        return {
            "broker_status": broker_status,
            "broker_warning": broker_status == "Disconnected",
            "market_status": market_status,
            "market_warning": market_status == "Idle",
            "refresh_interval": refresh_interval,
            "runtime": runtime,
            "notification_count": notification_count,
        }

    def _resolve_service(self, name: str) -> Any | None:
        if self.container is None:
            return None
        if hasattr(self.container, "contains") and self.container.contains(name):
            return self.container.resolve(name)
        return None

    def _read_broker_status(self, broker: Any | None) -> str:
        if broker is None:
            return "Unavailable"
        if hasattr(broker, "connected"):
            return "Connected" if broker.connected else "Disconnected"
        return "Unavailable"

    def _read_market_status(self, data_engine: Any | None) -> str:
        if data_engine is None:
            return "Unavailable"
        if hasattr(data_engine, "is_running"):
            return "Live" if data_engine.is_running() else "Idle"
        return "Unavailable"

    def _read_refresh_interval(self, refresh_manager: Any | None) -> str:
        if refresh_manager is None:
            return "N/A"
        if hasattr(refresh_manager, "interval_seconds"):
            return f"{refresh_manager.interval_seconds}s"
        if hasattr(refresh_manager, "current_mode"):
            return str(refresh_manager.current_mode)
        return "N/A"

    def _read_runtime(self) -> str:
        return "Live"

    def _read_notification_count(self, notifications: Any | None) -> int:
        if notifications is None:
            return 0
        if hasattr(notifications, "count"):
            return int(notifications.count)
        return 0

    def _format_status(self, value: str, warning: bool = False) -> str:
        if warning:
            return f"\033[31m{value}\033[0m"
        return value
