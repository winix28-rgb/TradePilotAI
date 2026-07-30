#!/usr/bin/env python3
"""
============================================================
TradePilotAI Operating System
Sprint 1 - Core Platform Generator
Part 1 of 3
============================================================
"""

from pathlib import Path
from textwrap import dedent
import shutil
import sys

# ----------------------------------------------------------
# Project Information
# ----------------------------------------------------------

PROJECT_NAME = "TradePilotAI-OS"

PACKAGE_NAME = "tradepilotai_os"

ROOT = Path.cwd()

SRC = ROOT / "src" / PACKAGE_NAME

# ----------------------------------------------------------
# Directories
# ----------------------------------------------------------

DIRECTORIES = [
    SRC,
    SRC / "core",
    SRC / "infrastructure",
    SRC / "infrastructure" / "logging",
    ROOT / "logs",
]

# ----------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------


def banner():

    print()
    print("=" * 60)
    print("TradePilotAI Operating System")
    print("Sprint 1 Generator")
    print("=" * 60)
    print()


def info(message):

    print(f"[INFO] {message}")


def ok(message):

    print(f"[ OK ] {message}")


def fail(message):

    print(f"[FAIL] {message}")


def create_directory(path: Path):

    path.mkdir(parents=True, exist_ok=True)

    ok(f"Directory : {path.relative_to(ROOT)}")


def write_file(relative_path: str, content: str):

    filename = ROOT / relative_path

    filename.parent.mkdir(parents=True, exist_ok=True)

    filename.write_text(
        dedent(content).lstrip(),
        encoding="utf-8",
    )

    ok(f"File      : {relative_path}")


# ----------------------------------------------------------
# Build Directories
# ----------------------------------------------------------


def build_directories():

    print()
    info("Creating directories")
    print()

    for directory in DIRECTORIES:

        create_directory(directory)


# ----------------------------------------------------------
# Source Files
# ----------------------------------------------------------

FILES = {}

FILES["src/tradepilotai_os/__init__.py"] = """
\"\"\"
TradePilotAI Operating System
\"\"\"

__version__ = "1.0.0"
"""

FILES["src/tradepilotai_os/version.py"] = """
VERSION = "1.0.0"
APPLICATION_NAME = "TradePilotAI Operating System"
"""

FILES["src/tradepilotai_os/banner.py"] = """
from .version import VERSION
from .version import APPLICATION_NAME


def print_banner():

    print()

    print("=" * 60)
    print(APPLICATION_NAME)
    print(f"Version {VERSION}")
    print("=" * 60)
    print()
"""

FILES["src/tradepilotai_os/core/__init__.py"] = """
\"\"\"Core package.\"\"\"
"""

FILES["src/tradepilotai_os/infrastructure/__init__.py"] = """
\"\"\"Infrastructure package.\"\"\"
"""

FILES["src/tradepilotai_os/infrastructure/logging/__init__.py"] = """
\"\"\"Logging package.\"\"\"
"""
# ----------------------------------------------------------
# Remaining Source Files
# ----------------------------------------------------------

FILES["src/tradepilotai_os/core/service.py"] = """
class Service:
    \"""
    Base class for all services.
    \"""

    def start(self):
        pass

    def stop(self):
        pass
"""

FILES["src/tradepilotai_os/core/service_manager.py"] = """
class ServiceManager:

    def __init__(self):

        self._services = []

    def register(self, service):

        self._services.append(service)

    def start_all(self):

        for service in self._services:

            service.start()

    def stop_all(self):

        for service in reversed(self._services):

            service.stop()
"""

FILES["src/tradepilotai_os/infrastructure/logging/logging_service.py"] = """
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
"""

FILES["src/tradepilotai_os/application.py"] = """
from .banner import print_banner

from .core.service_manager import ServiceManager

from .infrastructure.logging.logging_service import LoggingService


class Application:

    def __init__(self):

        self.services = ServiceManager()

        self.services.register(LoggingService())

    def run(self):

        print_banner()

        print("Starting services...")

        self.services.start_all()

        print()

        print("Application Ready")

        print()

    def shutdown(self):

        self.services.stop_all()
"""

FILES["src/tradepilotai_os/__main__.py"] = """
from .application import Application


def main():

    app = Application()

    try:

        app.run()

    finally:

        app.shutdown()


if __name__ == "__main__":

    main()
"""

# ----------------------------------------------------------
# Write Files
# ----------------------------------------------------------

def build_files():

    print()
    info("Creating files")
    print()

    for filename, contents in FILES.items():

        write_file(filename, contents)
        # ----------------------------------------------------------
# Verification
# ----------------------------------------------------------

def verify():

    print()
    info("Verifying project")
    print()

    ok = True

    for directory in DIRECTORIES:

        if directory.exists():

            print(f"[ OK ] {directory.relative_to(ROOT)}")

        else:

            print(f"[FAIL] Missing directory: {directory.relative_to(ROOT)}")

            ok = False

    for filename in FILES:

        path = ROOT / filename

        if path.exists():

            print(f"[ OK ] {filename}")

        else:

            print(f"[FAIL] Missing file: {filename}")

            ok = False

    return ok


# ----------------------------------------------------------
# Clean Previous Build
# ----------------------------------------------------------

def clean():

    package = ROOT / "src" / PACKAGE_NAME

    if package.exists():

        shutil.rmtree(package)

        info("Previous package removed")

    logs = ROOT / "logs"

    logs.mkdir(exist_ok=True)


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():

    banner()

    clean()

    build_directories()

    build_files()

    print()

    if verify():

        print()
        print("=" * 60)
        print("SPRINT 1 COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Next command:")
        print()
        print("uv sync")
        print("uv run tradepilotai-os")
        print()

    else:

        print()
        fail("Sprint 1 failed.")
        sys.exit(1)


if __name__ == "__main__":

    main()