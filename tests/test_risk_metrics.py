"""Unit tests for risk metric calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.risk_metrics import (
    calculate_annualized_volatility,
    calculate_cumulative_return,
    calculate_max_drawdown,
)


def test_calculate_cumulative_return() -> None:
    close_prices = pd.Series([100.0, 105.0, 110.0])
    result = calculate_cumulative_return(close_prices)
    assert np.isclose(result, 0.10)


def test_calculate_cumulative_return_empty_series_raises() -> None:
    with pytest.raises(ValueError):
        calculate_cumulative_return(pd.Series([], dtype="float64"))


def test_calculate_annualized_volatility() -> None:
    daily_returns = pd.Series([0.01, -0.02, 0.015, 0.005, -0.01])
    result = calculate_annualized_volatility(daily_returns, trading_days=252)
    expected = float(daily_returns.std(ddof=1) * np.sqrt(252))
    assert np.isclose(result, expected)


def test_calculate_annualized_volatility_invalid_trading_days() -> None:
    with pytest.raises(ValueError):
        calculate_annualized_volatility(pd.Series([0.01, -0.01]), trading_days=0)


def test_calculate_max_drawdown() -> None:
    close_prices = pd.Series([100.0, 120.0, 90.0, 95.0])
    result = calculate_max_drawdown(close_prices)
    assert np.isclose(result, -0.25)


def test_calculate_max_drawdown_monotonic_increasing_is_zero() -> None:
    close_prices = pd.Series([100.0, 105.0, 110.0, 115.0])
    result = calculate_max_drawdown(close_prices)
    assert np.isclose(result, 0.0)
