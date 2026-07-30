"""
TradePilotAI OS Migration Tool

Copies the source code from FTSE-Quant-Trader V2
into the TradePilotAI OS project.
"""

from pathlib import Path
import shutil

# ------------------------------------------------------------------
# CHANGE THESE TWO PATHS
# ------------------------------------------------------------------

SOURCE = Path("/Users/wilhelm/Documents/FTSE-Quant-Trader-V2")

DESTINATION = Path("/Users/wilhelm/Documents/TradePilotAI-OS")

# ------------------------------------------------------------------

MODULES = [
    "src/core",
    "src/config",
    "src/models",
    "src/market",
    "src/indicators",
    "src/signals",
    "src/strategy",
    "src/risk",
    "src/portfolio",
    "src/scanner",
    "src/backtesting",
]

FILES = [
    "config/settings.yaml",
]


def copy_directory(source: Path, destination: Path):

    if not source.exists():
        print(f"Skipping {source}")
        return

    print(f"Copying {source}")

    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
    )


def copy_file(source: Path, destination: Path):

    if not source.exists():
        print(f"Skipping {source}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source, destination)

    print(f"Copied {source}")


def main():

    print("=" * 60)
    print("TradePilotAI Migration")
    print("=" * 60)

    package_root = DESTINATION / "tradepilotai_os"

    for module in MODULES:

        src = SOURCE / module

        dst = package_root / Path(module).name

        copy_directory(src, dst)

    for file in FILES:

        src = SOURCE / file

        dst = DESTINATION / file

        copy_file(src, dst)

    print()
    print("=" * 60)
    print("Migration Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()