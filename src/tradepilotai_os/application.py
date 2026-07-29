"""Application lifecycle."""

from tradepilotai_os.banner import print_banner
from tradepilotai_os.core.service_manager import ServiceManager
from tradepilotai_os.infrastructure.logging.logging_service import LoggingService


class Application:
    """Main application."""

    def run(self) -> None:
        print_banner()

        manager = ServiceManager()

        manager.register(LoggingService())

        manager.start_all()

        print()
        print("Application Ready")