"""
===========================================================
TradePilotAI
CSV Loader Tests
===========================================================
"""

from pathlib import Path

import pytest

from backtesting.csv_loader import CSVLoader


def test_load_csv(tmp_path: Path) -> None:
    """
    Verify a valid CSV file loads successfully.
    """

    csv_file = tmp_path / "prices.csv"

    csv_file.write_text(
        "\n".join(
            [
                "Date,Open,High,Low,Close,Volume",
                "2025-01-01,100,105,99,104,10000",
                "2025-01-02,104,108,103,107,12000",
            ]
        )
    )

    loader = CSVLoader()

    data = loader.load(csv_file)

    assert data.length == 2

    assert data.first.open == 100

    assert data.last.close == 107


def test_missing_file_raises_error() -> None:
    """
    Verify missing files raise FileNotFoundError.
    """

    loader = CSVLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("does_not_exist.csv")


def test_missing_columns_raise_error(tmp_path: Path) -> None:
    """
    Verify invalid CSV headers are rejected.
    """

    csv_file = tmp_path / "invalid.csv"

    csv_file.write_text(
        "\n".join(
            [
                "Date,Open,Close",
                "2025-01-01,100,101",
            ]
        )
    )

    loader = CSVLoader()

    with pytest.raises(ValueError):
        loader.load(csv_file)