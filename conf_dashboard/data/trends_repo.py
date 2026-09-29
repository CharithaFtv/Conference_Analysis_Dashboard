"""Queries backing the Series Trends tab.

Trend is now derived from each conference's own composite score (from
CONF_ROI_SCORECARD) rather than raw yearly counts, so this repository joins
through CONF_SERIES_MAP to CONF_ROI_SCORECARD instead of CONF_ROI_YOY.
"""

import pandas as pd

from conf_dashboard.config import SCORECARD_TABLE, SERIES_MAP_TABLE, SERIES_SCORECARD_TABLE
from conf_dashboard.data.db import run_query


def get_recurring_series(series_subquery: str, params: dict) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT CONFERENCE_SERIES, TOTAL_YEARS_ATTENDED AS N_YEARS
        FROM {SERIES_SCORECARD_TABLE}
        WHERE TOTAL_YEARS_ATTENDED >= 2 AND CONFERENCE_SERIES IN ({series_subquery})
        ORDER BY N_YEARS DESC, CONFERENCE_SERIES
        """,
        params,
    )


def get_series_score_history(series: str) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT
            YEAR(s.START_DATE) AS CONFERENCE_YEAR,
            s.CONFERENCE_ID, s.CONFERENCE_NAME, s.START_DATE,
            s.ALL_COMPANIES_MET_COUNT, s.HQTS_SOURCED, s.HQTS_AT_HQM,
            s.HQTS_AT_TOP_PROSPECT, s.TOUGH_TO_CRACK_TO_HQM, s.COMPOSITE_SCORE
        FROM {SCORECARD_TABLE} s
        JOIN {SERIES_MAP_TABLE} m ON s.CONFERENCE_ID = m.ID
        WHERE m.CANONICAL_SERIES = %(series)s
        ORDER BY s.START_DATE
        """,
        {"series": series},
    )
