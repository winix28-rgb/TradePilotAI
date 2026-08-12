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

    PANEL_TITLE = "16px"

    KPI_TITLE = "12px"

    KPI_VALUE = "24px"

    BODY = "13px"

    FONT = (
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