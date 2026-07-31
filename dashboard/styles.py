"""
TradePilotAI Professional Dashboard Styles
"""

from dashboard.theme import Theme
import streamlit as st


def apply_theme():
    st.markdown(
        f"""
<style>

/* ==========================================================
   GLOBAL
========================================================== */

html, body, [class*="css"] {{
    font-family:{Theme.FONT};
}}

.stApp {{
    background:{Theme.BACKGROUND};
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
    color:{Theme.TEXT};
    font-weight:700;
}}

p,label,span {{
    color:{Theme.TEXT};
}}

/* ==========================================================
   CARDS
========================================================== */

.tp-card {{

    background:{Theme.SURFACE};

    border:1px solid {Theme.BORDER};

    border-radius:{Theme.CARD_RADIUS};

    padding:{Theme.CARD_PADDING};

    box-shadow:{Theme.CARD_SHADOW};

}}

.tp-card:hover {{

    box-shadow:0 6px 18px rgba(0,0,0,.10);

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

    background:{Theme.SURFACE};

    border:1px solid {Theme.BORDER};

    border-radius:{Theme.CARD_RADIUS};

    padding:{Theme.PANEL_PADDING};

    margin-bottom:18px;

    box-shadow:{Theme.CARD_SHADOW};

}}

.tp-panel-title {{

    font-size:{Theme.PANEL_TITLE};

    font-weight:700;

    color:{Theme.TEXT};

    border-bottom:1px solid {Theme.BORDER};

    padding-bottom:10px;

    margin-bottom:18px;

}}

/* ==========================================================
   METRICS
========================================================== */

[data-testid="metric-container"] {{

    background:white;

    border:1px solid {Theme.BORDER};

    border-radius:12px;

    padding:12px;

    box-shadow:{Theme.CARD_SHADOW};

}}

[data-testid="metric-container"] label {{

    font-size:13px;

    color:{Theme.MUTED};

}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{

    font-size:28px;

    font-weight:700;

}}

/* ==========================================================
   BUTTONS
========================================================== */

.stButton>button {{

    width:100%;

    height:42px;

    border-radius:10px;

    border:none;

    background:{Theme.PRIMARY};

    color:white;

    font-weight:600;

}}

.stButton>button:hover {{

    background:#1D4ED8;

}}

/* ==========================================================
   TABLES
========================================================== */

table {{

    border-collapse:collapse;

    width:100%;

}}

thead tr {{

    background:#F8FAFC;

}}

th {{

    padding:12px;

    text-align:left;

    font-weight:700;

}}

td {{

    padding:12px;

    border-top:1px solid #EEF2F7;

}}

/* ==========================================================
   DATAFRAMES
========================================================== */

[data-testid="stDataFrame"] {{

    border-radius:12px;

    border:1px solid {Theme.BORDER};

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

    color:{Theme.PRIMARY};

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

    border-top:1px solid {Theme.BORDER};

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

</style>
""",
        unsafe_allow_html=True,
    )