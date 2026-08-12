"""
TradePilotAI Layout Helpers
"""

from __future__ import annotations

from contextlib import contextmanager
from html import escape
import re
from typing import Callable
from typing import Any

import streamlit as st

from dashboard.theme import Theme


DECISION_COLOUR_MAPPING: dict[str, str] = {
    "EXECUTE": "#16A34A",
    "WATCH": "#F59E0B",
    "REJECT": "#DC2626",
    "INSUFFICIENT_DATA": "#6B7280",
}


SCORE_COLOUR_MAPPING: dict[str, str] = {
    "Excellent": "#16A34A",
    "Strong": "#2563EB",
    "Moderate": "#F59E0B",
    "Weak": "#EA580C",
    "Poor": "#DC2626",
}


# ----------------------------------------------------------
# Spacing
# ----------------------------------------------------------

def spacer(lines: int = 1) -> None:
    """Insert vertical spacing."""
    for _ in range(lines):
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def apply_desktop_layout() -> None:
    """Apply the shared desktop geometry used by dashboard workspaces."""
    st.markdown(
        """
        <style>
        [data-testid="stMainBlockContainer"] {
            max-width: 1600px;
            min-width: 1400px;
            padding-left: 24px;
            padding-right: 24px;
            padding-top: 20px;
            padding-bottom: 20px;
            margin-left: auto;
            margin-right: auto;
        }
        @media (max-width: 1450px) {
            [data-testid="stMainBlockContainer"] {
                min-width: auto;
                width: 100%;
            }
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 20px !important;
            align-items: stretch !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_desktop_layout() -> None:
    """Alias for shared desktop geometry helper."""
    apply_desktop_layout()


# ----------------------------------------------------------
# Section Title
# ----------------------------------------------------------

def section(title: str, status: str | None = None) -> None:
    """Render a standardized panel header shared by all dashboard panels."""
    status_html = f"<span class='tp-panel-title__status'>{escape(str(status))}</span>" if status else ""
    st.markdown(
        f"""
        <div class="tp-panel-title">
            <span>{escape(str(title))}</span>
            {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_header(title: str, status: str | None = None) -> None:
    """Alias for standardized dashboard panel headers."""
    section(title, status=status)


def render_section(title: str, renderer: Callable[[], None], status: str | None = None) -> None:
    """Render a panel section with shared header and shared card container."""
    with st.container():
        render_panel_header(title, status=status)
        with card():
            renderer()


def render_information_banner(title: str, message: str, status: str | None = None) -> None:
    """Render informational content using shared section and card styling."""

    def _content() -> None:
        for line in str(message or "").splitlines() or [""]:
            st.write(line)

    render_section(title, _content, status=status)


# ----------------------------------------------------------
# Card Container
# ----------------------------------------------------------

@contextmanager
def card():
    """
    Creates a bordered card.

    Usage

        with card():
            st.write(...)
    """

    st.markdown(
        """
        <div class="tp-card">
        """,
        unsafe_allow_html=True,
    )

    yield

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------
# Status Badge
# ----------------------------------------------------------

def badge(
    text: str,
    colour: str = "info",
):
    colours = {
        "success": ("#DCFCE7", "#166534"),
        "danger": ("#FEE2E2", "#991B1B"),
        "warning": ("#FEF3C7", "#92400E"),
        "info": ("#DBEAFE", "#1E3A8A"),
        "neutral": ("#F3F4F6", "#4B5563"),
    }

    bg, fg = colours.get(colour, colours["info"])

    st.markdown(
        f"""
        <span style="
            background:{bg};
            color:{fg};
            padding:5px 12px;
            border-radius:999px;
            font-size:13px;
            font-weight:600;">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_decision_badge(decision: str | None) -> None:
    """Render a semantic badge for the decision engine recommendation."""
    normalized = str(decision or "INSUFFICIENT_DATA").strip().upper().replace(" ", "_")

    badge_colour = {
        "EXECUTE": "success",
        "WATCH": "warning",
        "REJECT": "danger",
        "INSUFFICIENT_DATA": "neutral",
    }.get(normalized, "neutral")

    label = "INSUFFICIENT DATA" if normalized == "INSUFFICIENT_DATA" else normalized
    badge(label, colour=badge_colour)


def score_rating(score: float | int | None) -> str:
    """Return a semantic score rating from the shared TradePilotAI bands."""
    try:
        numeric = float(score)
    except (TypeError, ValueError):
        numeric = 0.0

    if numeric >= 90.0:
        return "Excellent"
    if numeric >= 75.0:
        return "Strong"
    if numeric >= 60.0:
        return "Moderate"
    if numeric >= 40.0:
        return "Weak"
    return "Poor"


def quality_badge(score: float | int | None) -> str:
    """Return the shared five-level quality badge label from score bands."""
    rating = score_rating(score)
    return {
        "Excellent": "★★★★★ Excellent",
        "Strong": "★★★★☆ Strong",
        "Moderate": "★★★☆☆ Moderate",
        "Weak": "★★☆☆☆ Weak",
        "Poor": "★☆☆☆☆ Poor",
    }[rating]


# ----------------------------------------------------------
# KPI Card
# ----------------------------------------------------------

def kpi(
    title: str,
    value: str,
    delta: str | None = None,
):
    with card():

        st.caption(title)

        st.markdown(
            f"""
            <div style="
                font-size:28px;
                font-weight:700;
                color:#111827;">
                {value}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if delta:
            st.caption(delta)


def render_kpi_card(
    title: str,
    value: str,
    footer_label: str,
    footer_value: str,
    footer_secondary_label: str | None = None,
    footer_secondary_value: str | None = None,
    show_footer: bool = True,
    card_class: str = "",
) -> None:
    """Render one standardized KPI card used by the Market Review dashboard."""
    secondary_label = footer_secondary_label or ""
    secondary_value = footer_secondary_value or ""
    supporting_lines: list[str] = []
    if show_footer:
        if footer_label or footer_value:
            primary_text = ": ".join(part for part in [footer_label, footer_value] if str(part).strip())
            supporting_lines.append(primary_text or "Not available")
        if footer_secondary_label or footer_secondary_value:
            secondary_text = ": ".join(part for part in [secondary_label, secondary_value] if str(part).strip())
            supporting_lines.append(secondary_text or "Not available")

    supporting_html = ""
    if supporting_lines:
        supporting_html = "<div class='tp-kpi-supporting'>" + "".join(
            f"<div class='tp-kpi-supporting-line'>{escape(line)}</div>" for line in supporting_lines
        ) + "</div>"

    class_suffix = f" {card_class.strip()}" if str(card_class).strip() else ""

    st.markdown(
        f"""
        <div class="tp-kpi-card{class_suffix}">
            <div class="tp-kpi-title">{escape(title)}</div>
            <div class="tp-kpi-value">{escape(value)}</div>
            {supporting_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------
# Empty State
# ----------------------------------------------------------

def empty_state(message: str = "No data available") -> None:
    st.markdown(
        f"""
        <div class="tp-empty-state">{message}</div>
        """,
        unsafe_allow_html=True,
    )


def empty_panel(message: str = "No data available") -> None:
    empty_state(message)


def render_table(rows: list[dict[str, Any]], columns: list[str], numeric_columns: list[str] | None = None) -> None:
    """Render dashboard tables using one shared implementation and style."""
    numeric = set(numeric_columns or [])
    safe_rows = rows or []

    decision_column_hints = (
        "decision",
        "recommendation",
        "action",
    )
    decision_values = {
        "EXECUTE",
        "WATCH",
        "REJECT",
        "INSUFFICIENT_DATA",
    }

    numeric_header_hints = (
        "score",
        "price",
        "value",
        "amount",
        "allocation",
        "exposure",
        "confidence",
        "risk",
        "p/l",
        "%",
        "qty",
        "quantity",
        "size",
        "entry",
        "current",
        "target",
        "stop",
    )

    numeric_value_pattern = re.compile(r"^\s*[\$\-+]?\d[\d,]*(?:\.\d+)?%?\s*$")

    def _is_numeric_cell(column: str, value: Any) -> bool:
        if column in numeric:
            return True

        column_name = str(column or "").strip().lower()
        if any(hint in column_name for hint in numeric_header_hints):
            return True

        text = str(value or "").strip()
        if not text:
            return False
        return bool(numeric_value_pattern.match(text))

    def _decision_value(value: Any) -> str:
        return str(value or "").strip().upper().replace(" ", "_")

    def _is_decision_cell(column: str, value: Any) -> bool:
        column_name = str(column or "").strip().lower()
        normalized = _decision_value(value)
        return any(hint in column_name for hint in decision_column_hints) and bool(normalized)

    def _header_class(column: str) -> str:
        column_name = str(column or "").strip().lower()
        if any(hint in column_name for hint in decision_column_hints):
            return "tp-center"
        if column in numeric or any(hint in column_name for hint in numeric_header_hints):
            return "tp-num"
        return "tp-text"

    header_html = "".join(
        (
            f"<th class='{_header_class(col)}'>"
            f"<div class='tp-cell-heading'>{escape(str(col))}</div>"
            "</th>"
        )
        for col in columns
    )

    body_html = ""
    for row in safe_rows:
        row_class = "tp-selected" if isinstance(row, dict) and any(bool(row.get(key)) for key in ("selected", "is_selected", "_selected", "highlight", "highlighted")) else ""
        cells = []
        for col in columns:
            value = row.get(col, "") if isinstance(row, dict) else ""
            is_decision = _is_decision_cell(col, value)
            cell_class = "tp-center" if is_decision else ("tp-num" if _is_numeric_cell(col, value) else "tp-text")
            content_class = "tp-cell-content tp-decision-badge" if is_decision else "tp-cell-content"
            semantic = _decision_value(value).lower()
            if _decision_value(value) not in decision_values:
                semantic = "neutral"
            cells.append(
                f"<td class='{cell_class}' title='{escape(str(value))}'>"
                f"<div class='{content_class}' data-decision='{escape(semantic)}'>{escape(str(value))}</div>"
                "</td>"
            )
        body_html += f"<tr class='{row_class}'>{''.join(cells)}</tr>"

    if not body_html:
        body_html = f"<tr><td colspan='{max(len(columns), 1)}'></td></tr>"

    table_html = f"""
<table class="tp-shared-table">
    <thead>
        <tr>{header_html}</tr>
    </thead>
    <tbody>
        {body_html}
    </tbody>
</table>
"""

    st.markdown(table_html, unsafe_allow_html=True)