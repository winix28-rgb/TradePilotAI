"""
TradePilotAI OS - Migration Tool (Version 1)

This tool helps locate an older TradePilotAI / FTSE-Quant-Trader
project ready for migration.

Version 1 only discovers the project and reports what it finds.
No files are copied.
"""

from pathlib import Path


IGNORE = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "reports",
    "dist",
    "build",
    "__MACOSX",
}


MODULES = [
    "core",
    "config",
    "models",
    "market",
    "broker",
    "indicators",
    "signals",
    "strategy",
    "risk",
    "portfolio",
    "scanner",
    "backtesting",
]


def banner():
    print("=" * 60)
    print(" TradePilotAI OS Migration Tool")
    print(" Version 1")
    print("=" * 60)
    print()


def get_project():

    project = input("Enter the FULL path to the old project:\n> ").strip()

    project = Path(project).expanduser()

    if not project.exists():
        print()
        print("❌ Folder not found.")
        return None

    return project


def scan(project: Path):

    print()
    print("Scanning project...")
    print()

    found = []

    for folder in project.rglob("*"):

        if not folder.is_dir():
            continue

        if any(part in IGNORE for part in folder.parts):
            continue

        if folder.name in MODULES:
            found.append(folder)

    return found


def report(project: Path, modules):

    print()
    print("=" * 60)
    print("PROJECT")
    print("=" * 60)

    print(project)

    print()
    print("=" * 60)
    print("MODULES FOUND")
    print("=" * 60)

    if not modules:
        print("No recognised modules found.")
        return

    for module in sorted(modules):
        print(f"✓ {module.relative_to(project)}")

    print()
    print(f"{len(modules)} module(s) found.")


def main():

    banner()

    project = get_project()

    if project is None:
        return

    modules = scan(project)

    report(project, modules)


if __name__ == "__main__":
    main()