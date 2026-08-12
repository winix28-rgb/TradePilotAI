"""Scanner service layer for the TradePilotAI OS scanner workspace."""

from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Any

import pandas as pd

from tradepilotai_os.indicators.indicator_engine import IndicatorEngine
from tradepilotai_os.market_data.yahoo_provider import YahooMarketDataProvider
from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.scanner.market_scanner import MarketScanner
from tradepilotai_os.strategy.strategy_engine import StrategyEngine

from .opportunity_scoring import OpportunityScoringEngine


class ScannerService:
    """Run the live scanner workflow using the existing market-data and strategy stack."""

    def __init__(
        self,
        market_scanner: MarketScanner | None = None,
        data_provider: YahooMarketDataProvider | None = None,
        indicator_engine: IndicatorEngine | None = None,
        strategy_engine: StrategyEngine | None = None,
        scoring_engine: OpportunityScoringEngine | None = None,
    ) -> None:
        self.market_scanner = market_scanner or MarketScanner()
        self.data_provider = data_provider or YahooMarketDataProvider()
        self.indicator_engine = indicator_engine or IndicatorEngine()
        self.strategy_engine = strategy_engine or StrategyEngine()
        self.scoring_engine = scoring_engine or OpportunityScoringEngine()
        self.last_scan_time = ""
        self.scan_duration = "0s"
        self.signals_found = 0
        self.buy_signals = 0
        self.sell_signals = 0
        self.watch_list_count = len(self.market_scanner.get_watchlist())
        self._scan_state = "ready"
        self._last_scan_result: dict[str, Any] | None = None
        self._last_watchlist: list[str] = []

    def scan(self, watchlist: list[str] | None = None) -> dict[str, Any]:
        self._scan_state = "running"
        symbols = list(watchlist or self.market_scanner.get_watchlist() or [])
        self._last_watchlist = symbols
        strategy = getattr(self.strategy_engine, "strategy", None)
        interval = str(getattr(strategy, "primary_timeframe", "")).strip() if strategy is not None else ""
        if not interval:
            interval = str(getattr(self.strategy_engine, "primary_timeframe", "")).strip()
        if not interval:
            raise ValueError("Scanner strategy must declare a primary timeframe.")

        started_at = time.monotonic()
        results: list[dict[str, Any]] = []
        buy_candidates: list[dict[str, Any]] = []
        sell_candidates: list[dict[str, Any]] = []
        watch_list_rows: list[dict[str, Any]] = []
        events: list[dict[str, Any]] = [{"name": "ScanStarted", "status": "Complete"}]

        for symbol in symbols:
            try:
                history = self.data_provider.history(symbol, period="6mo", interval=interval)
                if history is None or history.empty or len(history) < 30:
                    raise ValueError("Not enough market data")

                enriched = self.indicator_engine.add_indicators(history)
                volatility = self._volatility(enriched)
                signal = self.strategy_engine.evaluate(symbol, enriched)
            except Exception as exc:  # pragma: no cover - defensive guard
                events.append({"name": f"{symbol} Scan", "status": "Failed", "message": str(exc)})
                watch_list_rows.append({
                    "symbol": symbol,
                    "reason": "No actionable signal generated",
                    "last_signal": "WATCH",
                    "status": "Monitor",
                })
                continue

            if signal is None:
                watch_list_rows.append({
                    "symbol": symbol,
                    "reason": "No actionable signal generated",
                    "last_signal": "WATCH",
                    "status": "Monitor",
                })
                continue

            row = self._to_result_row(symbol=symbol, signal=signal, volatility=volatility)
            results.append(row)
            watch_list_rows.append({
                "symbol": symbol,
                "reason": " | ".join(signal.reasons) if signal.reasons else "Strategy signal generated",
                "last_signal": signal.signal,
                "status": "Watch",
            })

            if signal.signal == "BUY":
                buy_candidates.append({
                    "symbol": symbol,
                    "company": symbol,
                    "price": f"{signal.price:.2f}",
                    "rsi": round(signal.rsi, 1),
                    "ema_trend": "Bullish" if signal.ema12 >= signal.ema26 else "Bearish",
                    "signal": signal.signal,
                    "confidence": signal.confidence,
                    "risk_rating": self._risk_rating(signal.confidence, volatility),
                    "overall_score": row["overall_score"],
                    "score_breakdown": row["score_breakdown"],
                    "ranking_reason": row["ranking_reason"],
                })
            elif signal.signal == "SELL":
                sell_candidates.append({
                    "symbol": symbol,
                    "company": symbol,
                    "price": f"{signal.price:.2f}",
                    "rsi": round(signal.rsi, 1),
                    "ema_trend": "Bullish" if signal.ema12 >= signal.ema26 else "Bearish",
                    "signal": signal.signal,
                    "confidence": signal.confidence,
                    "risk_rating": self._risk_rating(signal.confidence, volatility),
                    "overall_score": row["overall_score"],
                    "score_breakdown": row["score_breakdown"],
                    "ranking_reason": row["ranking_reason"],
                })

            events.append({"name": f"{symbol} Scan", "status": "Complete", "message": signal.signal})

        results.sort(key=lambda item: item["confidence"], reverse=True)
        buy_candidates.sort(key=lambda item: item["confidence"], reverse=True)
        sell_candidates.sort(key=lambda item: item["confidence"], reverse=True)

        scan_duration = round(time.monotonic() - started_at, 2)
        self.scan_duration = f"{scan_duration:.2f}s"
        self.last_scan_time = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.signals_found = len(results)
        self.buy_signals = len(buy_candidates)
        self.sell_signals = len(sell_candidates)
        self.watch_list_count = len(symbols)
        self._scan_state = "ready"

        payload = {
            "summary": {
                "universe": f"{len(symbols)} symbols",
                "symbols_scanned": len(symbols),
                "scan_duration": self.scan_duration,
                "signals_found": self.signals_found,
                "buy_signals": self.buy_signals,
                "sell_signals": self.sell_signals,
                "watch_list_count": self.watch_list_count,
                "last_scan_time": self.last_scan_time,
                "timeframe": interval,
            },
            "pipeline": {
                "market_data": "Complete",
                "indicators": "Complete",
                "strategy": "Complete",
                "risk": "Complete",
                "complete": "Complete",
            },
            "buy_candidates": buy_candidates,
            "sell_candidates": sell_candidates,
            "watch_list": watch_list_rows,
            "signal_detail": self._signal_detail(results[0]) if results else {},
            "events": events + [{"name": "ScanCompleted", "status": "Complete"}],
            "results": results,
        }

        self._last_scan_result = payload
        return payload

    def _to_result_row(self, *, symbol: str, signal: TradeSignal, volatility: float | None = None) -> dict[str, Any]:
        signal_label = str(signal.signal or "HOLD").upper()
        trend = self._trend(signal)
        reason = " | ".join(signal.reasons) if signal.reasons else "Strategy signal generated"
        score = self.scoring_engine.evaluate(
            symbol=symbol,
            signal=signal_label,
            confidence=int(signal.confidence),
            volatility=volatility,
            raw_signal=signal,
            base_reason=reason,
        )
        score_payload = score.to_payload()

        return {
            "ticker": symbol,
            "symbol": symbol,
            "signal": signal_label,
            "decision": score_payload.get("decision_result", {}).get("decision"),
            "confidence": int(signal.confidence),
            "score": int(signal.confidence),
            "rsi": round(signal.rsi, 1),
            "ema12": round(signal.ema12, 2),
            "ema26": round(signal.ema26, 2),
            "trend": trend,
            "risk": self._risk_rating(signal.confidence, volatility),
            "reason": reason,
            "reasons": list(signal.reasons),
            "opportunity": reason,
            "price": round(signal.price, 2),
            "stop_loss": round(float(getattr(signal, "stop_loss", 0.0)), 2) if getattr(signal, "stop_loss", None) is not None else None,
            "target": round(float(getattr(signal, "target", 0.0)), 2) if getattr(signal, "target", None) is not None else None,
            "overall_score": score_payload["overall_score"],
            "score_breakdown": score_payload["score_breakdown"],
            "ranking_reason": score_payload["ranking_reason"],
            "technical_score": score_payload["technical_score"],
            "strategy_score": score_payload["strategy_score"],
            "risk_score": score_payload["risk_score"],
            "portfolio_score": score_payload["portfolio_score"],
            "market_score": score_payload["market_score"],
            "technical_component": score_payload.get("technical"),
            "strategy_component": score_payload.get("strategy"),
            "risk_component": score_payload.get("risk"),
            "portfolio_component": score_payload.get("portfolio"),
            "market_component": score_payload.get("market"),
            "decision_result": score_payload.get("decision_result"),
            "raw": signal,
        }

    def _signal_detail(self, row: dict[str, Any]) -> dict[str, Any]:
        if not row:
            return {}
        raw_signal = row.get("raw")
        if not isinstance(raw_signal, TradeSignal):
            return {}
        return {
            "symbol": row.get("ticker", raw_signal.symbol),
            "company_name": row.get("ticker", raw_signal.symbol),
            "latest_price": f"{raw_signal.price:.2f}",
            "rsi": round(raw_signal.rsi, 1),
            "ema12": round(raw_signal.ema12, 2),
            "ema26": round(raw_signal.ema26, 2),
            "strategy_reason": " | ".join(raw_signal.reasons) if raw_signal.reasons else "Strategy signal generated",
            "risk_summary": self._risk_rating(raw_signal.confidence),
            "confidence_score": raw_signal.confidence,
            "suggested_stop_loss": f"{raw_signal.stop_loss:.2f}",
            "suggested_take_profit": f"{raw_signal.target:.2f}",
        }

    def _risk_rating(self, confidence: int, volatility: float | None = None) -> str:
        if volatility is None:
            volatility = 0.0

        if volatility >= 0.04:
            return "High"
        if volatility >= 0.02:
            return "Medium"
        if confidence >= 80:
            return "Low"
        if confidence >= 60:
            return "Medium"
        return "High"

    def _volatility(self, data: pd.DataFrame | None) -> float:
        if data is None or data.empty:
            return 0.0

        close = data.get("Close") if "Close" in data.columns else None
        if close is None:
            return 0.0

        if isinstance(close, pd.DataFrame):
            if close.shape[1] == 0:
                return 0.0
            close = close.iloc[:, 0]

        close = pd.Series(close).dropna()
        if len(close) < 2:
            return 0.0

        returns = close.pct_change().dropna()
        if returns.empty:
            return 0.0

        volatility = returns.rolling(20).std().iloc[-1]
        if pd.isna(volatility):
            return 0.0
        return float(volatility)

    def _trend(self, signal: TradeSignal) -> str:
        if signal.ema12 > signal.ema26:
            return "Bullish"
        if signal.ema12 < signal.ema26:
            return "Bearish"
        return "Neutral"
