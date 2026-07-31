"""
===========================================================
TradePilotAI Operating System
Application
===========================================================
"""

from .banner import print_banner
from .dashboard import DashboardPage
from .dashboard.data_provider import DashboardDataProvider
from .scanner import ScannerDataProvider as ScannerDashboardDataProvider
from .scanner import ScannerPage
from .trade_history import TradeHistoryDataProvider as TradeHistoryDashboardDataProvider
from .trade_history import TradeHistoryPage
from .risk import RiskDashboardPage, RiskDataProvider as RiskDashboardDataProvider
from .live_trading import LiveTradingDataProvider as LiveTradingDashboardDataProvider
from .live_trading import LiveTradingPage
from .strategy import StrategyDataProvider as StrategyDashboardDataProvider
from .strategy import StrategyPage

from .core.container import Container
from .core.registry import ServiceRegistry
from .core.service_manager import ServiceManager
from .core.config import ConfigurationManager

from .infrastructure.logging.logging_service import LoggingService
from .operations import ConfigurationValidator, ExceptionHandler, HealthCheckService, PerformanceMonitor, StartupValidator, create_logger


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

        self.logging_service = LoggingService(self.container.resolve(ConfigurationManager))
        self.logger = create_logger("TradePilotAI")
        self.exception_handler = ExceptionHandler(self.logger)
        self.health_service = HealthCheckService()
        self.performance_monitor = PerformanceMonitor()
        self.config_validator = ConfigurationValidator()
        self.startup_validator = StartupValidator()

        self.service_manager.register(self.logging_service)

    def run(self) -> None:

        print_banner()

        print("\nStarting services...")

        self.service_manager.start_all()

        self.logger.info("Application startup began", module="application")
        self._register_core_dependencies()
        self._validate_startup()
        self.logger.info("Application startup completed", module="application")

        print("\nApplication Ready\n")

        dashboard_provider = DashboardDataProvider(container=self.container, app=self)
        dashboard = DashboardPage(data_provider=dashboard_provider)
        dashboard.show()

        scanner_provider = ScannerDashboardDataProvider(container=self.container)
        scanner_page = ScannerPage(data_provider=scanner_provider)
        scanner_page.render()

        trade_history_provider = TradeHistoryDashboardDataProvider(container=self.container)
        trade_history_page = TradeHistoryPage(data_provider=trade_history_provider)
        trade_history_page.render()

        risk_provider = RiskDashboardDataProvider(container=self.container)
        risk_page = RiskDashboardPage(data_provider=risk_provider)
        risk_page.render()

        live_trading_provider = LiveTradingDashboardDataProvider(container=self.container)
        live_trading_page = LiveTradingPage(data_provider=live_trading_provider)
        live_trading_page.render()

        strategy_provider = StrategyDashboardDataProvider(container=self.container)
        strategy_page = StrategyPage(data_provider=strategy_provider)
        strategy_page.render()

    def _register_core_dependencies(self) -> None:
        self.container.register_singleton("config", ConfigurationManager())
        self.container.register_singleton("logger", self.logger)
        self.container.register_singleton("exception_handler", self.exception_handler)
        self.container.register_singleton("health_service", self.health_service)
        self.container.register_singleton("performance_monitor", self.performance_monitor)
        self.container.register_singleton("notifications", type("Notifications", (), {"count": 0})())
        self.container.register_singleton("refresh_manager", type("RefreshManager", (), {"current_mode": "30s", "interval_seconds": 30, "refresh": lambda self: None})())
        self.container.register_singleton("broker", type("Broker", (), {"connected": True})())
        self.container.register_singleton("data_engine", type("DataEngine", (), {"is_running": lambda self: True})())

    def _validate_startup(self) -> None:
        config = self.container.resolve("config")
        self.config_validator = ConfigurationValidator(config)
        self.startup_validator = StartupValidator(config, self.container, type("Navigation", (), {"_routes": {"portfolio": object(), "scanner": object(), "backtesting": object(), "trade_history": object(), "risk": object(), "live_trading": object(), "strategy": object()}})())
        errors = self.config_validator.validate()
        errors.extend(self.startup_validator.validate())
        if errors:
            self.logger.warning("Startup validation reported issues", module="application", errors=errors)
            for error in errors:
                self.exception_handler.handle(ValueError(error), context="application")
        else:
            self.logger.info("Startup validation passed", module="application")

    def shutdown(self) -> None:

        self.service_manager.stop_all()