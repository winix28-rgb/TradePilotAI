"""
TradePilotAI Professional Dashboard Styles
"""

from dashboard.theme import Theme
import streamlit as st


def apply_theme():
    st.markdown(
        f"""
<style>

:root {{
    --tp-background: {Theme.BACKGROUND};
    --tp-surface: {Theme.SURFACE};
    --tp-border: {Theme.BORDER};
    --tp-text: {Theme.TEXT};
    --tp-muted: {Theme.MUTED};
    --tp-primary: {Theme.PRIMARY};
    --tp-success: {Theme.SUCCESS};
    --tp-warning: {Theme.WARNING};
    --tp-danger: {Theme.DANGER};
    --tp-secondary: {Theme.MUTED};
    --tp-table-header: {Theme.TABLE['header_background']};
    --tp-table-alt: {Theme.TABLE['row_alt_background']};
    --tp-table-hover: {Theme.TABLE['row_hover_background']};
    --tp-table-selected: {Theme.TABLE['row_selected_background']};
}}

/* ==========================================================
   GLOBAL
========================================================== */

html, body, [class*="css"] {{
    font-family:{Theme.FONT_DISPLAY};
    color:var(--tp-text);
}}

.stApp {{
    background:var(--tp-background);
}}

.main .block-container {{
    max-width:{Theme.PAGE_WIDTH};
    padding-top:1rem;
    padding-bottom:1rem;
}}

/* Hide Streamlit Chrome */

header {{
    visibility:hidden;
}}

footer {{
    visibility:hidden;
}}

#MainMenu {{
    visibility:hidden;
}}

div[data-testid="stToolbar"] {{
    display:none;
}}

/* ==========================================================
   HEADINGS
========================================================== */

h1,h2,h3,h4 {{
    color:var(--tp-text);
    font-weight:800;
    letter-spacing:-0.02em;
}}

p,label,span {{
    color:var(--tp-text);
}}

.tp-page-title {{
    margin:0 0 8px 0;
    font-size:{Theme.PAGE_TITLE_SIZE};
    line-height:1.1;
    font-weight:800;
    letter-spacing:-0.04em;
    color:var(--tp-text);
}}

.tp-panel-title {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    min-height:48px;
    padding:12px 16px;
    border-bottom:1px solid var(--tp-border);
    color:var(--tp-text);
    font-size:{Theme.SECTION_TITLE_SIZE};
    font-weight:700;
    letter-spacing:-0.01em;
    background:linear-gradient(180deg, rgba(255,255,255,0.72), rgba(255,255,255,0.94));
}}

.tp-panel-title__status {{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:4px 10px;
    border-radius:999px;
    background:#F3F4F6;
    color:var(--tp-muted);
    font-size:12px;
    font-weight:700;
    white-space:nowrap;
}}

/* ==========================================================
   CARDS
========================================================== */

.tp-card {{
    background:var(--tp-surface);
    border:1px solid var(--tp-border);
    border-radius:{Theme.CARD_RADIUS};
    padding:{Theme.CARD_PADDING};
    box-shadow:{Theme.CARD_SHADOW};
    transition:box-shadow 160ms ease, transform 160ms ease;
}}

.tp-card:hover {{
    box-shadow:0 10px 24px rgba(15,23,42,.10);
    transform:translateY(-1px);
}}

.tp-pill {{

    display:inline-block;

    padding:6px 12px;

    border-radius:999px;

    background:{Theme.PRIMARY};

    color:white;

    font-weight:600;

}}

/* ==========================================================
   PANELS
========================================================== */

.tp-panel {{
    background:var(--tp-surface);
    border:1px solid var(--tp-border);
    border-radius:{Theme.CARD_RADIUS};
    padding:{Theme.PANEL_PADDING};
    margin-bottom:18px;
    box-shadow:{Theme.CARD_SHADOW};
}}

.tp-panel-title {{
    font-size:{Theme.PANEL_TITLE};
}}

.tp-kpi-card {{
    min-height:160px;
    box-sizing:border-box;
    border:1px solid var(--tp-border);
    border-radius:14px;
    padding:14px 16px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    gap:12px;
    background:linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98));
    box-shadow:{Theme.CARD_SHADOW};
}}

.tp-kpi-card .tp-kpi-title {{
    font-size:{Theme.KPI_LABEL};
    line-height:1.2;
    font-weight:700;
    color:var(--tp-muted);
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}}

.tp-kpi-card .tp-kpi-value {{
    font-size:{Theme.KPI_VALUE};
    line-height:1.05;
    font-weight:800;
    color:var(--tp-text);
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}}

.tp-kpi-card .tp-kpi-supporting {{
    display:flex;
    flex-direction:column;
    gap:4px;
    font-size:{Theme.KPI_SUPPORTING};
    line-height:1.35;
    color:var(--tp-muted);
}}

.tp-kpi-card .tp-kpi-supporting-line {{
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}}

/* ==========================================================
   METRICS
========================================================== */

[data-testid="metric-container"] {{
    background:var(--tp-surface);
    border:1px solid var(--tp-border);
    border-radius:12px;
    padding:12px;
    box-shadow:{Theme.CARD_SHADOW};
}}

[data-testid="metric-container"] label {{
    font-size:13px;
    color:var(--tp-muted);

}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-size:28px;
    font-weight:800;

}}

/* ==========================================================
   BUTTONS
========================================================== */

.stButton>button {{
    width:100%;
    border-radius:10px;
    border:none;
    min-height:42px;
    background:var(--tp-primary);
    color:white;
    font-weight:700;
    box-shadow:0 1px 2px rgba(15,23,42,.08);
    transition:transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}}

.stButton>button:hover {{
    background:#1D4ED8;
    transform:translateY(-1px);
    box-shadow:0 6px 14px rgba(37,99,235,.18);
}}

.stButton>button[kind="secondary"] {{
    background:#E5E7EB;
    color:#374151;
}}

.stButton>button[kind="secondary"]:hover {{
    background:#D1D5DB;
    color:#111827;
}}

.stButton>button[kind="primary"] {{
    background:var(--tp-primary);
}}

.stButton>button[kind="primary"]:hover {{
    background:#1D4ED8;
}}

.tp-button-success {{
    background:var(--tp-success) !important;
    color:white !important;
}}

.tp-button-danger {{
    background:var(--tp-danger) !important;
    color:white !important;
}}

.tp-button-secondary {{
    background:#E5E7EB !important;
    color:#374151 !important;
}}

/* ==========================================================
   TABLES
========================================================== */

table {{
    border-collapse:collapse;
    width:100%;
    width:100%;
    background:var(--tp-surface);
}}

thead tr {{
    background:var(--tp-table-header);
}}

th {{
    padding:10px 12px;
    text-align:left;
    font-weight:700;
    color:var(--tp-text);
}}

td {{
    padding:10px 12px;
    border-top:1px solid var(--tp-border);
}}

tbody tr:nth-child(even) td {{
    background:var(--tp-table-alt);
}}

tbody tr:hover td {{
    background:var(--tp-table-hover);
}}

tbody tr.tp-selected td {{
    background:var(--tp-table-selected);
}}

.tp-shared-table {{
    width:100%;
    border:1px solid var(--tp-border);
    border-radius:12px;
    overflow:hidden;
    border-spacing:0;
    table-layout:fixed;
}}

.tp-shared-table thead th {{
    background:var(--tp-table-header);
    font-size:{Theme.TABLE_HEADER};
    font-weight:800;
    height:46px;
    vertical-align:middle;
    padding:10px 14px;
    border-bottom:1px solid var(--tp-border);
    white-space:nowrap;
    line-height:1.2;
}}

.tp-shared-table tbody td {{
    font-size:{Theme.TABLE_BODY};
    height:44px;
    vertical-align:middle;
    padding:10px 14px;
    border-top:1px solid rgba(215,223,234,.65);
    transition:background-color 140ms ease;
    overflow:hidden;
    line-height:1.25;
}}

.tp-shared-table .tp-num {{
    text-align:right;
    font-variant-numeric: tabular-nums;
}}

.tp-shared-table .tp-text {{
    text-align:left;
}}

.tp-shared-table .tp-center {{
    text-align:center;
}}

.tp-shared-table .tp-cell-heading {{
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    line-height:1.2;
}}

.tp-shared-table .tp-cell-content {{
    display:block;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
    line-height:1.35;
    width:100%;
}}

.tp-shared-table .tp-decision-badge {{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-width:120px;
    max-width:100%;
    padding:5px 10px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
    letter-spacing:0.02em;
    text-transform:uppercase;
}}

.tp-shared-table .tp-decision-badge[data-decision="execute"] {{
    background:#DCFCE7;
    color:#166534;
}}

.tp-shared-table .tp-decision-badge[data-decision="watch"] {{
    background:#FEF3C7;
    color:#92400E;
}}

.tp-shared-table .tp-decision-badge[data-decision="reject"] {{
    background:#FEE2E2;
    color:#991B1B;
}}

.tp-shared-table .tp-decision-badge[data-decision="insufficient_data"] {{
    background:#F3F4F6;
    color:#4B5563;
}}

.tp-shared-table .tp-decision-badge[data-decision="neutral"] {{
    background:#F3F4F6;
    color:#4B5563;
}}

.tp-shared-table tbody tr:hover:not(.tp-selected) td {{
    background:var(--tp-table-hover);
}}

.tp-shared-table tbody tr.tp-selected td,
.tp-shared-table tr.tp-selected td {{
    background:var(--tp-table-selected) !important;
}}

.tp-shared-table tbody tr:nth-child(even):not(.tp-selected) td {{
    background:var(--tp-table-alt);
}}

@media (max-width: 1200px) {{
    .tp-shared-table thead th,
    .tp-shared-table tbody td {{
        padding:9px 12px;
    }}
}}

.tp-empty-state {{
    padding:16px;
    border:1px dashed var(--tp-border);
    border-radius:12px;
    color:var(--tp-muted);
    background:rgba(255,255,255,.7);
}}

/* ==========================================================
   DATAFRAMES
========================================================== */

[data-testid="stDataFrame"] {{
    border-radius:12px;
    border:1px solid var(--tp-border);
    overflow:hidden;
}}

/* ==========================================================
   INPUTS
========================================================== */

.stSelectbox > div > div {{
    border-radius:10px;
}}

.stTextInput input {{

    border-radius:10px;

}}

.stNumberInput input {{

    border-radius:10px;

}}

/* ==========================================================
   SIDEBAR
========================================================== */

[data-testid="stSidebar"] {{
    background:#17202A;
}}

[data-testid="stSidebar"] * {{
    color:white;
}}

/* ==========================================================
   TABS
========================================================== */

button[data-baseweb="tab"] {{
    font-weight:600;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color:var(--tp-primary);
}}

/* ==========================================================
   EXPANDERS
========================================================== */

.streamlit-expanderHeader {{

    font-weight:600;

}}

/* ==========================================================
   DIVIDERS
========================================================== */

hr {{
    border:none;
    border-top:1px solid var(--tp-border);
}}

/* ==========================================================
   SCROLLBARS
========================================================== */

::-webkit-scrollbar {{
    width:10px;
}}

::-webkit-scrollbar-thumb {{
    background:#C7CDD4;
    border-radius:20px;
}}

::-webkit-scrollbar-track {{
    background:#EEF2F7;
}}

.tp-scanner-selected-banner {{
    background:#EFF6FF;
    border:1px solid #BFDBFE;
    border-radius:8px;
    padding:6px 10px;
    margin-bottom:8px;
    font-weight:700;
    color:#1D4ED8;
}}

</style>
""",
        unsafe_allow_html=True,
    )