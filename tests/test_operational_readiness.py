from tradepilotai_os.operations import ConfigurationValidator, ExceptionHandler, HealthCheckService, PerformanceMonitor, StartupValidator, create_logger
from tradepilotai_os.core.container import Container
from tradepilotai_os.core.config import ConfigurationManager
from tradepilotai_os.navigation import NavigationService
from tradepilotai_os.orchestration import ApplicationOrchestrator
from tradepilotai_os.broker import PaperBroker
from tradepilotai_os.risk.risk_engine import RiskEngine


class StubRefreshManager:
    def __init__(self) -> None:
        self.refresh_calls = 0

    def refresh(self) -> None:
        self.refresh_calls += 1


class StubNotifications:
    def __init__(self) -> None:
        self.count = 0


class StubScanner:
    def get_watchlist(self) -> list[str]:
        return ["AAPL"]


class StubRiskEngine:
    def assess_trade(self, trade) -> object:
        return type("Assessment", (), {"permitted": True, "reason": "ok"})()


class StubPortfolioService:
    def __init__(self) -> None:
        self.state = type("State", (), {"positions": {}, "cash": 1000.0})()


class StubHistoryService:
    def add_trade(self, trade) -> None:
        self.trades = [trade]


def test_logging_and_health_checks_work():
    logger = create_logger("TradePilotAI", correlation_id="abc123")
    logger.info("startup", module="application")

    health = HealthCheckService()
    health.register("broker", "READY", {"detail": "ok"})
    health.register("portfolio", "WARNING", {"detail": "degraded"})

    overview = health.report()
    assert overview["overall_status"] == "WARNING"
    assert health.get("broker").status == "READY"


def test_configuration_validator_rejects_invalid_settings():
    config = ConfigurationManager()
    config.set("risk", {"risk_per_trade": 0.02})
    config.set("strategy", {"rsi_period": 14})
    config.set("broker", {"type": "invalid"})
    config.set("portfolio", {})
    config.set("refresh", {"interval_seconds": 0})
    config.set("environment", {})

    validator = ConfigurationValidator(config)
    errors = validator.validate()

    assert any("Risk setting missing" in error for error in errors)
    assert any("Broker type" in error for error in errors)
    assert any("Refresh interval" in error for error in errors)


def test_startup_validator_reports_missing_services():
    config = ConfigurationManager()
    config.set("risk", {"risk_per_trade": 0.01, "max_position_size": 1000.0})
    config.set("broker", {"type": "paper"})
    config.set("strategy", {"rsi_period": 14, "ema_fast": 9, "ema_slow": 21})
    config.set("portfolio", {})
    config.set("refresh", {"interval_seconds": 30})

    container = Container()
    navigation = NavigationService()
    validator = StartupValidator(config, container, navigation)
    errors = validator.validate()

    assert any("Required service not registered" in error for error in errors)


def test_exception_handler_returns_user_friendly_message():
    handler = ExceptionHandler()
    message = handler.handle(ValueError("boom"), context="broker")
    assert "Operational warning" in message


def test_performance_monitor_tracks_calls():
    monitor = PerformanceMonitor()
    monitor.time_call("refresh", lambda: None)
    monitor.time_call("refresh", lambda: None)

    assert monitor.counts()["refresh"] == 2


def test_orchestrator_handles_workflow_and_perf_tracking():
    scanner = StubScanner()
    risk_engine = StubRiskEngine()
    broker = PaperBroker()
    portfolio = StubPortfolioService()
    history = StubHistoryService()
    refresh_manager = StubRefreshManager()
    notifications = StubNotifications()

    orchestrator = ApplicationOrchestrator(
        scanner=scanner,
        risk_engine=risk_engine,
        broker=broker,
        portfolio_service=portfolio,
        trade_history_service=history,
        refresh_manager=refresh_manager,
        notifications=notifications,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "completed"
    assert refresh_manager.refresh_calls == 1
    assert notifications.count == 1
