#!/usr/bin/env python3
"""
=========================================================
TradePilotAI Release Freeze Utility
=========================================================

Creates a release checkpoint by:

✓ Checking git status
✓ Staging all changes
✓ Creating a release commit
✓ Creating an annotated git tag
✓ Creating the next development branch
✓ Displaying next steps

Usage:

python scripts/freeze_release.py

=========================================================
"""

import subprocess
import sys

# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------

VERSION = "v1.0.0"
NEXT_BRANCH = "develop-v1.1"

COMMIT_MESSAGE = (
    "Release: TradePilotAI v1.0.0 "
    "- Research & Paper Trading Platform"
)

TAG_MESSAGE = "TradePilotAI Version 1.0"


# -------------------------------------------------------
# Helper
# -------------------------------------------------------

def run(command: list[str]) -> None:
    """Run a git command."""
    print("\n>", " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print("\n❌ Command failed.")
        sys.exit(result.returncode)


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():

    print("=" * 60)
    print("TradePilotAI Release Freeze")
    print("=" * 60)

    # ---------------------------------------------------

    print("\nChecking Git status...")

    run(["git", "status"])

    # ---------------------------------------------------

    print("\nStaging files...")

    run(["git", "add", "."])

    # ---------------------------------------------------

    print("\nCreating release commit...")

    run(
        [
            "git",
            "commit",
            "-m",
            COMMIT_MESSAGE,
        ]
    )

    # ---------------------------------------------------

    print("\nCreating annotated tag...")

    run(
        [
            "git",
            "tag",
            "-a",
            VERSION,
            "-m",
            TAG_MESSAGE,
        ]
    )

    # ---------------------------------------------------

    print("\nCreating next development branch...")

    run(
        [
            "git",
            "checkout",
            "-b",
            NEXT_BRANCH,
        ]
    )

    # ---------------------------------------------------

    print("\n")
    print("=" * 60)
    print("Release Complete")
    print("=" * 60)

    print(f"""
Version Tag

    {VERSION}

Next Development Branch

    {NEXT_BRANCH}

Suggested Commands

    git push origin main
    git push origin {VERSION}
    git push origin {NEXT_BRANCH}

Congratulations!

TradePilotAI Version 1.0 has been frozen.
""")


if __name__ == "__main__":
    main()