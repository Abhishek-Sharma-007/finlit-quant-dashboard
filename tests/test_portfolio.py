"""Unit tests for portfolio simulator utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.portfolio import (
    calculate_portfolio_cumulative_return,
    calculate_portfolio_metrics,
    calculate_portfolio_returns,
    parse_weights,
    validate_weights,
)


def test_parse_weights_percent_input() -> None:
    assert parse_weights("40,30,30") == pytest.approx([0.4, 0.3, 0.3])


def test_parse_weights_decimal_input() -> None:
    assert parse_weights("0.5, 0.25, 0.25") == pytest.approx([0.5, 0.25, 0.25])


def test_parse_weights_with_percent_signs() -> None:
    assert parse_weights("60%, 40%") == pytest.approx([0.6, 0.4])


def test_parse_weights_empty_raises() -> None:
    with pytest.raises(ValueError):
        parse_weights("   ")


def test_validate_weights_valid() -> None:
    assert validate_weights([0.4, 0.3, 0.3]) is True


def test_validate_weights_bad_sum() -> None:
    assert validate_weights([0.5, 0.3, 0.3]) is False


def test_validate_weights_negative() -> None:
    assert validate_weights([0.5, 0.6, -0.1]) is False


def test_validate_weights_empty() -> None:
    assert validate_weights([]) is False


def test_calculate_portfolio_returns_basic() -> None:
    returns_df = pd.DataFrame(
        {
            "A": [0.01, 0.02, -0.01],
            "B": [-0.02, 0.01, 0.03],
        }
    )
    weights = [0.5, 0.5]
    portfolio = calculate_portfolio_returns(returns_df, weights)
    assert portfolio.iloc[0] == pytest.approx(-0.005)
    assert portfolio.iloc[1] == pytest.approx(0.015)
    assert portfolio.iloc[2] == pytest.approx(0.010)


def test_calculate_portfolio_returns_weight_mismatch_raises() -> None:
    returns_df = pd.DataFrame({"A": [0.01], "B": [0.02]})
    with pytest.raises(ValueError):
        calculate_portfolio_returns(returns_df, [1.0])


def test_calculate_portfolio_metrics_returns_expected_keys() -> None:
    returns = pd.Series([0.01, -0.005, 0.02, -0.01, 0.005])
    metrics = calculate_portfolio_metrics(returns)
    assert set(metrics.keys()) == {
        "cumulative_return",
        "annualized_volatility",
        "max_drawdown",
        "return_risk_ratio",
    }
    assert isinstance(metrics["cumulative_return"], float)
    assert metrics["max_drawdown"] <= 0


def test_calculate_portfolio_cumulative_return_basic() -> None:
    returns = pd.Series([0.10, 0.10])
    result = calculate_portfolio_cumulative_return(returns)
    assert np.isclose(result, 0.21)
