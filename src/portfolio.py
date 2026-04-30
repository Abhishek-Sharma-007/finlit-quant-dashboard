"""Portfolio simulation utilities."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.risk_metrics import (
    calculate_annualized_volatility,
    calculate_max_drawdown,
)

WEIGHT_TOLERANCE = 0.01


def parse_weights(weights_text: str) -> list[float]:
    """Parse a comma-separated weights string into a list of decimal weights.

    Accepts inputs like "40,30,30", "40%, 30%, 30%", or "0.4, 0.3, 0.3".
    Values greater than 1.5 are interpreted as percentages and divided by 100.

    Args:
        weights_text: Raw user input string.

    Returns:
        A list of float weights as decimals.

    Raises:
        ValueError: If the input is empty or contains non-numeric tokens.
    """
    if not weights_text or not weights_text.strip():
        raise ValueError("Weights input cannot be empty.")

    tokens = [t.strip().rstrip("%") for t in weights_text.split(",") if t.strip()]
    if not tokens:
        raise ValueError("Weights input cannot be empty.")

    try:
        raw_values = [float(t) for t in tokens]
    except ValueError as exc:
        raise ValueError(f"Could not parse weights from input: '{weights_text}'.") from exc

    # Heuristic: if any value > 1.5, assume the user meant percentages.
    if any(v > 1.5 for v in raw_values):
        return [v / 100.0 for v in raw_values]
    return raw_values


def validate_weights(weights: list[float], tolerance: float = WEIGHT_TOLERANCE) -> bool:
    """Return True if weights are non-negative and sum to ~1.0 within tolerance."""
    if not weights:
        return False
    if any((w < 0) or math.isnan(w) for w in weights):
        return False
    return math.isclose(sum(weights), 1.0, abs_tol=tolerance)


def calculate_portfolio_returns(
    returns_df: pd.DataFrame, weights: list[float]
) -> pd.Series:
    """Calculate weighted daily portfolio returns.

    Args:
        returns_df: DataFrame of daily returns where columns are tickers.
        weights: List of decimal weights aligned with the column order.

    Returns:
        A Series of portfolio daily returns indexed by date.

    Raises:
        ValueError: If weights length does not match the number of columns.
    """
    if returns_df.empty:
        raise ValueError("Returns DataFrame cannot be empty.")
    if len(weights) != returns_df.shape[1]:
        raise ValueError(
            f"Number of weights ({len(weights)}) does not match number of "
            f"return columns ({returns_df.shape[1]})."
        )

    weight_array = np.array(weights, dtype="float64")
    portfolio = returns_df.fillna(0.0).values @ weight_array
    return pd.Series(portfolio, index=returns_df.index, name="portfolio_return")


def calculate_portfolio_cumulative_return(portfolio_returns: pd.Series) -> float:
    """Calculate total cumulative return from a series of daily portfolio returns."""
    if portfolio_returns.empty:
        raise ValueError("Portfolio returns cannot be empty.")
    cumulative = float((1.0 + portfolio_returns).prod() - 1.0)
    return cumulative


def calculate_portfolio_metrics(portfolio_returns: pd.Series) -> dict:
    """Compute cumulative return, volatility, max drawdown, and return/risk ratio."""
    if portfolio_returns.empty:
        raise ValueError("Portfolio returns cannot be empty.")

    cum_return = calculate_portfolio_cumulative_return(portfolio_returns)
    ann_vol = calculate_annualized_volatility(portfolio_returns)

    equity_curve = (1.0 + portfolio_returns).cumprod()
    max_dd = calculate_max_drawdown(equity_curve)

    return {
        "cumulative_return": cum_return,
        "annualized_volatility": ann_vol,
        "max_drawdown": max_dd,
        "return_risk_ratio": (cum_return / ann_vol) if ann_vol else float("nan"),
    }
