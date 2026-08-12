from __future__ import annotations

from tradepilotai_os.performance import PerformanceEngine
from tradepilotai_os.performance import PerformanceService


def _paper_payload() -> dict:
    entries = [
        {
            "journal_id": "JRN-00001",
            "trade_id": "PT-0001",
            "strategy_id": "trend_alpha",
            "strategy_name": "Trend Alpha",
            "symbol": "AAPL",
            "asset_class": "EQUITY",
            "direction": "BUY",
            "entry_date": "2026-08-01T10:00:00+00:00",
            "exit_date": "2026-08-01T14:00:00+00:00",
            "entry_price": 100.0,
            "exit_price": 110.0,
            "quantity": 10,
            "gross_profit": 100.0,
            "costs": 5.0,
            "net_profit": 95.0,
            "exit_reason": "TAKE_PROFIT",
            "risk_snapshot": {"risk_percent": 1.0, "capital_at_risk": 1000.0, "position_size": 10.0},
        },
        {
            "journal_id": "JRN-00002",
            "trade_id": "PT-0002",
            "strategy_id": "mean_alpha",
            "strategy_name": "Mean Alpha",
            "symbol": "TSLA",
            "asset_class": "EQUITY",
            "direction": "SELL",
            "entry_date": "2026-08-02T09:00:00+00:00",
            "exit_date": "2026-08-02T16:00:00+00:00",
            "entry_price": 200.0,
            "exit_price": 210.0,
            "quantity": 5,
            "gross_profit": -50.0,
            "costs": 3.0,
            "net_profit": -53.0,
            "exit_reason": "STOP_LOSS",
            "risk_snapshot": {"risk_percent": 1.2, "capital_at_risk": 1200.0, "position_size": 5.0},
        },
    ]

    return {
        "summary": {
            "current_equity": 100042.0,
            "portfolio_value": 100042.0,
            "cash": 90000.0,
            "buying_power": 90000.0,
            "open_positions": 1,
            "closed_trades": 2,
            "total_pnl": 42.0,
            "current_exposure": 10042.0,
        },
        "closed_trades": [],
        "trade_journal": {"entries": entries},
    }


def _backtest_payload() -> dict:
    return {
        "configuration": {"strategy_id": "ema_trend", "strategy_name": "EMA Trend"},
        "closed_trades": [
            {
                "symbol": "NVDA",
                "direction": "Long",
                "entry_date": "2026-07-01T09:00:00+00:00",
                "exit_date": "2026-07-03T12:00:00+00:00",
                "entry_price": 300.0,
                "exit_price": 320.0,
                "quantity": 2,
                "gross_pnl": 40.0,
                "costs": 2.0,
                "net_pnl": 38.0,
                "exit_reason": "Strategy Exit",
            }
        ],
    }


def _comparison_payload() -> dict:
    return {
        "table": [
            {"strategy_name": "Trend Alpha", "net_profit": 95.0},
            {"strategy_name": "EMA Trend", "net_profit": 38.0},
        ]
    }


class _StubPaperService:
    def get_workspace_data(self):
        return _paper_payload()


class _StubBacktestingProvider:
    def get_backtest_data(self):
        return _backtest_payload()

    def get_comparison_data(self):
        return _comparison_payload()


def test_performance_engine_portfolio_and_summary_calculations():
    engine = PerformanceEngine()
    dashboard = engine.build_dashboard(
        paper_portfolio=_paper_payload()["summary"],
        paper_closed_trades=[],
        trade_journal_entries=_paper_payload()["trade_journal"]["entries"],
        backtest_payload=_backtest_payload(),
        strategy_comparison_payload=_comparison_payload(),
    ).to_dict()

    overview = dashboard["portfolio_overview"]
    assert overview["closed_trades"] == 3
    assert overview["net_profit"] == 80.0

    kpis = dashboard["performance_kpis"]
    assert kpis["net_profit"] == 80.0
    assert kpis["gross_profit"] == 140.0
    assert kpis["gross_loss"] == 50.0


def test_performance_engine_strategy_ranking_and_exit_analysis():
    engine = PerformanceEngine()
    dashboard = engine.build_dashboard(
        paper_portfolio=_paper_payload()["summary"],
        paper_closed_trades=[],
        trade_journal_entries=_paper_payload()["trade_journal"]["entries"],
        backtest_payload=_backtest_payload(),
        strategy_comparison_payload=_comparison_payload(),
    ).to_dict()

    strategies = dashboard["strategy_analysis"]
    assert strategies[0]["rank"] == 1
    assert strategies[0]["strategy_name"] in {"Trend Alpha", "EMA Trend"}

    exits = dashboard["exit_analysis"]
    exit_types = {row["exit_reason"] for row in exits}
    assert "Take Profit" in exit_types
    assert "Stop Loss" in exit_types
    assert "Strategy Exit" in exit_types


def test_performance_engine_equity_drawdown_monthly_and_charts():
    engine = PerformanceEngine()
    dashboard = engine.build_dashboard(
        paper_portfolio=_paper_payload()["summary"],
        paper_closed_trades=[],
        trade_journal_entries=_paper_payload()["trade_journal"]["entries"],
        backtest_payload=_backtest_payload(),
        strategy_comparison_payload=_comparison_payload(),
    ).to_dict()

    assert len(dashboard["equity_curve"]["running_equity"]) >= 2
    assert len(dashboard["equity_curve"]["peak_equity"]) >= 2

    drawdown = dashboard["drawdown"]
    assert "maximum_drawdown" in drawdown
    assert "current_drawdown" in drawdown

    monthly = dashboard["time_analysis"]["monthly_returns"]
    assert isinstance(monthly, list)

    charts = dashboard["charts"]
    assert "equity_curve" in charts
    assert "drawdown_curve" in charts
    assert "monthly_returns" in charts
    assert "strategy_comparison" in charts
    assert "exit_distribution" in charts
    assert "win_loss_distribution" in charts
    assert "portfolio_growth" in charts


def test_performance_service_exports_csv_excel_json():
    service = PerformanceService(
        paper_trading_service=_StubPaperService(),
        backtesting_data_provider=_StubBacktestingProvider(),
    )

    csv_data, csv_name, csv_mime = service.export(format_name="csv")
    xls_data, xls_name, xls_mime = service.export(format_name="excel")
    json_data, json_name, json_mime = service.export(format_name="json")

    assert csv_name.endswith(".csv")
    assert csv_mime == "text/csv"
    assert b"trade_id" in csv_data

    assert xls_name.endswith(".xls")
    assert xls_mime == "application/vnd.ms-excel"
    assert b"Section,Key,Value" in xls_data

    assert json_name.endswith(".json")
    assert json_mime == "application/json"
    assert b"portfolio_overview" in json_data
