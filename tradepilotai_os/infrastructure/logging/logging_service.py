from pathlib import Path
import logging

from ...core.service import Service


class LoggingService(Service):

    def __init__(self):

        self.logger = logging.getLogger("TradePilotAI")

    def start(self):

        log_directory = Path("logs")
        log_directory.mkdir(exist_ok=True)

        logfile = log_directory / "tradepilotai.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)-8s | %(message)s",
            handlers=[
                logging.FileHandler(logfile),
                logging.StreamHandler(),
            ],
        )

        self.logger.info("Logging service started.")

    def stop(self):

        self.logger.info("Logging service stopped.")
