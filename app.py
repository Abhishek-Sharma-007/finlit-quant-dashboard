"""Streamlit app entry point for FinLit Quant Dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.alpha_insights import (
    generate_comparison_insights,
    generate_literature_insight,
    generate_portfolio_insights,
    generate_single_asset_insights,
)
from src.comparison import (
    calculate_asset_comparison_table,
    calculate_correlation_matrix,
    fetch_multiple_assets,
    normalize_prices,
)
from src.data_loader import fetch_market_data
from src.explainability import generate_signal_explanation
from src.indicators import calculate_daily_returns, calculate_rsi, calculate_sma
from src.literature_search import load_literature_notes, search_literature_tfidf
from src.portfolio import (
    calculate_portfolio_metrics,
    calculate_portfolio_returns,
    parse_weights,
    validate_weights,
)
from src.reporting import generate_markdown_report
from src.risk_metrics import (
    calculate_annualized_volatility,
    calculate_cumulative_return,
    calculate_max_drawdown,
)
from src.signal_summary import generate_signal_summary

st.set_page_config(page_title="FinLit Quant Dashboard", layout="wide")


@st.cache_data(ttl=600, show_spinner=False)
def cached_fetch_single(ticker: str, period: str) -> pd.DataFrame:
    return fetch_market_data(ticker=ticker, period=period)


@st.cache_data(ttl=600, show_spinner=False)
def cached_fetch_multi(tickers_tuple: tuple[str, ...], period: str) -> pd.DataFrame:
    return fetch_multiple_assets(list(tickers_tuple), period=period)


@st.cache_data(show_spinner=False)
def cached_load_literature(path_str: str) -> pd.DataFrame:
    return load_literature_notes(Path(path_str))


def _analyze_single_asset(ticker: str, period: str) -> dict:
    market_df = cached_fetch_single(ticker, period)
    close = market_df["Close"]
    daily_returns = calculate_daily_returns(close)
    sma20 = calculate_sma(close, 20)
    sma50 = calculate_sma(close, 50)
    rsi = calculate_rsi(close, 14)

    metrics = {
        "latest_close": float(close.iloc[-1]),
        "cumulative_return": calculate_cumulative_return(close),
        "annualized_volatility": calculate_annualized_volatility(daily_returns),
        "max_drawdown": calculate_max_drawdown(close),
        "latest_rsi": float(rsi.dropna().iloc[-1]) if not rsi.dropna().empty else 50.0,
        "latest_daily_return": float(daily_returns.iloc[-1]) if not daily_returns.empty else 0.0,
        "latest_sma20": float(sma20.dropna().iloc[-1]) if not sma20.dropna().empty else float(close.iloc[-1]),
        "latest_sma50": float(sma50.dropna().iloc[-1]) if not sma50.dropna().empty else float(close.iloc[-1]),
    }

    return {
        "market_df": market_df,
        "close": close,
        "daily_returns": daily_returns,
        "sma20": sma20,
        "sma50": sma50,
        "rsi": rsi,
        "metrics": metrics,
    }


def _format_recent_ohlcv(df: pd.DataFrame, rows: int = 15) -> pd.DataFrame:
    ohlcv = df[["Open", "High", "Low", "Close", "Volume"]].copy().tail(rows)
    formatted = ohlcv.reset_index().rename(columns={"index": "Date"})
    formatted["Date"] = pd.to_datetime(formatted["Date"]).dt.strftime("%Y-%m-%d")
    for col in ["Open", "High", "Low", "Close"]:
        formatted[col] = pd.to_numeric(formatted[col], errors="coerce").round(2)
    formatted["Volume"] = pd.to_numeric(formatted["Volume"], errors="coerce").fillna(0).astype(int)
    return formatted


st.title("FinLit Quant Dashboard: Financial Literature & Market Signal Analyzer")
st.write(
    "An educational dashboard that connects financial literature with quantitative "
    "market signals across single assets, comparisons, and portfolios."
)

with st.sidebar:
    st.header("Inputs")
    ticker = st.text_input("Ticker", value="AAPL", help="Examples: AAPL, MSFT, NVDA, INFY.NS")
    period = st.selectbox("Period", options=["6mo", "1y", "2y", "5y"], index=1)
    comparison_text = st.text_input("Comparison tickers", value="AAPL,MSFT,NVDA")
    portfolio_tickers_text = st.text_input("Portfolio tickers", value="AAPL,MSFT,NVDA")
    portfolio_weights_text = st.text_input("Portfolio weights (sum to 100)", value="40,30,30")
    literature_query = st.text_input("Literature query", value="momentum")
    literature_top_k = st.slider("Top literature results", min_value=1, max_value=10, value=5)
    st.caption("All outputs are educational and not financial advice.")

tab_single, tab_compare, tab_portfolio, tab_literature, tab_report = st.tabs(
    ["Single Asset Analysis", "Asset Comparison", "Portfolio Simulator", "Financial Literature Search", "Report"]
)

single_analysis: dict | None = None
comparison_summary_df: pd.DataFrame | None = None
comparison_corr_df: pd.DataFrame | None = None
literature_results_df: pd.DataFrame | None = None
single_hypothesis_text = ""
literature_insight_text = ""

with tab_single:
    st.markdown("### Single Asset Analysis")
    if ticker.strip():
        try:
            single_analysis = _analyze_single_asset(ticker.strip().upper(), period)
        except (ValueError, RuntimeError) as err:
            st.error(str(err))
    else:
        st.error("Please enter a ticker symbol.")

    if single_analysis:
        m = single_analysis["metrics"]
        cols = st.columns(4)
        cols[0].metric("Latest Close", f"{m['latest_close']:.2f}")
        cols[1].metric("Cumulative Return", f"{m['cumulative_return'] * 100:.2f}%")
        cols[2].metric("Annualized Volatility", f"{m['annualized_volatility'] * 100:.2f}%")
        cols[3].metric("Max Drawdown", f"{m['max_drawdown'] * 100:.2f}%")

        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(x=single_analysis["close"].index, y=single_analysis["close"], mode="lines", name="Close"))
        price_fig.add_trace(go.Scatter(x=single_analysis["sma20"].index, y=single_analysis["sma20"], mode="lines", name="SMA 20"))
        price_fig.add_trace(go.Scatter(x=single_analysis["sma50"].index, y=single_analysis["sma50"], mode="lines", name="SMA 50"))
        price_fig.update_layout(title=f"{ticker.upper()} Close with SMA Overlays", template="plotly_white")
        st.plotly_chart(price_fig, use_container_width=True)

        signal_text = generate_signal_summary(
            latest_close=m["latest_close"],
            latest_sma20=m["latest_sma20"],
            latest_sma50=m["latest_sma50"],
            latest_rsi=m["latest_rsi"],
            annualized_volatility=m["annualized_volatility"],
        )
        explanation_text = generate_signal_explanation(
            latest_close=m["latest_close"],
            latest_sma20=m["latest_sma20"],
            latest_sma50=m["latest_sma50"],
            latest_rsi=m["latest_rsi"],
            annualized_volatility=m["annualized_volatility"],
            max_drawdown=m["max_drawdown"],
        )
        single_hypothesis_text = generate_single_asset_insights(m)

        st.markdown("#### Signal Summary")
        st.success(signal_text)
        st.markdown("#### Signal Explanation")
        st.write(explanation_text)
        st.markdown("#### Educational Signal Hypothesis")
        st.info(single_hypothesis_text)

        st.markdown("#### Recent Market Data")
        recent_ohlcv = _format_recent_ohlcv(single_analysis["market_df"], rows=15)
        st.dataframe(recent_ohlcv, use_container_width=True, hide_index=True)
        with st.expander("View full historical OHLCV data", expanded=False):
            full_ohlcv = _format_recent_ohlcv(single_analysis["market_df"], rows=len(single_analysis["market_df"]))
            st.dataframe(full_ohlcv, use_container_width=True, hide_index=True)

with tab_compare:
    st.markdown("### Asset Comparison")
    comparison_tickers = [t.strip().upper() for t in comparison_text.split(",") if t.strip()]
    if len(comparison_tickers) < 2:
        st.warning("Enter at least two tickers (example: AAPL,MSFT,NVDA).")
    else:
        try:
            price_df = cached_fetch_multi(tuple(comparison_tickers), period)
            normalized = normalize_prices(price_df)
            comparison_summary_df = calculate_asset_comparison_table(price_df)
            comparison_corr_df = calculate_correlation_matrix(price_df)
        except (ValueError, RuntimeError) as err:
            st.error(str(err))
            price_df = None

        if price_df is not None and not price_df.empty:
            norm_fig = go.Figure()
            for ticker_col in normalized.columns:
                norm_fig.add_trace(go.Scatter(x=normalized.index, y=normalized[ticker_col], mode="lines", name=ticker_col))
            norm_fig.update_layout(title="Normalized Performance (Start = 100)", template="plotly_white")
            st.plotly_chart(norm_fig, use_container_width=True)

            st.markdown("#### Summary Statistics")
            st.dataframe(
                comparison_summary_df.style.format(
                    {
                        "cumulative_return": "{:.2%}",
                        "annualized_volatility": "{:.2%}",
                        "max_drawdown": "{:.2%}",
                        "return_risk_ratio": "{:.2f}",
                    }
                ),
                use_container_width=True,
            )

            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=comparison_corr_df.values,
                    x=comparison_corr_df.columns,
                    y=comparison_corr_df.index,
                    colorscale="RdBu",
                    zmin=-1,
                    zmax=1,
                    text=comparison_corr_df.round(2).values,
                    texttemplate="%{text}",
                )
            )
            heatmap_fig.update_layout(title="Daily Return Correlation Matrix", template="plotly_white")
            st.plotly_chart(heatmap_fig, use_container_width=True)

            st.markdown("#### Comparison Insights")
            st.info(generate_comparison_insights(comparison_summary_df, comparison_corr_df))
            st.markdown("#### Cross-Asset Research Hypothesis")
            st.write(
                "Cross-asset historical observation: dispersion in cumulative returns and "
                "differences in volatility/correlation can be studied as diversification "
                "hypotheses, but these are backward-looking and require validation."
            )

portfolio_metrics: dict | None = None
portfolio_tickers_final: list[str] = []
portfolio_weights_final: list[float] = []

with tab_portfolio:
    st.markdown("### Portfolio Simulator")
    portfolio_tickers = [t.strip().upper() for t in portfolio_tickers_text.split(",") if t.strip()]
    if not portfolio_tickers:
        st.error("Enter at least one portfolio ticker.")
    else:
        try:
            weights = parse_weights(portfolio_weights_text)
        except ValueError as err:
            st.error(str(err))
            weights = None

        if weights is not None:
            if len(portfolio_tickers) != len(weights):
                st.error("The number of tickers must match the number of weights.")
            elif not validate_weights(weights):
                st.error(f"Weights must sum to 100% and be non-negative. Current sum: {sum(weights) * 100:.1f}%.")
            else:
                try:
                    prices = cached_fetch_multi(tuple(portfolio_tickers), period)
                except (ValueError, RuntimeError) as err:
                    st.error(str(err))
                    prices = None

                if prices is not None and not prices.empty:
                    portfolio_tickers_final = [t for t in portfolio_tickers if t in prices.columns]
                    portfolio_weights_final = [w for t, w in zip(portfolio_tickers, weights) if t in prices.columns]
                    total = sum(portfolio_weights_final)
                    if total <= 0:
                        st.error("No valid portfolio weights remain after filtering unavailable ticker data.")
                    else:
                        portfolio_weights_final = [w / total for w in portfolio_weights_final]
                        returns_df = prices[portfolio_tickers_final].pct_change().dropna(how="all")
                        portfolio_returns = calculate_portfolio_returns(returns_df, portfolio_weights_final)
                        portfolio_metrics = calculate_portfolio_metrics(portfolio_returns)

                        mc = st.columns(4)
                        mc[0].metric("Cumulative Return", f"{portfolio_metrics['cumulative_return'] * 100:.2f}%")
                        mc[1].metric("Annualized Volatility", f"{portfolio_metrics['annualized_volatility'] * 100:.2f}%")
                        mc[2].metric("Max Drawdown", f"{portfolio_metrics['max_drawdown'] * 100:.2f}%")
                        mc[3].metric("Return/Risk Ratio", f"{portfolio_metrics['return_risk_ratio']:.2f}")

                        equity_curve = (1 + portfolio_returns).cumprod() * 100
                        equity_fig = go.Figure(data=[go.Scatter(x=equity_curve.index, y=equity_curve, mode="lines", name="Portfolio")])
                        equity_fig.update_layout(title="Portfolio Equity Curve (Start = 100)", template="plotly_white")
                        st.plotly_chart(equity_fig, use_container_width=True)

                        returns_fig = go.Figure(data=[go.Scatter(x=portfolio_returns.index, y=portfolio_returns, mode="lines", name="Daily Returns")])
                        returns_fig.update_layout(title="Portfolio Daily Returns", template="plotly_white")
                        st.plotly_chart(returns_fig, use_container_width=True)

                        alloc_fig = go.Figure(data=[go.Pie(labels=portfolio_tickers_final, values=[w * 100 for w in portfolio_weights_final], hole=0.45)])
                        alloc_fig.update_layout(title="Portfolio Allocation", template="plotly_white")
                        st.plotly_chart(alloc_fig, use_container_width=True)

                        st.markdown("#### Portfolio Insights")
                        st.info(generate_portfolio_insights(portfolio_tickers_final, portfolio_weights_final, portfolio_metrics))
                        st.markdown("#### Portfolio Risk Hypothesis")
                        st.write(
                            "Portfolio risk hypothesis: concentration, volatility, and drawdown should be "
                            "evaluated together over different periods. This is a backward-looking educational "
                            "observation and not financial advice."
                        )

with tab_literature:
    st.markdown("### Financial Literature Search")
    notes_path = Path("data/literature_notes.csv")
    try:
        notes_df = cached_load_literature(str(notes_path))
        literature_results_df = search_literature_tfidf(notes_df, literature_query, top_k=literature_top_k)
    except (FileNotFoundError, ValueError) as err:
        notes_df = None
        st.error(str(err))

    if notes_df is not None:
        if literature_results_df is None or literature_results_df.empty:
            st.warning("No literature notes matched your query.")
        else:
            for _, row in literature_results_df.iterrows():
                with st.expander(f"{row['title']} — similarity {float(row['similarity_score']):.3f}", expanded=False):
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Summary:** {row['summary']}")
                    st.write(f"**Keywords:** {row['keywords']}")

            st.markdown("#### Results Table")
            lit_view = literature_results_df[["title", "category", "summary", "keywords", "similarity_score"]].copy()
            lit_view["similarity_score"] = lit_view["similarity_score"].round(4)
            st.dataframe(lit_view, use_container_width=True, hide_index=True)

        literature_insight_text = generate_literature_insight(literature_query, literature_results_df)
        st.markdown("#### Literature Insight")
        st.info(literature_insight_text)
        st.markdown("#### Literature-to-Signal Connection")
        st.write(
            "Literature-to-signal connection: concepts from matched notes can be translated into "
            "testable signal hypotheses using SMA, RSI, volatility, drawdown, and cross-asset "
            "correlation analysis. These are educational and require validation."
        )

with tab_report:
    st.markdown("### Report")
    if single_analysis is None:
        st.warning("Run Single Asset Analysis first to generate report inputs.")
    else:
        metrics = single_analysis["metrics"]
        signal_text = generate_signal_summary(
            latest_close=metrics["latest_close"],
            latest_sma20=metrics["latest_sma20"],
            latest_sma50=metrics["latest_sma50"],
            latest_rsi=metrics["latest_rsi"],
            annualized_volatility=metrics["annualized_volatility"],
        )
        explanation_text = generate_signal_explanation(
            latest_close=metrics["latest_close"],
            latest_sma20=metrics["latest_sma20"],
            latest_sma50=metrics["latest_sma50"],
            latest_rsi=metrics["latest_rsi"],
            annualized_volatility=metrics["annualized_volatility"],
            max_drawdown=metrics["max_drawdown"],
        )

        report_md = generate_markdown_report(
            ticker=ticker,
            metrics=metrics,
            signal_summary=signal_text,
            signal_explanation=explanation_text,
            literature_results=literature_results_df if literature_results_df is not None else pd.DataFrame(),
            educational_signal_hypothesis=single_hypothesis_text,
            literature_insight=literature_insight_text,
        )
        st.download_button(
            label="Download Markdown Report",
            data=report_md,
            file_name=f"finlit_quant_report_{ticker.strip().upper()}.md",
            mime="text/markdown",
        )
        with st.expander("Preview report", expanded=True):
            st.markdown(report_md)

st.divider()
st.warning(
    "This project is for educational purposes only and is not investment advice. "
    "All metrics are backward-looking and should not be used as the sole basis for financial decisions."
)
