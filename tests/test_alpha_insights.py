"""Unit tests for educational alpha insight generators."""

from __future__ import annotations

import pandas as pd

from src.alpha_insights import (
    generate_comparison_insights,
    generate_literature_insight,
    generate_portfolio_insights,
    generate_single_asset_insights,
)


def test_generate_single_asset_insights_contains_key_sections() -> None:
    text = generate_single_asset_insights(
        {
            "latest_close": 110,
            "latest_sma20": 100,
            "latest_sma50": 95,
            "latest_rsi": 65,
            "annualized_volatility": 0.22,
            "max_drawdown": -0.18,
        }
    )
    assert "Trend:" in text
    assert "Momentum:" in text
    assert "not financial advice" in text.lower()


def test_generate_comparison_insights_mentions_best_and_correlation() -> None:
    summary_df = pd.DataFrame(
        {
            "cumulative_return": [0.20, 0.10, 0.15],
            "annualized_volatility": [0.30, 0.15, 0.25],
            "max_drawdown": [-0.30, -0.10, -0.22],
            "return_risk_ratio": [0.67, 0.66, 0.60],
        },
        index=["AAPL", "MSFT", "NVDA"],
    )
    corr_df = pd.DataFrame(
        [[1.0, 0.9, 0.2], [0.9, 1.0, 0.1], [0.2, 0.1, 1.0]],
        index=["AAPL", "MSFT", "NVDA"],
        columns=["AAPL", "MSFT", "NVDA"],
    )
    text = generate_comparison_insights(summary_df, corr_df)
    assert "AAPL" in text
    assert "MSFT" in text
    assert "Highest pairwise correlation" in text


def test_generate_portfolio_insights_mentions_top_allocation() -> None:
    text = generate_portfolio_insights(
        ["AAPL", "MSFT", "NVDA"],
        [0.5, 0.3, 0.2],
        {"annualized_volatility": 0.2, "max_drawdown": -0.18},
    )
    assert "AAPL" in text
    assert "50.0%" in text
    assert "backward-looking" in text


def test_generate_literature_insight_handles_empty() -> None:
    text = generate_literature_insight("momentum", pd.DataFrame())
    assert "no strong literature match" in text.lower()


def test_generate_literature_insight_uses_top_result() -> None:
    df = pd.DataFrame(
        [
            {
                "title": "Momentum Strategies in Practice",
                "category": "Quant Strategies",
                "summary": "Momentum links trend persistence with systematic signal research.",
                "similarity_score": 0.9,
            }
        ]
    )
    text = generate_literature_insight("momentum", df)
    assert "Momentum Strategies in Practice" in text
    assert "Quant Strategies" in text
