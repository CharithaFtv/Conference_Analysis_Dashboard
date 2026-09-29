"""Series Trends-tab computations: composite-score trend per year for a series."""

import pandas as pd

DETAIL_DISPLAY_COLUMNS = {
    "CONFERENCE_YEAR": "Year",
    "CONFERENCE_LINK": "Conference",
    "START_DATE": "Start Date",
    "ALL_COMPANIES_MET_COUNT": "Companies Met",
    "HQTS_SOURCED": "HQTs Sourced",
    "HQTS_AT_HQM": "HQTs at HQM",
    "HQTS_AT_TOP_PROSPECT": "HQTs at Top Prospect",
    "TOUGH_TO_CRACK_TO_HQM": "Tough→HQM",
    "COMPOSITE_SCORE": "Score",
}


def series_option_labels(series_df: pd.DataFrame) -> list[str]:
    return [f"{row.CONFERENCE_SERIES} ({row.N_YEARS} yrs)" for row in series_df.itertuples()]


def has_duplicate_years(history_df: pd.DataFrame) -> bool:
    return bool(history_df["CONFERENCE_YEAR"].duplicated().any())


def yearly_score_trend(history_df: pd.DataFrame) -> pd.DataFrame:
    return (
        history_df.dropna(subset=["COMPOSITE_SCORE"])
        .groupby("CONFERENCE_YEAR", as_index=False)["COMPOSITE_SCORE"]
        .mean()
        .sort_values("CONFERENCE_YEAR")
    )


def to_detail_table(history_df: pd.DataFrame) -> pd.DataFrame:
    return history_df.rename(columns=DETAIL_DISPLAY_COLUMNS)[list(DETAIL_DISPLAY_COLUMNS.values())]
