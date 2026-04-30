"""Educational alpha-hypothesis style narrative generators."""

from __future__ import annotations

import math

import pandas as pd


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(converted):
        return default
    return converted


def generate_single_asset_insights(metrics: dict) -> str:
    """Create educational single-asset research insight text."""
    latest_close = _safe_float(metrics.get("latest_close"))
    sma20 = _safe_float(metrics.get("latest_sma20"))
    sma50 = _safe_float(metrics.get("latest_sma50"))
    rsi = _safe_float(metrics.get("latest_rsi"), default=50.0)
    volatility = _safe_float(metrics.get("annualized_volatility"))
    max_drawdown = _safe_float(metrics.get("max_drawdown"))

    trend = "mixed trend condition"
    if latest_close > sma20 and latest_close > sma50:
        trend = "positive trend alignment (price above SMA 20 and SMA 50)"
    elif latest_close < sma20 and latest_close < sma50:
        trend = "weaker trend alignment (price below SMA 20 and SMA 50)"

    if rsi >= 70:
        momentum = "elevated momentum condition (RSI in historically stretched territory)"
    elif rsi <= 30:
        momentum = "compressed momentum condition (RSI in historically weak territory)"
    else:
        momentum = "balanced momentum condition (RSI in a middle range)"

    if volatility >= 0.35:
        vol_note = "higher volatility condition that may require tighter risk framing"
    elif volatility >= 0.20:
        vol_note = "moderate volatility condition"
    else:
        vol_note = "relatively lower volatility condition"

    dd_note = (
        "deeper historical drawdown profile"
        if max_drawdown <= -0.30
        else "contained historical drawdown profile"
    )

    return (
        f"Trend: {trend}. Momentum: {momentum}. Volatility: {vol_note}. "
        f"Drawdown: {dd_note}. Educational signal hypothesis: this setup can be studied as a "
        "backward-looking momentum/reversion hypothesis, but it requires validation across "
        "multiple assets and time periods and is not financial advice."
    )


def generate_comparison_insights(summary_df: pd.DataFrame, corr_df: pd.DataFrame) -> str:
    """Create educational cross-asset insight text."""
    if summary_df is None or summary_df.empty:
        return (
            "Cross-asset research hypothesis: insufficient summary statistics to form observations. "
            "Any interpretation requires more historical data and validation; not financial advice."
        )

    best_performer = summary_df["cumulative_return"].idxmax()
    low_vol = summary_df["annualized_volatility"].idxmin()
    best_rr = summary_df["return_risk_ratio"].idxmax()

    corr_observation = "correlation observations are unavailable."
    if corr_df is not None and not corr_df.empty and corr_df.shape[0] > 1:
        pairs: list[tuple[str, str, float]] = []
        cols = list(corr_df.columns)
        for i, left in enumerate(cols):
            for right in cols[i + 1 :]:
                pairs.append((left, right, float(corr_df.loc[left, right])))
        if pairs:
            max_pair = max(pairs, key=lambda x: x[2])
            min_pair = min(pairs, key=lambda x: x[2])
            corr_observation = (
                f"Highest pairwise correlation is {max_pair[0]} vs {max_pair[1]} ({max_pair[2]:.2f}), "
                f"while lowest is {min_pair[0]} vs {min_pair[1]} ({min_pair[2]:.2f})."
            )

    return (
        f"Best historical performer by cumulative return: {best_performer}. "
        f"Lowest historical volatility: {low_vol}. "
        f"Strongest historical return/risk profile: {best_rr}. "
        f"{corr_observation} This is an educational cross-asset hypothesis based on "
        "backward-looking data and requires validation; not financial advice."
    )


def generate_portfolio_insights(
    tickers: list[str], weights: list[float], portfolio_metrics: dict
) -> str:
    """Create educational portfolio insight text."""
    if not tickers or not weights:
        return (
            "Portfolio risk hypothesis: no valid allocation provided. Add tickers and weights to "
            "study diversification assumptions. Educational use only; not financial advice."
        )

    max_weight = max(weights)
    max_index = weights.index(max_weight)
    top_asset = tickers[max_index] if max_index < len(tickers) else tickers[0]
    concentration = "concentrated"
    if max_weight <= 0.35:
        concentration = "more diversified"
    elif max_weight <= 0.50:
        concentration = "moderately concentrated"

    volatility = _safe_float(portfolio_metrics.get("annualized_volatility"))
    drawdown = _safe_float(portfolio_metrics.get("max_drawdown"))

    return (
        f"The portfolio appears {concentration}, with highest allocation in {top_asset} "
        f"({max_weight * 100:.1f}%). Historical volatility is {volatility * 100:.2f}% and "
        f"max drawdown is {drawdown * 100:.2f}%. Educational portfolio risk hypothesis: "
        "allocation concentration and drawdown tolerance should be evaluated together over "
        "multiple market regimes. This is backward-looking and not financial advice."
    )


def generate_literature_insight(query: str, results_df: pd.DataFrame) -> str:
    """Create educational literature-to-signal narrative text."""
    q = (query or "").strip() or "the query"
    if results_df is None or results_df.empty:
        return (
            f"For '{q}', no strong literature match was found. Educational hypothesis: refine the "
            "query and connect concepts to measurable indicators such as trend, volatility, and "
            "drawdown. This is educational and not financial advice."
        )

    top = results_df.iloc[0]
    title = str(top.get("title", "Untitled note"))
    category = str(top.get("category", "General"))
    summary = str(top.get("summary", ""))

    reason = summary[:140] + ("..." if len(summary) > 140 else "")
    return (
        f"For the query '{q}', the top matched note is '{title}' in category '{category}'. "
        f"The match is likely driven by concept overlap: {reason} "
        "Educational literature-to-signal connection: this concept can be mapped to historical "
        "observations in trend, momentum, volatility, and drawdown analytics, but requires "
        "validation and is not financial advice."
    )
