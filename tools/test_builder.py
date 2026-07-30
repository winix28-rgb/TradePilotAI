from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

from builder import ProjectBuilder


def main():
    builder = ProjectBuilder()

    builder.header("TradePilotAI Builder Test")

    builder.create_directory("test_folder")

    builder.write_file(
        "test_folder/test.txt",
        "Builder is working correctly!"
    )

    builder.verify()
    builder.summary()


if __name__ == "__main__":
    main()