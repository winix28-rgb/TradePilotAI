"""
===========================================================
TradePilotAI
CSV Loader
===========================================================

Loads OHLCV data from a CSV file into HistoricalData.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from backtesting.candle import Candle
from backtesting.historical_data import HistoricalData


class CSVLoader:
    """
    Loads historical market data from a CSV file.
    """

    DATE_FORMATS = (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
    )

    def load(self, filename: str | Path) -> HistoricalData:
        """
        Load historical data from a CSV file.
        """

        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(path)

        candles: list[Candle] = []

        with path.open("r", newline="", encoding="utf-8-sig") as csv_file:

            reader = csv.DictReader(csv_file)

            required_columns = {
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            }

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header.")

            missing = required_columns.difference(reader.fieldnames)

            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}"
                )

            for row in reader:

                candles.append(
                    Candle(
                        timestamp=self._parse_date(row["Date"]),
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=float(row["Volume"]),
                    )
                )

        return HistoricalData(candles)

    def _parse_date(self, value: str) -> datetime:
        """
        Parse supported date formats.
        """

        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass

        raise ValueError(f"Unsupported date format: {value}")