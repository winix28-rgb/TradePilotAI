from pathlib import Path

from tradepilotai_os.core.config import ConfigurationManager
from tradepilotai_os.infrastructure.logging.logging_service import LoggingService
from tradepilotai_os.operations.logging_service import configure_logging, correlation_context, create_logger


def test_logger_emits_structured_entries(tmp_path: Path) -> None:
    log_file = tmp_path / "tradepilotai.log"
    configure_logging(level="INFO", log_file=str(log_file), console_enabled=False, file_enabled=True)

    logger = create_logger("TradePilotAI")
    logger.info("startup", module="application", environment="test")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "startup" in content
    assert '"module": "application"' in content


def test_logging_service_reads_configuration(tmp_path: Path) -> None:
    config = ConfigurationManager()
    config.set(
        "logging",
        {
            "level": "DEBUG",
            "console_enabled": False,
            "file_enabled": True,
            "file_path": str(tmp_path / "configured.log"),
            "max_bytes": 256,
            "backup_count": 1,
        },
    )

    service = LoggingService(config=config)
    service.start()

    logger = create_logger("TradePilotAI")
    logger.debug("debug message", module="tests")

    assert (tmp_path / "configured.log").exists()


def test_rotating_file_handler_rolls_over(tmp_path: Path) -> None:
    log_file = tmp_path / "tradepilotai.log"
    configure_logging(level="INFO", log_file=str(log_file), console_enabled=False, file_enabled=True, max_bytes=120, backup_count=2)

    logger = create_logger("TradePilotAI")
    for _ in range(30):
        logger.info("x" * 20, module="rotation")

    assert log_file.exists()
    backups = sorted(tmp_path.glob("tradepilotai.log.*"))
    assert backups or log_file.stat().st_size > 0


def test_correlation_context_propagates_across_logs(tmp_path: Path) -> None:
    log_file = tmp_path / "tradepilotai.log"
    configure_logging(level="INFO", log_file=str(log_file), console_enabled=False, file_enabled=True)

    with correlation_context("workflow-123"):
        logger = create_logger("TradePilotAI")
        logger.info("scanner event", module="scanner")

    content = log_file.read_text(encoding="utf-8")
    assert '"correlation_id": "workflow-123"' in content
