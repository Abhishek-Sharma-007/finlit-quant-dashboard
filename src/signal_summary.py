"""Signal interpretation helper for educational dashboard output."""

from __future__ import annotations

OVERBOUGHT_RSI = 70.0
HIGH_VOLATILITY_THRESHOLD = 0.35


def generate_signal_summary(
    latest_close: float,
    latest_sma20: float,
    latest_sma50: float,
    latest_rsi: float,
    annualized_volatility: float,
) -> str:
    """Generate an educational signal summary based on simple decision rules.

    Rules:
        - Cautious / overbought if RSI > 70.
        - Bullish trend if close > SMA20 > SMA50 and RSI < 70.
        - Bearish trend if close < SMA20 < SMA50.
        - Neutral / mixed otherwise.
        - Appends a high-volatility warning if annualized volatility > 35%.

    Args:
        latest_close: Most recent close price.
        latest_sma20: Most recent 20-period simple moving average value.
        latest_sma50: Most recent 50-period simple moving average value.
        latest_rsi: Most recent RSI value (0-100).
        annualized_volatility: Annualized volatility as a decimal (e.g. 0.25 for 25%).

    Returns:
        A short, human-readable string for educational interpretation.
    """
    if latest_rsi > OVERBOUGHT_RSI:
        base_signal = (
            "Cautious / overbought setup: RSI is above 70, which may indicate stretched momentum "
            "even if price trend is strong."
        )
    elif latest_close > latest_sma20 > latest_sma50 and latest_rsi < OVERBOUGHT_RSI:
        base_signal = (
            "Bullish trend setup: price is above SMA 20 and SMA 50 with RSI below overbought levels."
        )
    elif latest_close < latest_sma20 < latest_sma50:
        base_signal = (
            "Bearish trend setup: price is below SMA 20 and SMA 50, suggesting downward momentum."
        )
    else:
        base_signal = "Neutral / mixed setup: indicators are not aligned strongly in either direction."

    if annualized_volatility > HIGH_VOLATILITY_THRESHOLD:
        base_signal += " Volatility warning: annualized volatility is above 35%, implying elevated risk."

    base_signal += " Educational use only, not financial advice."
    return base_signal
