"""
TradePilotAI Dashboard Launcher
"""

from pathlib import Path
import subprocess
import sys


def main():
    dashboard = Path(__file__).parent / "dashboard" / "app.py"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()