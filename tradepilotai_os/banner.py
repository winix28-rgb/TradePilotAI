from .version import VERSION
from .version import APPLICATION_NAME


def print_banner():

    print()

    print("=" * 60)
    print(APPLICATION_NAME)
    print(f"Version {VERSION}")
    print("=" * 60)
    print()
