"""Downloadable markdown report generation."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

DISCLAIMER = (
    "This report is for educational purposes only and is not investment advice. "
    "All metrics are backward-looking and should not be used as the sole basis for "
    "financial decisions."
)


def _format_metric(value: float | None, unit: str = "") -> str:
    """Render a metric value with safe handling for missing data."""
    if value is None:
        return "N/A"
    try:
        if pd.isna(value):
            return "N/A"
    except (TypeError, ValueError):
        pass
    return f"{value:.2f}{unit}"


def generate_markdown_report(
    ticker: str,
    metrics: dict,
    signal_summary: str,
    signal_explanation: str,
    literature_results: pd.DataFrame,
    educational_signal_hypothesis: str | None = None,
    literature_insight: str | None = None,
) -> str:
    """Render a clean markdown report summarizing a single-asset analysis.

    Args:
        ticker: The analyzed ticker symbol.
        metrics: Dict of computed values. Recognized keys include
            'latest_close', 'cumulative_return', 'annualized_volatility',
            'max_drawdown', 'latest_rsi', 'latest_daily_return'.
        signal_summary: Short rule-based signal string.
        signal_explanation: Multi-sentence explanation of the signal.
        literature_results: DataFrame of matched literature notes (may be empty).

    Returns:
        A markdown-formatted string suitable for download.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ticker_label = (ticker or "UNKNOWN").strip().upper() or "UNKNOWN"

    lines: list[str] = []
    lines.append(f"# FinLit Quant Dashboard Report: {ticker_label}")
    lines.append("")
    lines.append(f"**Generated:** {timestamp}  ")
    lines.append(f"**Ticker:** `{ticker_label}`")
    lines.append("")

    lines.append("## Market Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Latest Close | {_format_metric(metrics.get('latest_close'))} |")
    lines.append(
        f"| Cumulative Return | {_format_metric((metrics.get('cumulative_return') or 0) * 100, '%') if metrics.get('cumulative_return') is not None else 'N/A'} |"
    )
    lines.append(
        f"| Annualized Volatility | {_format_metric((metrics.get('annualized_volatility') or 0) * 100, '%') if metrics.get('annualized_volatility') is not None else 'N/A'} |"
    )
    lines.append(
        f"| Max Drawdown | {_format_metric((metrics.get('max_drawdown') or 0) * 100, '%') if metrics.get('max_drawdown') is not None else 'N/A'} |"
    )
    lines.append("")

    lines.append("## Quant Indicators")
    lines.append("")
    lines.append("| Indicator | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Latest RSI (14) | {_format_metric(metrics.get('latest_rsi'))} |")
    lines.append(
        f"| Latest Daily Return | {_format_metric((metrics.get('latest_daily_return') or 0) * 100, '%') if metrics.get('latest_daily_return') is not None else 'N/A'} |"
    )
    lines.append("")

    lines.append("## Signal Summary")
    lines.append("")
    lines.append(signal_summary.strip() if signal_summary else "_No summary available._")
    lines.append("")

    lines.append("## Signal Explanation")
    lines.append("")
    lines.append(signal_explanation.strip() if signal_explanation else "_No explanation available._")
    lines.append("")

    lines.append("## Educational Signal Hypothesis")
    lines.append("")
    lines.append(
        educational_signal_hypothesis.strip()
        if educational_signal_hypothesis
        else "_No educational hypothesis available._"
    )
    lines.append("")

    lines.append("## Top Literature Matches")
    lines.append("")
    if literature_results is None or literature_results.empty:
        lines.append("_No literature notes matched the active query._")
    else:
        for _, row in literature_results.iterrows():
            title = row.get("title", "Untitled")
            category = row.get("category", "")
            summary = row.get("summary", "")
            keywords = row.get("keywords", "")
            score = row.get("similarity_score")
            score_str = f" — score: {score:.3f}" if score is not None and not pd.isna(score) else ""
            lines.append(f"### {title}{score_str}")
            if category:
                lines.append(f"- **Category:** {category}")
            if summary:
                lines.append(f"- **Summary:** {summary}")
            if keywords:
                lines.append(f"- **Keywords:** {keywords}")
            lines.append("")

    lines.append("## Literature-to-Signal Explanation")
    lines.append("")
    lines.append(
        literature_insight.strip()
        if literature_insight
        else "_No literature insight available._"
    )
    lines.append("")

    lines.append("## Educational Disclaimer")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")

    return "\n".join(lines)
