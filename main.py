"""
===========================================================
TradePilotAI
Main Application
Version 3.0
===========================================================

Entry point for the application.
"""

from config import settings
from data.data_loader import DataLoader
from indicators.indicator_engine import IndicatorEngine


def main():
    """
    Main application entry point.
    """

    print("=" * 60)
    print("TradePilotAI")
    print("=" * 60)

    ticker = "RR.L"

    print(f"\nLoading data for {ticker}...")

    data = DataLoader.load_yahoo(
        ticker=ticker,
        start_date=settings.START_DATE,
        end_date=settings.END_DATE,
    )

    print(f"Loaded {len(data)} candles")

    print("\nCalculating indicators...")

    data = IndicatorEngine.add_indicators(data)

    print("\nLatest Market Data\n")

    print(
        data[
            [
                "Close",
                "EMA12",
                "EMA26",
                "RSI",
            ]
        ].tail()
    )


if __name__ == "__main__":
    main()