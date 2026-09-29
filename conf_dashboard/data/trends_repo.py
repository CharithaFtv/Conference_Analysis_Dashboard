"""Queries backing the Series Trends tab."""

import pandas as pd

from conf_dashboard.config import YOY_TABLE
from conf_dashboard.data.db import run_query


def get_recurring_series(where_sql_yoy: str, params: dict) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT CONFERENCE_SERIES, COUNT(DISTINCT CONFERENCE_YEAR) AS N_YEARS
        FROM {YOY_TABLE}
        WHERE {where_sql_yoy}
        GROUP BY 1
        HAVING N_YEARS >= 2
        ORDER BY N_YEARS DESC, CONFERENCE_SERIES
        """,
        params,
    )


def get_series_history(series: str) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT CONFERENCE_YEAR, CONFERENCE_NAME, START_DATE, CITY, STATE, COUNTRY,
               COMPANIES_MET, HQTS_SOURCED, HQTS_AT_HQM, TOUGH_TO_CRACK_TO_HQM
        FROM {YOY_TABLE}
        WHERE CONFERENCE_SERIES = %(series)s
        ORDER BY CONFERENCE_YEAR
        """,
        {"series": series},
    )
