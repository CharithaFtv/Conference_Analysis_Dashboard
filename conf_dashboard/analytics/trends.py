"""Series Trends-tab computations: yearly aggregation and conversion rates."""

import pandas as pd

YEARLY_SUM_COLUMNS = ["COMPANIES_MET", "HQTS_SOURCED", "HQTS_AT_HQM", "TOUGH_TO_CRACK_TO_HQM"]

DETAIL_DISPLAY_COLUMNS = {
    "CONFERENCE_YEAR": "Year",
    "CONFERENCE_NAME": "Conference",
    "START_DATE": "Start Date",
    "COMPANIES_MET": "Companies Met",
    "HQTS_SOURCED": "HQTs Sourced",
    "HQTS_AT_HQM": "HQTs at HQM",
    "TOUGH_TO_CRACK_TO_HQM": "Tough→HQM",
    "HQT_CONVERSION_RATE": "HQT Conv. Rate",
    "HQM_CONVERSION_RATE": "HQM Conv. Rate",
}

SERIES_METRICS = [
    ("COMPANIES_MET", "Companies Met"),
    ("HQTS_SOURCED", "HQTs Sourced"),
    ("HQTS_AT_HQM", "HQTs at HQM+"),
]


def series_option_labels(series_df: pd.DataFrame) -> list[str]:
    return [f"{row.CONFERENCE_SERIES} ({row.N_YEARS} yrs)" for row in series_df.itertuples()]


def has_duplicate_years(yoy_df: pd.DataFrame) -> bool:
    return bool(yoy_df["CONFERENCE_YEAR"].duplicated().any())


def aggregate_yearly(yoy_df: pd.DataFrame) -> pd.DataFrame:
    return (
        yoy_df.groupby("CONFERENCE_YEAR", as_index=False)[YEARLY_SUM_COLUMNS]
        .sum()
        .sort_values("CONFERENCE_YEAR")
    )


def with_conversion_rates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["HQT_CONVERSION_RATE"] = (df["HQTS_SOURCED"] / df["COMPANIES_MET"]).where(
        df["COMPANIES_MET"] > 0
    )
    df["HQM_CONVERSION_RATE"] = (df["HQTS_AT_HQM"] / df["HQTS_SOURCED"]).where(
        df["HQTS_SOURCED"] > 0
    )
    return df


def to_detail_table(yoy_df: pd.DataFrame) -> pd.DataFrame:
    return with_conversion_rates(yoy_df).rename(columns=DETAIL_DISPLAY_COLUMNS)
