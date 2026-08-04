from __future__ import annotations

from tradepilotai_os.models.trade_signal import TradeSignal
from tradepilotai_os.scanner.module.opportunity_scoring import (
    OpportunityScore,
    OpportunityScoreWeights,
    OpportunityScoringEngine,
)
from tradepilotai_os.scanner.module.service import ScannerService


def test_aggregate_scores_uses_configurable_weights() -> None:
    engine = OpportunityScoringEngine(
        weights=OpportunityScoreWeights(
            technical=40.0,
            strategy=20.0,
            risk=15.0,
            portfolio=15.0,
            market=10.0,
        )
    )

    overall = engine.aggregate_scores(
        technical_score=100.0,
        strategy_score=80.0,
        risk_score=60.0,
        portfolio_score=40.0,
        market_score=20.0,
    )

    expected = round((100.0 * 40.0 + 80.0 * 20.0 + 60.0 * 15.0 + 40.0 * 15.0 + 20.0 * 10.0) / 100.0, 2)
    assert overall == expected


def test_evaluate_constructs_opportunity_score_with_breakdown() -> None:
    engine = OpportunityScoringEngine()

    score = engine.evaluate(
        symbol="TSLA",
        signal="BUY",
        confidence=82,
        volatility=0.02,
        raw_signal=None,
        base_reason="Momentum breakout",
    )

    assert isinstance(score, OpportunityScore)
    assert score.overall_score == 50.0
    assert score.technical_score == 50.0
    assert score.strategy_score == 50.0
    assert score.risk_score == 50.0
    assert score.portfolio_score == 50.0
    assert score.market_score == 50.0
    assert score.score_breakdown == {
        "technical": 50.0,
        "strategy": 50.0,
        "risk": 50.0,
        "portfolio": 50.0,
        "market": 50.0,
    }
    assert "Placeholder scoring framework active." in score.ranking_reason


def test_scanner_service_result_row_includes_scoring_fields() -> None:
    service = ScannerService()
    signal = TradeSignal(
        symbol="TSLA",
        signal="BUY",
        confidence=84,
        price=250.5,
        rsi=61.2,
        ema12=255.0,
        ema26=248.0,
        stop_loss=242.0,
        target=268.0,
        reasons=["RSI recovery", "EMA bullish crossover"],
    )

    row = service._to_result_row(symbol="TSLA", signal=signal, volatility=0.02)

    assert row["overall_score"] == 50.0
    assert row["score_breakdown"] == {
        "technical": 50.0,
        "strategy": 50.0,
        "risk": 50.0,
        "portfolio": 50.0,
        "market": 50.0,
    }
    assert row["ranking_reason"]
    assert row["technical_score"] == 50.0
    assert row["strategy_score"] == 50.0
    assert row["risk_score"] == 50.0
    assert row["portfolio_score"] == 50.0
    assert row["market_score"] == 50.0
