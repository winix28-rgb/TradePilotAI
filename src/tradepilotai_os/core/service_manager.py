"""Service manager."""

from tradepilotai_os.core.service import Service


class ServiceManager:
    """Starts and stops registered services."""

    def __init__(self) -> None:
        self._services: list[Service] = []

    def register(self, service: Service) -> None:
        self._services.append(service)

    def start_all(self) -> None:
        for service in self._services:
            print(f"Starting {service.name}...")
            service.start()

    def stop_all(self) -> None:
        for service in reversed(self._services):
            service.stop()