"""Unit tests for literature search (substring + TF-IDF)."""

from __future__ import annotations

import pandas as pd

from src.literature_search import (
    search_literature_notes,
    search_literature_tfidf,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "title": "Inflation and Consumer Demand",
                "category": "Macro Economics",
                "summary": "Persistent inflation can change spending behavior.",
                "keywords": "inflation;consumer demand;pricing power",
            },
            {
                "title": "Momentum Strategies in Practice",
                "category": "Quant Strategies",
                "summary": "Momentum strategies buy recent winners and sell laggards.",
                "keywords": "momentum;trend following;factor investing",
            },
            {
                "title": "Diversification Across Assets",
                "category": "Portfolio Construction",
                "summary": "Diversification reduces concentration risk by combining assets.",
                "keywords": "diversification;correlation;portfolio construction",
            },
        ]
    )


def test_substring_search_finds_known_term() -> None:
    df = _sample_df()
    result = search_literature_notes(df, "momentum")
    assert len(result) == 1
    assert result.iloc[0]["title"] == "Momentum Strategies in Practice"


def test_substring_empty_query_returns_full_df() -> None:
    df = _sample_df()
    result = search_literature_notes(df, "")
    assert len(result) == len(df)


def test_tfidf_returns_relevant_row_first() -> None:
    df = _sample_df()
    result = search_literature_tfidf(df, "diversification reduces risk", top_k=3)
    assert not result.empty
    assert "similarity_score" in result.columns
    assert result.iloc[0]["title"] == "Diversification Across Assets"
    assert result.iloc[0]["similarity_score"] > 0


def test_tfidf_empty_query_does_not_crash() -> None:
    df = _sample_df()
    result = search_literature_tfidf(df, "", top_k=3)
    assert "similarity_score" in result.columns
    assert len(result) == len(df)
    assert (result["similarity_score"] == 0.0).all()


def test_tfidf_top_k_caps_results() -> None:
    df = _sample_df()
    result = search_literature_tfidf(df, "inflation momentum diversification", top_k=2)
    assert len(result) <= 2
