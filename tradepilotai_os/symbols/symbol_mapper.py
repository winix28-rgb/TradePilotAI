"""
===========================================================
TradePilotAI OS
Universal Symbol Mapper
===========================================================

Maintains a single internal symbol and converts it for
different market data and broker providers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:

    symbol: str
    yahoo: str
    tradingview: str
    ig: str


class SymbolMapper:

    def __init__(self):

        self._symbols = {

            "RR": Instrument(
                symbol="RR",
                yahoo="RR.L",
                tradingview="LSE:RR",
                ig="IX.D.RR.DAILY.IP",
            ),

            "TSCO": Instrument(
                symbol="TSCO",
                yahoo="TSCO.L",
                tradingview="LSE:TSCO",
                ig="IX.D.TSCO.DAILY.IP",
            ),

            "LLOY": Instrument(
                symbol="LLOY",
                yahoo="LLOY.L",
                tradingview="LSE:LLOY",
                ig="IX.D.LLOY.DAILY.IP",
            ),

            "BARC": Instrument(
                symbol="BARC",
                yahoo="BARC.L",
                tradingview="LSE:BARC",
                ig="IX.D.BARC.DAILY.IP",
            ),

            "MKS": Instrument(
                symbol="MKS",
                yahoo="MKS.L",
                tradingview="LSE:MKS",
                ig="IX.D.MKS.DAILY.IP",
            ),

            "BP": Instrument(
                symbol="BP",
                yahoo="BP.L",
                tradingview="LSE:BP",
                ig="IX.D.BP.DAILY.IP",
            ),

            "SHEL": Instrument(
                symbol="SHEL",
                yahoo="SHEL.L",
                tradingview="LSE:SHEL",
                ig="IX.D.SHEL.DAILY.IP",
            ),

            "AZN": Instrument(
                symbol="AZN",
                yahoo="AZN.L",
                tradingview="LSE:AZN",
                ig="IX.D.AZN.DAILY.IP",
            ),

            "NG": Instrument(
                symbol="NG",
                yahoo="NG.L",
                tradingview="LSE:NG",
                ig="IX.D.NG.DAILY.IP",
            ),

            "VOD": Instrument(
                symbol="VOD",
                yahoo="VOD.L",
                tradingview="LSE:VOD",
                ig="IX.D.VOD.DAILY.IP",
            ),

        }

    def yahoo(self, symbol: str) -> str:
        return self._symbols[symbol.upper()].yahoo

    def ig(self, symbol: str) -> str:
        return self._symbols[symbol.upper()].ig

    def tradingview(self, symbol: str) -> str:
        return self._symbols[symbol.upper()].tradingview

    def instruments(self):
        return list(self._symbols.values())