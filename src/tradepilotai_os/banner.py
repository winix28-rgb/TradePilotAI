"""Application banner."""

from .version import __version__


def print_banner() -> None:
    print("=" * 52)
    print("        TradePilotAI Operating System")
    print(f"                Version {__version__}")
    print("=" * 52)
    print()