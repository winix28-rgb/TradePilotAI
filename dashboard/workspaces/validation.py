"""Validation workspace renderer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from dashboard.layout import empty_state
from dashboard.layout import render_desktop_layout
from dashboard.layout import render_panel_header
from dashboard.layout import render_section
from dashboard.layout import render_table
from tradepilotai_os.validation import run_validation_suite


def render_validation_workspace(state: Any) -> None:
    """Render the read-only validation workspace."""

    render_desktop_layout()
    result = run_validation_suite()

    render_panel_header("VALIDATION WORKSPACE", status=result.overall_status)

    score_col, module_col, check_col, timestamp_col = st.columns([1, 1, 1, 2], gap="small")
    with score_col:
        st.metric("Overall Score", f"{result.overall_score:.1f}%")
    with module_col:
        st.metric("Modules Passed", f"{result.passed_modules}/{result.total_modules}")
    with check_col:
        st.metric("Checks Passed", f"{result.passed_checks}/{result.total_checks}")
    with timestamp_col:
        st.caption("Generated At")
        st.write(result.generated_at)

    render_section(
        "Suite Summary",
        lambda: _render_summary_table(result),
    )

    for module in result.modules:
        render_section(
            module.name,
            lambda module=module: _render_module_details(module),
            status=module.status,
        )


def _render_summary_table(result: Any) -> None:
    rows = [
        {
            "Module": module.name,
            "Status": module.status,
            "Score": f"{module.score:.1f}%",
            "Checks": f"{module.passed_checks}/{module.total_checks}",
            "Summary": module.summary,
        }
        for module in result.modules
    ]

    if not rows:
        empty_state("No validation modules executed")
        return

    render_table(rows=rows, columns=["Module", "Status", "Score", "Checks", "Summary"])


def _render_module_details(module: Any) -> None:
    st.caption(module.summary)
    rows = [
        {
            "Check": check.name,
            "Result": "PASS" if check.passed else "FAIL",
            "Expected": check.expected,
            "Actual": check.actual,
            "Details": check.details,
        }
        for check in module.checks
    ]

    if not rows:
        empty_state("No checks were executed for this module")
        return

    render_table(rows=rows, columns=["Check", "Result", "Expected", "Actual", "Details"])