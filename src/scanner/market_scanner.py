"""
===========================================================
FTSE Quant Trader V2
Market Scanner
===========================================================
"""


class MarketScanner:
    """
    Returns a list of stocks to scan.
    """

    def __init__(self):

        print("Market Scanner Initialised")

    def get_watchlist(self):

        return [

            "RR.L",
            "LLOY.L",
            "TSCO.L",
            "MKS.L",
            "BARC.L",
            "BP.L",
            "SHEL.L",
            "VOD.L",
            "AZN.L",
            "NG.L"

        ]