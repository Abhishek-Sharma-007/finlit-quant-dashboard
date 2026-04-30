"""Search utilities for financial literature notes.

Provides two complementary search strategies:
- `search_literature_notes`: case-insensitive substring fallback.
- `search_literature_tfidf`: TF-IDF + cosine similarity ranking.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REQUIRED_COLUMNS = {"title", "category", "summary", "keywords"}
TEXT_COLUMNS = ["title", "category", "summary", "keywords"]


def load_literature_notes(path: str | Path) -> pd.DataFrame:
    """Load literature notes from a CSV file and validate expected columns.

    Args:
        path: Filesystem path to the literature notes CSV.

    Returns:
        A DataFrame with required text columns and missing values filled as empty strings.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required columns are missing.
    """
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Literature notes file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"Literature notes CSV is missing columns: {missing_str}")

    df = df.dropna(how="all").fillna("")
    return df


def search_literature_notes(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Substring-match search across the four text columns (case-insensitive).

    Kept as a transparent fallback for users who type literal phrases or
    punctuation that TF-IDF tokenization would discard.
    """
    if df.empty:
        return df

    cleaned_query = query.strip()
    if not cleaned_query:
        return df

    mask = pd.Series(False, index=df.index)
    for col in TEXT_COLUMNS:
        if col in df.columns:
            mask = mask | df[col].astype(str).str.contains(
                cleaned_query, case=False, na=False, regex=False
            )

    return df.loc[mask].copy()


def search_literature_tfidf(
    df: pd.DataFrame, query: str, top_k: int = 5
) -> pd.DataFrame:
    """Rank literature notes by TF-IDF cosine similarity to the query.

    Combines title, category, summary, and keywords into a per-row document,
    fits a TF-IDF vectorizer over the corpus, and scores each row against
    the query vector.

    Args:
        df: DataFrame of literature notes with the standard text columns.
        query: Free-text search query.
        top_k: Maximum number of ranked results to return.

    Returns:
        A copy of the matching rows with an additional `similarity_score` column,
        sorted by descending score. If `query` is empty, returns all rows with
        zeroed scores so downstream UI code can render them uniformly.
    """
    if df.empty:
        result = df.copy()
        result["similarity_score"] = pd.Series(dtype="float64")
        return result

    cleaned_query = (query or "").strip()
    if not cleaned_query:
        result = df.copy()
        result["similarity_score"] = 0.0
        return result

    available_cols = [c for c in TEXT_COLUMNS if c in df.columns]
    if not available_cols:
        result = df.copy()
        result["similarity_score"] = 0.0
        return result

    documents = df[available_cols].astype(str).agg(" ".join, axis=1).tolist()

    try:
        vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
        doc_matrix = vectorizer.fit_transform(documents)
        query_matrix = vectorizer.transform([cleaned_query])
        scores = cosine_similarity(query_matrix, doc_matrix).flatten()
    except ValueError:
        # Empty vocabulary (e.g. query is only stop words) — fall back to substring search.
        fallback = search_literature_notes(df, cleaned_query).copy()
        fallback["similarity_score"] = 0.0
        return fallback.head(top_k).reset_index(drop=True)

    result = df.copy()
    result["similarity_score"] = scores
    result = result.sort_values("similarity_score", ascending=False)

    # Drop zero-score rows when at least one positive match exists.
    if (result["similarity_score"] > 0).any():
        result = result[result["similarity_score"] > 0]

    return result.head(top_k).reset_index(drop=True)
