#!/usr/bin/env python3
"""
=========================================================
TradePilotAI Version 1.0 Checkpoint Creator
=========================================================

Creates a reproducible project checkpoint.

Outputs:
    checkpoint/
        version_info.txt
        requirements.txt
        project_tree.txt
        git_status.txt
        test_results.txt

Author: TradePilotAI
"""

from pathlib import Path
import subprocess
import platform
from datetime import datetime

CHECKPOINT_DIR = Path("checkpoint")
CHECKPOINT_DIR.mkdir(exist_ok=True)


def run(command: str) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )
        return result.stdout + result.stderr
    except Exception as ex:
        return str(ex)


print("Creating checkpoint...\n")

# -------------------------------------------------------
# Version information
# -------------------------------------------------------

version = f"""
TradePilotAI Version 1.0
Decision Engine Baseline

Checkpoint Created:
{datetime.now()}

Python:
{platform.python_version()}

Platform:
{platform.platform()}

Decision Rule Book:
Version 1.0

Assessment Components:
✔ Technical
✔ Strategy
✔ Risk
✔ Portfolio
✔ Market

Decision Engine:
✔ Rule Book
✔ Hard Overrides
✔ Decision Quality
✔ Recommendation Stability

Expected Test Status:
90 passed
"""

(CHECKPOINT_DIR / "version_info.txt").write_text(version)

# -------------------------------------------------------
# Requirements
# -------------------------------------------------------

print("Saving requirements...")
requirements = run("pip freeze")
(CHECKPOINT_DIR / "requirements.txt").write_text(requirements)

# -------------------------------------------------------
# Git status
# -------------------------------------------------------

print("Saving git status...")
git = run("git status")
git += "\n\n"
git += run("git log -1")
(CHECKPOINT_DIR / "git_status.txt").write_text(git)

# -------------------------------------------------------
# Project tree
# -------------------------------------------------------

print("Saving project structure...")

tree = run("find . -type f")
(CHECKPOINT_DIR / "project_tree.txt").write_text(tree)

# -------------------------------------------------------
# Run tests
# -------------------------------------------------------

print("Running test suite...")
tests = run("pytest -q")
(CHECKPOINT_DIR / "test_results.txt").write_text(tests)

print("\nCheckpoint complete.")
print(f"Files written to: {CHECKPOINT_DIR.resolve()}")