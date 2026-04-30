"""Multi-asset comparison utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf

from src.risk_metrics import (
    calculate_annualized_volatility,
    calculate_cumulative_return,
    calculate_max_drawdown,
)


def fetch_multiple_assets(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    """Fetch close-price history for multiple tickers.

    Args:
        tickers: List of Yahoo-Finance-compatible symbols.
        period: yfinance period string, e.g. "6mo", "1y", "2y".

    Returns:
        A DataFrame indexed by date with one column per ticker. Tickers that
        return no data are silently dropped from the result.

    Raises:
        ValueError: If `tickers` is empty or no ticker returned data.
        RuntimeError: If the upstream API call fails.
    """
    cleaned = [t.strip().upper() for t in tickers if t and t.strip()]
    if not cleaned:
        raise ValueError("Tickers list cannot be empty.")

    try:
        raw = yf.download(
            tickers=cleaned,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="column",
        )
    except Exception as exc:  # pragma: no cover - network/runtime behavior
        raise RuntimeError("Failed to fetch market data for comparison.") from exc

    if raw.empty:
        raise ValueError("No market data returned for the requested tickers.")

    # Multi-ticker downloads return MultiIndex columns; single-ticker returns flat.
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" not in raw.columns.get_level_values(0):
            raise ValueError("Downloaded data is missing the 'Close' column.")
        close_df = raw["Close"].copy()
    else:
        if "Close" not in raw.columns:
            raise ValueError("Downloaded data is missing the 'Close' column.")
        close_df = raw[["Close"]].copy()
        close_df.columns = [cleaned[0]]

    # Drop columns that are entirely empty (failed tickers).
    close_df = close_df.dropna(axis=1, how="all")
    if close_df.empty:
        raise ValueError("No valid price data was returned for any ticker.")

    return close_df


def normalize_prices(price_df: pd.DataFrame) -> pd.DataFrame:
    """Rebase every price column so the first valid observation equals 100."""
    if price_df.empty:
        return price_df.copy()

    first_valid = price_df.bfill().iloc[0]
    if (first_valid == 0).any():
        raise ValueError("Cannot normalize prices: first observation contains zero.")
    return price_df.divide(first_valid).multiply(100.0)


def calculate_asset_comparison_table(price_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-ticker summary stats: cumulative return, vol, max drawdown, return/risk."""
    if price_df.empty:
        raise ValueError("Price DataFrame cannot be empty.")

    rows = []
    for ticker in price_df.columns:
        prices = price_df[ticker].dropna()
        if prices.empty:
            continue

        daily_returns = prices.pct_change().dropna()
        cum_return = calculate_cumulative_return(prices)
        ann_vol = (
            calculate_annualized_volatility(daily_returns) if not daily_returns.empty else float("nan")
        )
        max_dd = calculate_max_drawdown(prices)
        return_risk = cum_return / ann_vol if ann_vol and ann_vol != 0 else float("nan")

        rows.append(
            {
                "ticker": ticker,
                "cumulative_return": cum_return,
                "annualized_volatility": ann_vol,
                "max_drawdown": max_dd,
                "return_risk_ratio": return_risk,
            }
        )

    return pd.DataFrame(rows).set_index("ticker")


def calculate_correlation_matrix(price_df: pd.DataFrame) -> pd.DataFrame:
    """Return the pairwise correlation matrix of daily returns across tickers."""
    if price_df.empty:
        raise ValueError("Price DataFrame cannot be empty.")
    returns = price_df.pct_change().dropna(how="all")
    if returns.empty:
        raise ValueError("Not enough data to compute correlations.")
    return returns.corr().round(4)
