"""
===========================================================
TradePilotAI OS Builder
===========================================================

Reusable project builder used by all sprint generators.

Author : TradePilotAI OS
Version: 1.0.0
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


class ProjectBuilder:
    """
    Generic project builder.

    Responsible for:
        - Creating directories
        - Writing files
        - Verifying files exist
        - Reporting results
    """

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root).resolve()

        self.created_directories = []
        self.created_files = []

    # -----------------------------------------------------
    # Console
    # -----------------------------------------------------

    @staticmethod
    def header(title: str) -> None:
        print()
        print("=" * 60)
        print(title)
        print("=" * 60)

    @staticmethod
    def info(message: str) -> None:
        print(f"[INFO] {message}")

    @staticmethod
    def success(message: str) -> None:
        print(f"[ OK ] {message}")

    @staticmethod
    def error(message: str) -> None:
        print(f"[ERR ] {message}")

    # -----------------------------------------------------
    # Directories
    # -----------------------------------------------------

    def create_directory(self, relative_path: str) -> Path:

        directory = self.project_root / relative_path

        directory.mkdir(parents=True, exist_ok=True)

        self.created_directories.append(directory)

        self.success(f"Directory created: {relative_path}")

        return directory

    # -----------------------------------------------------
    # Files
    # -----------------------------------------------------

    def write_file(self, relative_path: str, content: str) -> Path:

        file_path = self.project_root / relative_path

        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")

        self.created_files.append(file_path)

        self.success(f"File written: {relative_path}")

        return file_path

    # -----------------------------------------------------
    # Verification
    # -----------------------------------------------------

    def verify(self) -> bool:

        self.header("Verification")

        ok = True

        for directory in self.created_directories:

            if directory.exists():
                self.success(directory.name)
            else:
                self.error(str(directory))
                ok = False

        for file in self.created_files:

            if file.exists():
                self.success(file.name)
            else:
                self.error(str(file))
                ok = False

        return ok

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    def summary(self) -> None:

        self.header("Build Summary")

        print(f"Directories : {len(self.created_directories)}")
        print(f"Files       : {len(self.created_files)}")
        print(f"Completed   : {datetime.now()}")

        print()
        