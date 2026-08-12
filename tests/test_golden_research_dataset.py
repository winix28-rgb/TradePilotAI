from tradepilotai_os.backtesting import create_golden_research_dataset


def test_golden_research_dataset_is_deterministic_and_reusable():
    first = create_golden_research_dataset()
    second = create_golden_research_dataset()

    assert first.result.to_dict() == second.result.to_dict()
    assert first.trade_history == second.trade_history
    assert first.monthly_returns == second.monthly_returns


def test_golden_research_dataset_matches_expected_profile():
    dataset = create_golden_research_dataset()
    result = dataset.result

    assert result.initial_cash == 100000.0
    assert result.portfolio.cash == 124850.0
    assert result.metrics["net_profit"] == 24850.0
    assert result.metrics["total_return"] == 0.2485
    assert result.metrics["maximum_drawdown"] == -8.02
    assert result.metrics["win_rate"] == 61.2
    assert result.metrics["profit_factor"] == 2.1

    assert len(result.closed_trades) == 245
    assert len(dataset.trade_history) == 245
    assert len(result.equity_curve) == 36
    assert len(result.drawdown_series) == 36
    assert len(dataset.monthly_returns) == 36

    reasons = result.metrics["exit_reason_breakdown"]
    assert reasons["Stop Loss"] > 0
    assert reasons["Take Profit"] > 0
    assert reasons["Strategy Exit"] > 0
    assert reasons["End of Test"] > 0
