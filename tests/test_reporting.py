"""Unit tests for the markdown report generator."""

from __future__ import annotations

import pandas as pd

from src.reporting import generate_markdown_report


def _sample_metrics() -> dict:
    return {
        "latest_close": 175.42,
        "cumulative_return": 0.1234,
        "annualized_volatility": 0.215,
        "max_drawdown": -0.18,
        "latest_rsi": 58.7,
        "latest_daily_return": 0.0042,
    }


def _sample_literature() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "title": "Volatility and Risk Management",
                "category": "Risk Management",
                "summary": "Volatility should be sized against position risk.",
                "keywords": "volatility;risk controls",
                "similarity_score": 0.85,
            }
        ]
    )


def test_generate_markdown_report_returns_string() -> None:
    report = generate_markdown_report(
        ticker="AAPL",
        metrics=_sample_metrics(),
        signal_summary="Bullish trend setup.",
        signal_explanation="Price is above both SMAs.",
        literature_results=_sample_literature(),
    )
    assert isinstance(report, str)
    assert len(report) > 100


def test_report_contains_ticker_and_disclaimer() -> None:
    report = generate_markdown_report(
        ticker="msft",
        metrics=_sample_metrics(),
        signal_summary="Neutral setup.",
        signal_explanation="Indicators are mixed.",
        literature_results=_sample_literature(),
    )
    assert "MSFT" in report  # ticker is uppercased
    assert "educational purposes only" in report.lower()
    assert "not investment advice" in report.lower()


def test_report_contains_signal_sections() -> None:
    report = generate_markdown_report(
        ticker="TSLA",
        metrics=_sample_metrics(),
        signal_summary="Cautious / overbought.",
        signal_explanation="RSI is above 70.",
        literature_results=_sample_literature(),
    )
    assert "## Signal Summary" in report
    assert "Cautious / overbought." in report
    assert "## Signal Explanation" in report
    assert "RSI is above 70." in report


def test_report_accepts_optional_insight_sections() -> None:
    report = generate_markdown_report(
        ticker="AAPL",
        metrics=_sample_metrics(),
        signal_summary="Signal summary text.",
        signal_explanation="Signal explanation text.",
        literature_results=_sample_literature(),
        educational_signal_hypothesis="Educational hypothesis text.",
        literature_insight="Literature insight text.",
    )
    assert "## Educational Signal Hypothesis" in report
    assert "Educational hypothesis text." in report
    assert "## Literature-to-Signal Explanation" in report
    assert "Literature insight text." in report


def test_report_handles_empty_literature() -> None:
    report = generate_markdown_report(
        ticker="AAPL",
        metrics=_sample_metrics(),
        signal_summary="Neutral.",
        signal_explanation="Mixed.",
        literature_results=pd.DataFrame(),
    )
    assert "No literature notes matched" in report


def test_report_includes_market_metrics_table() -> None:
    report = generate_markdown_report(
        ticker="AAPL",
        metrics=_sample_metrics(),
        signal_summary="Neutral.",
        signal_explanation="Mixed.",
        literature_results=_sample_literature(),
    )
    assert "## Market Metrics" in report
    assert "Latest Close" in report
    assert "Cumulative Return" in report
