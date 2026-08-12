"""
TradePilotAI Theme
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """
    Central theme configuration.
    """

    VERSION = "2.0"

    # --------------------------------------------------
    # Brand
    # --------------------------------------------------

    APP_NAME = "TradePilotAI"

    # --------------------------------------------------
    # Colours
    # --------------------------------------------------

    BACKGROUND = "#F5F7FA"

    SURFACE = "#FFFFFF"

    HEADER = "#17202A"

    BORDER = "#E5E7EB"

    PRIMARY = "#2563EB"

    SUCCESS = "#16A34A"

    WARNING = "#F59E0B"

    DANGER = "#DC2626"

    TEXT = "#111827"

    MUTED = "#6B7280"

    # --------------------------------------------------
    # Card Settings
    # --------------------------------------------------

    CARD_RADIUS = "14px"

    CARD_PADDING = "14px 16px"

    CARD_SHADOW = "0 2px 10px rgba(15,23,42,.04)"

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    PAGE_WIDTH = "96%"

    KPI_HEIGHT = "112px"

    PANEL_PADDING = "14px 16px"

    GAP = "16px"

    # --------------------------------------------------
    # Fonts
    # --------------------------------------------------

    TITLE_SIZE = "28px"

    PAGE_TITLE_SIZE = "34px"

    PANEL_TITLE = "16px"

    SECTION_TITLE_SIZE = "16px"

    KPI_TITLE = "12px"

    KPI_LABEL = "14px"

    KPI_VALUE = "30px"

    KPI_SUPPORTING = "12px"

    BODY = "13px"

    TABLE_HEADER = "13px"

    TABLE_BODY = "14px"

    FONT = (
        "-apple-system,"
        "BlinkMacSystemFont,"
        "'Segoe UI',"
        "Roboto,"
        "'Helvetica Neue',"
        "Arial,"
        "sans-serif"
    )

    FONT_DISPLAY = (
        "-apple-system,"
        "BlinkMacSystemFont,"
        "'Segoe UI',"
        "Roboto,"
        "'Helvetica Neue',"
        "Arial,"
        "sans-serif"
    )

    # --------------------------------------------------
    # Status Colours
    # --------------------------------------------------

    STATUS = {
        "online": {
            "background": "#DCFCE7",
            "text": "#166534",
        },
        "warning": {
            "background": "#FEF3C7",
            "text": "#92400E",
        },
        "offline": {
            "background": "#FEE2E2",
            "text": "#991B1B",
        },
        "info": {
            "background": "#DBEAFE",
            "text": "#1E3A8A",
        },
    }

    SEMANTIC = {
        "execute": "#16A34A",
        "watch": "#F59E0B",
        "reject": "#DC2626",
        "insufficient_data": "#6B7280",
        "bullish": "#16A34A",
        "bearish": "#DC2626",
        "neutral": "#6B7280",
        "low": "#16A34A",
        "medium": "#F59E0B",
        "high": "#DC2626",
    }

    BUTTON = {
        "primary": "#2563EB",
        "success": "#16A34A",
        "danger": "#DC2626",
        "secondary": "#6B7280",
    }

    TABLE = {
        "header_background": "#E9EEF5",
        "row_alt_background": "#F8FAFC",
        "row_hover_background": "#EEF4FF",
        "row_selected_background": "#DBEAFE",
        "border": "#D7DFEA",
    }