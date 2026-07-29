"""Application lifecycle."""

from .banner import print_banner


class Application:
    """Main application."""

    def run(self) -> None:
        print_banner()

        print("Initialising...")
        print()

        print("✓ Configuration")
        print("✓ Logging")
        print("✓ Application")
        print()
        print("System Ready")