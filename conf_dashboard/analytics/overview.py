"""Overview-tab computations: KPI derivation, ranking, search, top-N selection."""

import pandas as pd

DISPLAY_COLUMNS = {
    "RANK": "Rank",
    "CONFERENCE_NAME": "Conference",
    "START_DATE": "Start Date",
    "CITY": "City",
    "STATE": "State",
    "COUNTRY": "Country",
    "SOURCE_TYPE": "Type",
    "PRIORITY": "Priority",
    "SECTORS": "Sectors",
    "COMPANIES_MET": "Companies Met",
    "HQTS_SOURCED": "HQTs Sourced",
    "HQTS_AT_HQM": "HQTs at HQM",
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
    hqm_rate = (total_hqm / total_hqts * 100) if total_hqts else 0.0
    return {
        "total_conferences": total_conferences,
        "total_companies_met": total_companies_met,
        "total_hqts": total_hqts,
        "total_hqm": total_hqm,
        "hqm_rate": hqm_rate,
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
    return df[df["CONFERENCE_NAME"].str.contains(term, case=False, na=False)]


def to_display_table(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=DISPLAY_COLUMNS)[list(DISPLAY_COLUMNS.values())]


def top_performers(ranked_df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    scored = ranked_df.dropna(subset=["COMPOSITE_SCORE"])
    top_n = min(n, len(scored))
    return scored.head(top_n).sort_values("COMPOSITE_SCORE")
