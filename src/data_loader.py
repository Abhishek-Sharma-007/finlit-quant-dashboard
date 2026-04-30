"""Utilities for loading market data."""

from __future__ import annotations

from typing import Final

import pandas as pd
import yfinance as yf

REQUIRED_COLUMNS: Final[set[str]] = {"Open", "High", "Low", "Close", "Volume"}


def fetch_market_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch historical daily market data for a ticker.

    Args:
        ticker: Market symbol supported by Yahoo Finance.
        period: Time period accepted by yfinance, e.g. "6mo", "1y", "2y".

    Returns:
        A DataFrame indexed by date with standard OHLCV columns.

    Raises:
        ValueError: If ticker is empty, data is empty, or required columns are missing.
        RuntimeError: If the upstream API call fails.
    """
    cleaned_ticker = ticker.strip().upper()
    if not cleaned_ticker:
        raise ValueError("Ticker cannot be empty.")

    try:
        data = yf.Ticker(cleaned_ticker).history(period=period, interval="1d", auto_adjust=False)
    except Exception as exc:  # pragma: no cover - network/runtime behavior
        raise RuntimeError(f"Failed to fetch market data for {cleaned_ticker}.") from exc

    if data.empty:
        raise ValueError(f"No market data returned for ticker '{cleaned_ticker}'.")

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing expected columns in market data: {missing_str}.")

    return data
