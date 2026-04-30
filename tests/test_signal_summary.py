"""Unit tests for the rule-based signal summary."""

from __future__ import annotations

from src.signal_summary import generate_signal_summary


def test_signal_summary_bullish_setup() -> None:
    summary = generate_signal_summary(
        latest_close=110.0,
        latest_sma20=105.0,
        latest_sma50=100.0,
        latest_rsi=55.0,
        annualized_volatility=0.18,
    )
    assert "Bullish trend setup" in summary
    assert "not financial advice" in summary


def test_signal_summary_bearish_setup() -> None:
    summary = generate_signal_summary(
        latest_close=90.0,
        latest_sma20=95.0,
        latest_sma50=100.0,
        latest_rsi=45.0,
        annualized_volatility=0.20,
    )
    assert "Bearish trend setup" in summary


def test_signal_summary_overbought_setup() -> None:
    summary = generate_signal_summary(
        latest_close=110.0,
        latest_sma20=105.0,
        latest_sma50=100.0,
        latest_rsi=78.0,
        annualized_volatility=0.20,
    )
    assert "overbought" in summary.lower()


def test_signal_summary_neutral_setup() -> None:
    summary = generate_signal_summary(
        latest_close=100.0,
        latest_sma20=100.0,
        latest_sma50=100.0,
        latest_rsi=50.0,
        annualized_volatility=0.20,
    )
    assert "Neutral / mixed setup" in summary


def test_signal_summary_high_volatility_warning_appended() -> None:
    summary = generate_signal_summary(
        latest_close=110.0,
        latest_sma20=105.0,
        latest_sma50=100.0,
        latest_rsi=55.0,
        annualized_volatility=0.45,
    )
    assert "Volatility warning" in summary
