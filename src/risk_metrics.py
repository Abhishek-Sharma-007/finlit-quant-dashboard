"""Portfolio and price-series risk metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_numeric_series(series: pd.Series) -> pd.Series:
    """Return a cleaned numeric series with NaNs dropped."""
    return pd.to_numeric(series, errors="coerce").dropna()


def calculate_cumulative_return(close_prices: pd.Series) -> float:
    """Calculate cumulative return from the first to last valid price.

    Args:
        close_prices: A Series of close prices ordered by date.

    Returns:
        A float cumulative return, e.g. 0.10 for a 10% gain.

    Raises:
        ValueError: If the cleaned price series is empty or starts at zero.
    """
    prices = _to_numeric_series(close_prices)
    if prices.empty:
        raise ValueError("Close prices cannot be empty.")

    start_price = prices.iloc[0]
    end_price = prices.iloc[-1]
    if start_price == 0:
        raise ValueError("First close price cannot be zero.")

    return float((end_price / start_price) - 1)


def calculate_annualized_volatility(daily_returns: pd.Series, trading_days: int = 252) -> float:
    """Calculate annualized volatility from a series of daily returns.

    Args:
        daily_returns: A Series of daily percent returns (not in percentage points).
        trading_days: Number of trading days per year used for scaling. Defaults to 252.

    Returns:
        A float annualized volatility, e.g. 0.20 for 20%.

    Raises:
        ValueError: If trading_days is not positive or the returns series is empty.
    """
    if trading_days <= 0:
        raise ValueError("Trading days must be a positive integer.")

    returns = _to_numeric_series(daily_returns)
    if returns.empty:
        raise ValueError("Daily returns cannot be empty.")

    return float(returns.std(ddof=1) * np.sqrt(trading_days))


def calculate_max_drawdown(close_prices: pd.Series) -> float:
    """Calculate the maximum drawdown of a close-price series.

    Args:
        close_prices: A Series of close prices ordered by date.

    Returns:
        A float in [-1, 0] representing the worst peak-to-trough decline,
        e.g. -0.25 for a 25% drawdown.

    Raises:
        ValueError: If the cleaned price series is empty.
    """
    prices = _to_numeric_series(close_prices)
    if prices.empty:
        raise ValueError("Close prices cannot be empty.")

    running_max = prices.cummax()
    drawdown = (prices / running_max) - 1
    return float(drawdown.min())
