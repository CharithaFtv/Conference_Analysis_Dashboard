"""Queries backing the Series Rankings tab."""

import pandas as pd

from conf_dashboard.config import SERIES_SCORECARD_TABLE
from conf_dashboard.data.db import run_query


def get_series_rankings(series_subquery: str, params: dict) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT *
        FROM {SERIES_SCORECARD_TABLE}
        WHERE CONFERENCE_SERIES IN ({series_subquery})
        """,
        params,
    )
