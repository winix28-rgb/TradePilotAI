"""
TradePilotAI Layout Helpers
"""

from __future__ import annotations

from contextlib import contextmanager
from html import escape
from typing import Callable
from typing import Any

import streamlit as st


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
    status_html = f"<span>{status}</span>" if status else ""
    st.markdown(
        f"""
        <div class="tp-panel-title" style="box-sizing:border-box;height:48px;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--tp-border, #E5E7EB);">
            <span>{title}</span>
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
) -> None:
    """Render one standardized KPI card used by the Market Review dashboard."""
    secondary_label = footer_secondary_label or ""
    secondary_value = footer_secondary_value or ""
    footer_html = ""
    if show_footer:
        footer_html = (
            "<div class='tp-kpi-footer-grid'>"
            f"<div class='tp-kpi-footer-label'>{escape(footer_label)}</div>"
            f"<div class='tp-kpi-footer-label'>{escape(secondary_label)}</div>"
            "</div>"
            "<div class='tp-kpi-footer-grid'>"
            f"<div class='tp-kpi-footer-value'>{escape(footer_value)}</div>"
            f"<div class='tp-kpi-footer-value'>{escape(secondary_value)}</div>"
            "</div>"
        )

    st.markdown(
        f"""
        <style>
        .tp-kpi-card {{
            height:160px;
            box-sizing:border-box;
            border:1px solid #E5E7EB;
            border-radius:12px;
            padding:12px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
            gap:10px;
        }}
        .tp-kpi-card .tp-kpi-title {{
            font-size:14px;
            font-weight:600;
            color:#111827;
            line-height:18px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }}
        .tp-kpi-card .tp-kpi-value {{
            font-size:28px;
            font-weight:700;
            color:#111827;
            line-height:32px;
            text-align:center;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }}
        .tp-kpi-card .tp-kpi-footer-label,
        .tp-kpi-card .tp-kpi-footer-value {{
            font-size:12px;
            color:#6B7280;
            line-height:16px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }}
        .tp-kpi-card .tp-kpi-footer-grid {{
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:8px;
        }}
        </style>
        <div class="tp-kpi-card">
            <div class="tp-kpi-title">{escape(title)}</div>
            <div class="tp-kpi-value">{escape(value)}</div>
            <div>{footer_html}</div>
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

    style = """
    <style>
    .tp-shared-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }
    .tp-shared-table thead th {
        box-sizing: border-box;
        height: 39px;
        padding: 8px 12px;
        text-align: left;
        font-size: 14px;
        font-weight: 700;
        line-height: 23px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border-bottom: 1px solid #EEF2F7;
        vertical-align: middle;
    }
    .tp-shared-table tbody td {
        box-sizing: border-box;
        height: 35px;
        padding: 8px 12px;
        text-align: left;
        font-size: 14px;
        font-weight: 400;
        line-height: 19px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        border-bottom: 1px solid #EEF2F7;
        vertical-align: middle;
    }
    .tp-shared-table .tp-num {
        text-align: right;
    }
    </style>
    """

    header_html = "".join(
        f"<th class='{'tp-num' if col in numeric else ''}'>{escape(str(col))}</th>"
        for col in columns
    )

    body_html = ""
    for row in safe_rows:
        cells = []
        for col in columns:
            value = row.get(col, "") if isinstance(row, dict) else ""
            cells.append(f"<td class='{'tp-num' if col in numeric else ''}'>{escape(str(value))}</td>")
        body_html += f"<tr>{''.join(cells)}</tr>"

    if not body_html:
        body_html = f"<tr><td colspan='{max(len(columns), 1)}'></td></tr>"

    table_html = f"""
    {style}
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