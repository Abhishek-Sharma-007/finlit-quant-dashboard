# FinLit Quant Dashboard

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/Pytest-Unit%20Tested-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/tests.yml)
[![MLH Code Sample](https://img.shields.io/badge/MLH-Code%20Sample-000000)](https://fellowship.mlh.io/)
[![Educational Finance](https://img.shields.io/badge/Finance-Educational-2E8B57)](#educational-disclaimer)

## 1. Project Overview
FinLit Quant Dashboard is a Streamlit application that connects finance concepts from literature notes with historical market signal analysis.

## 2. Problem Statement
Learners often study terms like momentum, volatility, drawdown, and diversification separately from real market data, which makes concept-to-practice transfer difficult.

## 3. Why This Project Exists
This project bridges that gap by combining market analytics, explainable signal summaries, and literature search in one modular educational dashboard.

## 4. Features
- Single asset analysis with SMA, RSI, drawdown, and risk metrics
- Recent and full OHLCV table views
- Asset comparison with normalized chart, summary stats, and correlation matrix
- Portfolio simulator with input validation, metrics, and allocation visuals
- TF-IDF literature search with cards, table, and insight text
- Research-hypothesis style educational narratives across tabs
- Downloadable markdown report with insights and disclaimer

## 5. Screenshots
- Add `Single Asset Analysis` screenshot
- Add `Asset Comparison` screenshot
- Add `Portfolio Simulator` screenshot
- Add `Financial Literature Search` screenshot
- Add `Report` screenshot

## 6. Tech Stack
- Python
- Streamlit
- pandas
- numpy
- yfinance
- plotly
- scikit-learn
- pytest
- GitHub Actions

## 7. Architecture
- `app.py`: UI orchestration and tab-level flow
- `src/`: modular domain functions (data, indicators, risk, search, reporting, insights)
- `data/`: static curated literature notes
- `tests/`: unit tests aligned with each module

## 8. Folder Structure
```text
finlit-quant-dashboard/
├── .github/
│   └── workflows/
│       └── tests.yml
├── app.py
├── data/
│   └── literature_notes.csv
├── src/
│   ├── __init__.py
│   ├── alpha_insights.py
│   ├── comparison.py
│   ├── data_loader.py
│   ├── explainability.py
│   ├── indicators.py
│   ├── literature_search.py
│   ├── portfolio.py
│   ├── reporting.py
│   ├── risk_metrics.py
│   └── signal_summary.py
├── tests/
│   ├── __init__.py
│   ├── test_alpha_insights.py
│   ├── test_indicators.py
│   ├── test_literature_search.py
│   ├── test_portfolio.py
│   ├── test_reporting.py
│   ├── test_risk_metrics.py
│   └── test_signal_summary.py
├── README.md
├── requirements.txt
├── .gitignore
├── sample_requests_or_usage.md
└── LICENSE
```

## 9. Installation
```bash
python -m venv .venv
```
Windows PowerShell:
```powershell
.venv\Scripts\activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```

## 10. Running the App
```bash
streamlit run app.py
```

## 11. Running Tests
```bash
pytest
```

## 12. GitHub Actions CI
CI runs at `.github/workflows/tests.yml` on push and pull request to `main` and `master`, installs dependencies, then runs `pytest`.

## 13. Example Tickers
- `AAPL`
- `MSFT`
- `NVDA`
- `TSLA`
- `INFY.NS`
- `TCS.NS`
- `RELIANCE.NS`

## 14. Example Literature Queries
- `momentum`
- `volatility risk`
- `interest rates valuation`
- `drawdown capital preservation`
- `diversification`
- `inflation earnings`
- `liquidity risk appetite`

## 15. Educational Signal Hypotheses
The dashboard adds hypothesis-oriented text in each major tab:
- Educational Signal Hypothesis
- Cross-Asset Research Hypothesis
- Portfolio Risk Hypothesis
- Literature-to-Signal Connection

All interpretations are backward-looking and require validation.

## 16. MLH Code Sample Fit
This project demonstrates:
- Python software engineering
- Modular architecture
- Market data API integration
- Quant metric implementation
- TF-IDF information retrieval
- Streamlit product UI
- Unit testing
- GitHub Actions CI
- Report generation
- Educational finance/quant reasoning

## 17. What I Learned
- Structuring an analytics app with clean module boundaries
- Building testable quant logic for signals and risk
- Combining information retrieval with market analytics in one product flow
- Writing explainable educational output without advice language

## 18. Limitations
- Uses free data source behavior and availability
- Metrics are historical and not predictive
- Literature corpus is intentionally compact and curated

## 19. Future Improvements
- Add benchmark comparison overlays
- Expand literature corpus coverage
- Add richer scenario analysis for portfolio inputs
- Add lint/type-check CI stages

## 20. Educational Disclaimer
This project is for educational purposes only and is not investment advice. All metrics are backward-looking and should not be used as the sole basis for financial decisions.
