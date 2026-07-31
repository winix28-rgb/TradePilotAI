from __future__ import annotations

from pathlib import Path
import logging
from typing import Any

from ...core.config import ConfigurationManager
from ...core.service import Service
from ...operations.logging_service import configure_logging, create_logger


class LoggingService(Service):

    def __init__(self, config: ConfigurationManager | None = None):
        self.config = config or ConfigurationManager()
        self.logger = create_logger("TradePilotAI")

    def start(self):
        logging_config = self.config.get("logging", {})
        if isinstance(logging_config, dict):
            level = logging_config.get("level", "INFO")
            console_enabled = logging_config.get("console_enabled", True)
            file_enabled = logging_config.get("file_enabled", True)
            file_path = logging_config.get("file_path", "logs/tradepilotai.log")
            max_bytes = logging_config.get("max_bytes", 5 * 1024 * 1024)
            backup_count = logging_config.get("backup_count", 3)
        else:
            level = "INFO"
            console_enabled = True
            file_enabled = True
            file_path = "logs/tradepilotai.log"
            max_bytes = 5 * 1024 * 1024
            backup_count = 3

        configure_logging(
            level=level,
            log_file=file_path,
            console_enabled=console_enabled,
            file_enabled=file_enabled,
            max_bytes=max_bytes,
            backup_count=backup_count,
        )
        self.logger.info("Logging service started.", module="infrastructure.logging")

    def stop(self):
        self.logger.info("Logging service stopped.", module="infrastructure.logging")
