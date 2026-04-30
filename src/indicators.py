"""Technical indicator calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_close_series(data: pd.Series | pd.DataFrame) -> pd.Series:
    """Extract and sanitize a close-price series.

    Accepts either a Series of prices or a DataFrame containing a 'Close' column,
    coerces values to numeric, and drops missing entries.
    """
    if isinstance(data, pd.DataFrame):
        if "Close" not in data.columns:
            raise ValueError("DataFrame input must include a 'Close' column.")
        series = data["Close"]
    else:
        series = data

    return pd.to_numeric(series, errors="coerce").dropna()


def calculate_daily_returns(data: pd.Series | pd.DataFrame) -> pd.Series:
    """Calculate daily percent returns from close prices.

    Args:
        data: A Series of close prices or a DataFrame with a 'Close' column.

    Returns:
        A Series of daily percent changes with the first NaN row dropped.
    """
    close = _to_close_series(data)
    returns = close.pct_change()
    return returns.dropna()


def calculate_sma(data: pd.Series | pd.DataFrame, window: int) -> pd.Series:
    """Calculate the simple moving average for a given window.

    Args:
        data: A Series of close prices or a DataFrame with a 'Close' column.
        window: Lookback window length in periods. Must be positive.

    Returns:
        A Series of SMA values, with NaNs for periods before the window fills.
    """
    if window <= 0:
        raise ValueError("Window must be a positive integer.")
    close = _to_close_series(data)
    return close.rolling(window=window, min_periods=window).mean()


def calculate_ema(data: pd.Series | pd.DataFrame, window: int) -> pd.Series:
    """Calculate the exponential moving average for a given window.

    Args:
        data: A Series of close prices or a DataFrame with a 'Close' column.
        window: Span used for the EMA. Must be positive.

    Returns:
        A Series of EMA values, with NaNs for periods before the window fills.
    """
    if window <= 0:
        raise ValueError("Window must be a positive integer.")
    close = _to_close_series(data)
    return close.ewm(span=window, adjust=False, min_periods=window).mean()


def calculate_rsi(data: pd.Series | pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI) using smoothed averages.

    Returns values clipped to the range [0, 100] once enough periods are observed.

    Args:
        data: A Series of close prices or a DataFrame with a 'Close' column.
        window: Lookback window length in periods. Defaults to 14.

    Returns:
        A Series of RSI values, with NaNs for the warm-up period.
    """
    if window <= 0:
        raise ValueError("Window must be a positive integer.")

    close = _to_close_series(data)
    delta = close.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    gain_series = pd.Series(gain, index=close.index, dtype="float64")
    loss_series = pd.Series(loss, index=close.index, dtype="float64")

    avg_gain = gain_series.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss_series.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return rsi.clip(lower=0, upper=100)
