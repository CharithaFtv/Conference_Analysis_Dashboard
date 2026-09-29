"""Individual Conferences-tab computations: KPI derivation, ranking, search, top-N selection."""

import pandas as pd

DISPLAY_COLUMNS = {
    "RANK": "Rank",
    "CONFERENCE_NAME": "Conference",
    "START_DATE": "Start Date",
    "CITY": "City",
    "STATE": "State",
    "COUNTRY": "Country",
    "SOURCE_TYPE": "Type",
    "SECTORS": "Sectors",
    "ALL_COMPANIES_MET_COUNT": "Companies Met",
    "HQTS_SOURCED": "HQTs Sourced",
    "HQTS_AT_HQM": "HQTs at HQM",
    "HQTS_AT_TOP_PROSPECT": "HQTs at Top Prospect",
    "TOUGH_TO_CRACK_TO_HQM": "Tough→HQM",
    "HQT_CONVERSION_RATE": "HQT Conv. Rate",
    "HQM_CONVERSION_RATE": "HQM Conv. Rate",
    "COMPOSITE_SCORE": "Score",
}


def compute_kpis(totals_row: pd.Series) -> dict:
    total_conferences = int(totals_row["TOTAL_CONFERENCES"] or 0)
    total_companies_met = int(totals_row["TOTAL_COMPANIES_MET"] or 0)
    total_hqts = int(totals_row["TOTAL_HQTS_SOURCED"] or 0)
    total_hqm = int(totals_row["TOTAL_HQTS_AT_HQM"] or 0)
    total_tp = int(totals_row["TOTAL_HQTS_AT_TOP_PROSPECT"] or 0)
    tp_rate = (total_tp / total_hqts * 100) if total_hqts else 0.0
    return {
        "total_conferences": total_conferences,
        "total_companies_met": total_companies_met,
        "total_hqts": total_hqts,
        "total_hqm": total_hqm,
        "total_tp": total_tp,
        "tp_rate": tp_rate,
    }


def with_conversion_rates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    companies_met = df["ALL_COMPANIES_MET_COUNT"].fillna(df["COMPANIES_MET"])
    df["HQT_CONVERSION_RATE"] = (df["HQTS_SOURCED"] / companies_met * 100).where(companies_met > 0)
    df["HQM_CONVERSION_RATE"] = (df["HQTS_AT_HQM"] / df["HQTS_SOURCED"] * 100).where(
        df["HQTS_SOURCED"] > 0
    )
    return df


def rank_by_score(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.sort_values("COMPOSITE_SCORE", ascending=False, na_position="last").reset_index(
        drop=True
    )
    ranked.insert(0, "RANK", ranked.index + 1)
    return ranked


def search_by_name(df: pd.DataFrame, term: str) -> pd.DataFrame:
    if not term:
        return df
    return df[df["CONFERENCE_NAME"].str.contains(term, case=False, na=False)]


def to_display_table(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=DISPLAY_COLUMNS)[list(DISPLAY_COLUMNS.values())]


def top_performers(ranked_df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    scored = ranked_df.dropna(subset=["COMPOSITE_SCORE"])
    top_n = min(n, len(scored))
    return scored.head(top_n).sort_values("COMPOSITE_SCORE")
