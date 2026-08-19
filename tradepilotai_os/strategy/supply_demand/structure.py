"""
===========================================================
TradePilotAI OS
Supply & Demand H1 Structure Engine
===========================================================

Identifies H1 swing highs/lows and classifies them as:

    HH - Higher High
    HL - Higher Low
    LH - Lower High
    LL - Lower Low

The first confirmed high and low establish the reference.
They are NOT classified as HH or HL.

This module does not generate trades.
"""

from __future__ import annotations

import pandas as pd

from .models import H1Structure, MarketStructure, SwingPoint, SwingType


class H1StructureEngine:
    """
    Analyse H1 price structure.

    A swing high/low is confirmed using neighbouring candles.
    No moving averages are used.
    """

    def analyse(self, data: pd.DataFrame) -> H1Structure:
        if data is None or data.empty:
            return H1Structure(
                direction=MarketStructure.UNKNOWN,
                explanation="No H1 market data available.",
            )

        required = {"High", "Low"}

        missing = required.difference(data.columns)

        if missing:
            raise ValueError(
                f"Missing required H1 columns: {sorted(missing)}"
            )

        frame = data.reset_index(drop=False).copy()

        swing_highs = self._find_swing_highs(frame)
        swing_lows = self._find_swing_lows(frame)

        classified = self._classify_swings(
            frame,
            swing_highs,
            swing_lows,
        )

        direction = self._classify_structure(classified)

        latest = classified[-1] if classified else None

        return H1Structure(
            direction=direction,
            latest_swing=latest,
            swing_points=classified,
            higher_highs=[
                swing
                for swing in classified
                if swing.swing_type == SwingType.HIGHER_HIGH
            ],
            higher_lows=[
                swing
                for swing in classified
                if swing.swing_type == SwingType.HIGHER_LOW
            ],
            lower_highs=[
                swing
                for swing in classified
                if swing.swing_type == SwingType.LOWER_HIGH
            ],
            lower_lows=[
                swing
                for swing in classified
                if swing.swing_type == SwingType.LOWER_LOW
            ],
            explanation=self._explanation(direction),
        )

    def _find_swing_highs(self, frame: pd.DataFrame) -> list[int]:
        indices: list[int] = []

        for index in range(1, len(frame) - 1):
            previous_high = float(frame.iloc[index - 1]["High"])
            current_high = float(frame.iloc[index]["High"])
            next_high = float(frame.iloc[index + 1]["High"])

            if current_high > previous_high and current_high > next_high:
                indices.append(index)

        return indices

    def _find_swing_lows(self, frame: pd.DataFrame) -> list[int]:
        indices: list[int] = []

        for index in range(1, len(frame) - 1):
            previous_low = float(frame.iloc[index - 1]["Low"])
            current_low = float(frame.iloc[index]["Low"])
            next_low = float(frame.iloc[index + 1]["Low"])

            if current_low < previous_low and current_low < next_low:
                indices.append(index)

        return indices

    def _classify_swings(
        self,
        frame: pd.DataFrame,
        swing_high_indices: list[int],
        swing_low_indices: list[int],
    ) -> list[SwingPoint]:
        """
        Classify each confirmed swing against the previous
        swing of the same type.

        The first high and first low are reference points only.
        They are not classified as HH/HL/LH/LL.
        """

        points: list[SwingPoint] = []

        previous_high: float | None = None
        previous_low: float | None = None

        high_indices = set(swing_high_indices)
        low_indices = set(swing_low_indices)

        for index in sorted(high_indices | low_indices):

            timestamp = frame.iloc[index][frame.columns[0]]

            # -------------------------------------------------
            # HIGH
            # -------------------------------------------------

            if index in high_indices:
                price = float(frame.iloc[index]["High"])

                if previous_high is not None:
                    if price > previous_high:
                        swing_type = SwingType.HIGHER_HIGH
                    else:
                        swing_type = SwingType.LOWER_HIGH

                    points.append(
                        SwingPoint(
                            timestamp=timestamp,
                            price=price,
                            swing_type=swing_type,
                            index=index,
                        )
                    )

                previous_high = price

            # -------------------------------------------------
            # LOW
            # -------------------------------------------------

            if index in low_indices:
                price = float(frame.iloc[index]["Low"])

                if previous_low is not None:
                    if price > previous_low:
                        swing_type = SwingType.HIGHER_LOW
                    else:
                        swing_type = SwingType.LOWER_LOW

                    points.append(
                        SwingPoint(
                            timestamp=timestamp,
                            price=price,
                            swing_type=swing_type,
                            index=index,
                        )
                    )

                previous_low = price

        return sorted(
            points,
            key=lambda point: (
                point.index if point.index is not None else -1
            ),
        )

    def _classify_structure(
        self,
        swings: list[SwingPoint],
    ) -> MarketStructure:
        """
        Determine the current H1 structure.

        A bullish structure requires HH + HL.

        A bearish structure requires LH + LL.

        If both types of structure are present in the
        current data, the result is consolidation.
        """

        higher_highs = [
            swing
            for swing in swings
            if swing.swing_type == SwingType.HIGHER_HIGH
        ]

        higher_lows = [
            swing
            for swing in swings
            if swing.swing_type == SwingType.HIGHER_LOW
        ]

        lower_highs = [
            swing
            for swing in swings
            if swing.swing_type == SwingType.LOWER_HIGH
        ]

        lower_lows = [
            swing
            for swing in swings
            if swing.swing_type == SwingType.LOWER_LOW
        ]

        bullish = bool(higher_highs and higher_lows)
        bearish = bool(lower_highs and lower_lows)

        if bullish and not bearish:
            return MarketStructure.BULLISH

        if bearish and not bullish:
            return MarketStructure.BEARISH

        if bullish and bearish:
            return MarketStructure.CONSOLIDATION

        return MarketStructure.UNKNOWN

    @staticmethod
    def _explanation(direction: MarketStructure) -> str:
        if direction == MarketStructure.BULLISH:
            return "H1 structure contains higher highs and higher lows."

        if direction == MarketStructure.BEARISH:
            return "H1 structure contains lower highs and lower lows."

        if direction == MarketStructure.CONSOLIDATION:
            return "H1 structure contains mixed bullish and bearish swings."

        return "Insufficient confirmed H1 structure."