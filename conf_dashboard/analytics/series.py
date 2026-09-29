"""Series Rankings-tab computations: KPI derivation, ranking, search, top-N selection."""

import pandas as pd

DISPLAY_COLUMNS = {
    "RANK": "Rank",
    "CONFERENCE_SERIES": "Series",
    "TREND": "Trend",
    "TOTAL_YEARS_ATTENDED": "Years Attended",
    "TOTAL_CONFERENCES": "Conferences",
    "SECTORS": "Sectors",
    "ERA_WEIGHTED_COMPANIES_MET": "Avg Companies Met",
    "ERA_WEIGHTED_HQTS_SOURCED": "Avg HQTs Sourced",
    "ERA_WEIGHTED_HQTS_TOP_PROSPECT": "Avg HQTs → Top Prospect",
    "ERA_WEIGHTED_TOUGH_TO_CRACK": "Avg Tough→HQM",
    "COMPOSITE_SCORE": "Score",
}

TREND_LABELS = {
    "Increasing": "📈 Increasing",
    "Declining": "📉 Declining",
    "Flat": "➖ Flat",
    "New": "🆕 New",
    "Inactive": "💤 Inactive",
    "Insufficient Data": "❓ Insufficient Data",
}


def compute_kpis(rankings_df: pd.DataFrame) -> dict:
    return {
        "total_series": len(rankings_df),
        "total_conferences": int(rankings_df["TOTAL_CONFERENCES"].sum() or 0),
        "increasing_count": int((rankings_df["TREND"] == "Increasing").sum()),
        "declining_count": int((rankings_df["TREND"] == "Declining").sum()),
    }


def rank_by_score(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.sort_values("COMPOSITE_SCORE", ascending=False, na_position="last").reset_index(
        drop=True
    )
    ranked.insert(0, "RANK", ranked.index + 1)
    return ranked


def search_by_name(df: pd.DataFrame, term: str) -> pd.DataFrame:
    if not term:
        return df
    return df[df["CONFERENCE_SERIES"].str.contains(term, case=False, na=False)]


def with_trend_labels(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["TREND"] = df["TREND"].map(TREND_LABELS).fillna(df["TREND"])
    return df


def to_display_table(df: pd.DataFrame) -> pd.DataFrame:
    return with_trend_labels(df).rename(columns=DISPLAY_COLUMNS)[list(DISPLAY_COLUMNS.values())]


def top_performers(ranked_df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    scored = ranked_df.dropna(subset=["COMPOSITE_SCORE"])
    top_n = min(n, len(scored))
    return scored.head(top_n).sort_values("COMPOSITE_SCORE")
