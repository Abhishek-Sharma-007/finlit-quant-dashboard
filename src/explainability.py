"""Human-readable signal explanations for educational dashboard output."""

from __future__ import annotations

OVERBOUGHT_RSI = 70.0
OVERSOLD_RSI = 30.0
HIGH_VOLATILITY_THRESHOLD = 0.35
SIGNIFICANT_DRAWDOWN_THRESHOLD = -0.20


def generate_signal_explanation(
    latest_close: float,
    latest_sma20: float,
    latest_sma50: float,
    latest_rsi: float,
    annualized_volatility: float,
    max_drawdown: float,
) -> str:
    """Generate a multi-sentence explanation of the current technical setup.

    Breaks the signal into trend, momentum, volatility, and drawdown components
    so a learner can see exactly why the dashboard reached its conclusion.

    Args:
        latest_close: Most recent close price.
        latest_sma20: Latest 20-period SMA.
        latest_sma50: Latest 50-period SMA.
        latest_rsi: Latest RSI value (0-100).
        annualized_volatility: Annualized volatility as a decimal.
        max_drawdown: Worst peak-to-trough decline as a negative decimal.

    Returns:
        A paragraph explaining each component of the signal in plain English,
        ending with an educational disclaimer.
    """
    sentences: list[str] = []

    # Trend component.
    if latest_close > latest_sma20 > latest_sma50:
        sentences.append(
            "The latest close is above both SMA 20 and SMA 50, which suggests "
            "positive short-to-medium-term momentum."
        )
    elif latest_close < latest_sma20 < latest_sma50:
        sentences.append(
            "The latest close is below both SMA 20 and SMA 50, which suggests "
            "negative short-to-medium-term momentum."
        )
    else:
        sentences.append(
            "The relationship between price, SMA 20, and SMA 50 is mixed, so "
            "trend direction is not clearly established."
        )

    # RSI component.
    if latest_rsi > OVERBOUGHT_RSI:
        sentences.append(
            f"RSI is {latest_rsi:.1f}, above 70, which is traditionally read as overbought."
        )
    elif latest_rsi < OVERSOLD_RSI:
        sentences.append(
            f"RSI is {latest_rsi:.1f}, below 30, which is traditionally read as oversold."
        )
    else:
        sentences.append(
            f"RSI is {latest_rsi:.1f}, within the neutral 30-70 band, so momentum is "
            "not flagged as extreme."
        )

    # Volatility component.
    if annualized_volatility > HIGH_VOLATILITY_THRESHOLD:
        sentences.append(
            f"Annualized volatility is {annualized_volatility * 100:.1f}%, above the 35% "
            "threshold the dashboard treats as elevated risk."
        )
    else:
        sentences.append(
            f"Annualized volatility is {annualized_volatility * 100:.1f}%, within a "
            "normal range for this dashboard's heuristic."
        )

    # Drawdown component.
    if max_drawdown <= SIGNIFICANT_DRAWDOWN_THRESHOLD:
        sentences.append(
            f"Max drawdown is {max_drawdown * 100:.1f}%, a meaningful peak-to-trough decline "
            "that warrants caution when sizing positions."
        )
    else:
        sentences.append(
            f"Max drawdown is {max_drawdown * 100:.1f}%, within a moderate range for the "
            "selected period."
        )

    sentences.append(
        "These metrics are backward-looking and educational only; they do not predict "
        "future performance and are not financial advice."
    )

    return " ".join(sentences)
