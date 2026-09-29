"""Queries backing the Individual Conferences tab."""

import pandas as pd

from conf_dashboard.config import BASE_TABLE, SCORECARD_TABLE
from conf_dashboard.data.db import run_query


def get_kpi_totals(where_sql: str, params: dict) -> pd.Series:
    df = run_query(
        f"""
        SELECT
            COUNT(*) AS TOTAL_CONFERENCES,
            SUM(b.COMPANIES_MET) AS TOTAL_COMPANIES_MET,
            SUM(b.HQTS_SOURCED) AS TOTAL_HQTS_SOURCED,
            SUM(b.HQTS_AT_HQM) AS TOTAL_HQTS_AT_HQM
        FROM {BASE_TABLE} b
        WHERE {where_sql}
        """,
        params,
    )
    return df.iloc[0]


def get_scored_conferences(where_sql: str, params: dict) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT
            b.CONFERENCE_ID, b.CONFERENCE_NAME, b.START_DATE, b.END_DATE,
            b.CITY, b.STATE, b.COUNTRY, b.SOURCE_TYPE, b.SECTORS,
            b.COMPANIES_MET, b.HQTS_SOURCED, b.HQTS_AT_HQM, b.HQTS_AT_TOP_PROSPECT,
            b.TOUGH_TO_CRACK_TO_HQM,
            s.ALL_COMPANIES_MET_COUNT, s.COMPOSITE_SCORE,
            s.SCORE_COMPANIES_MET, s.SCORE_HQTS_SOURCED, s.SCORE_HQTS_TOP_PROSPECT,
            s.SCORE_YOY_SERIES, s.SCORE_TOUGH_TO_CRACK
        FROM {BASE_TABLE} b
        LEFT JOIN {SCORECARD_TABLE} s ON b.CONFERENCE_ID = s.CONFERENCE_ID
        WHERE {where_sql}
        """,
        params,
    )
