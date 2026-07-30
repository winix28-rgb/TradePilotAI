"""
===========================================================
TradePilotAI Operating System
Application
===========================================================
"""

from .banner import print_banner
from .dashboard import DashboardPage
from .dashboard.data_provider import DashboardDataProvider

from .core.container import Container
from .core.registry import ServiceRegistry
from .core.service_manager import ServiceManager
from .core.config import ConfigurationManager

from .infrastructure.logging.logging_service import LoggingService


class Application:
    """
    Main TradePilotAI application.
    """

    def __init__(self) -> None:

        self.container = Container()
        self.registry = ServiceRegistry(self.container)
        self.service_manager = ServiceManager()

        # --------------------------------------------------
        # Core Services
        # --------------------------------------------------

        self.container.register_singleton(
            ConfigurationManager,
            ConfigurationManager(),
        )

        # --------------------------------------------------
        # Infrastructure Services
        # --------------------------------------------------

        self.logging_service = LoggingService()

        self.service_manager.register(self.logging_service)

    def run(self) -> None:

        print_banner()

        print("\nStarting services...")

        self.service_manager.start_all()

        print("\nApplication Ready\n")

        dashboard_provider = DashboardDataProvider(container=self.container, app=self)
        dashboard = DashboardPage(data_provider=dashboard_provider)
        dashboard.show()

    def shutdown(self) -> None:

        self.service_manager.stop_all()