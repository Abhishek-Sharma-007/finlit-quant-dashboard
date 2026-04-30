"""Unit tests for indicator calculations."""

from __future__ import annotations

import pandas as pd
import pytest

from src.indicators import (
    calculate_daily_returns,
    calculate_ema,
    calculate_rsi,
    calculate_sma,
)


def test_calculate_sma_window_three() -> None:
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    sma = calculate_sma(prices, window=3)
    expected = pd.Series([None, None, 11.0, 12.0, 13.0], dtype="float64")
    pd.testing.assert_series_equal(sma.reset_index(drop=True), expected, check_names=False)


def test_calculate_sma_invalid_window_raises() -> None:
    prices = pd.Series([10.0, 11.0, 12.0])
    with pytest.raises(ValueError):
        calculate_sma(prices, window=0)


def test_calculate_ema_returns_series_of_expected_length() -> None:
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    ema = calculate_ema(prices, window=3)
    assert isinstance(ema, pd.Series)
    assert len(ema) == len(prices)
    assert ema.dropna().iloc[-1] > 0


def test_calculate_daily_returns_basic() -> None:
    prices = pd.Series([100.0, 110.0, 99.0])
    returns = calculate_daily_returns(prices)
    assert len(returns) == 2
    assert returns.iloc[0] == pytest.approx(0.10)
    assert returns.iloc[1] == pytest.approx(-0.10)


def test_calculate_rsi_stays_within_expected_range() -> None:
    prices = pd.Series(
        [100, 101, 102, 100, 98, 99, 101, 103, 104, 106, 105, 104, 103, 102, 101, 100, 99, 100]
    )
    rsi = calculate_rsi(prices, window=14).dropna()
    assert not rsi.empty
    assert (rsi >= 0).all()
    assert (rsi <= 100).all()
