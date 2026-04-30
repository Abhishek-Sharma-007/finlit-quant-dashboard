# Sample Requests and Usage

Use this guide to quickly try each tab of the FinLit Quant Dashboard.

## 1) Single Asset Analysis (Tab 1)
Analyze one ticker with SMA, RSI, risk metrics, and educational signal text.

### Example tickers
- `AAPL`
- `MSFT`
- `NVDA`
- `TSLA`
- `INFY.NS`
- `TCS.NS`
- `RELIANCE.NS`

## 2) Asset Comparison (Tab 2)
Compare multiple tickers with normalized performance, summary stats, and correlation matrix.

### Example comparison ticker sets
- `AAPL,MSFT,NVDA`
- `AAPL,TSLA,MSFT`
- `INFY.NS,TCS.NS,RELIANCE.NS`

## 3) Portfolio Simulator (Tab 3)
Provide comma-separated tickers + weights (weights can be percent-style or decimals).

### Example portfolio inputs
- `Tickers: AAPL,MSFT,NVDA`
- `Weights: 40,30,30`

- `Tickers: AAPL,TSLA,MSFT`
- `Weights: 0.4,0.3,0.3`

- `Tickers: INFY.NS,TCS.NS,RELIANCE.NS`
- `Weights: 35%,35%,30%`

## 4) Financial Literature Search (Tab 4)
Search curated finance notes using TF-IDF similarity (with fallback literal matching).

### Example literature queries
- `momentum`
- `volatility risk`
- `interest rates valuation`
- `drawdown capital preservation`
- `diversification`
- `inflation earnings`
- `liquidity risk appetite`

## 5) Report (Tab 5)
Generate a downloadable markdown report that includes:
- market metrics,
- quant indicators,
- signal summary and explanation,
- educational hypotheses,
- literature matches,
- educational disclaimer.

## Educational Note
All outputs are educational, backward-looking observations and hypothesis prompts. They require validation and are not financial advice.
