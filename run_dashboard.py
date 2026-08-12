"""
TradePilotAI Dashboard Launcher
"""

from pathlib import Path
import subprocess
import sys
import os


def main():
    project_root = Path(__file__).parent
    dashboard = project_root / "dashboard" / "app.py"
    environment = dict(os.environ)
    python_path = environment.get("PYTHONPATH", "")
    if python_path:
        environment["PYTHONPATH"] = f"{project_root}{os.pathsep}{python_path}"
    else:
        environment["PYTHONPATH"] = str(project_root)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard),
        ],
        env=environment,
        check=True,
    )


if __name__ == "__main__":
    main()