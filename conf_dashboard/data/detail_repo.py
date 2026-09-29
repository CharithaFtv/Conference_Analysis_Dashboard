"""Queries backing the Conference Detail tab."""

import pandas as pd

from conf_dashboard.config import BASE_TABLE, SCORECARD_TABLE
from conf_dashboard.data.db import run_query


def get_conference_options(id_subquery: str, params: dict) -> pd.DataFrame:
    return run_query(
        f"""
        SELECT CONFERENCE_ID, CONFERENCE_NAME, START_DATE
        FROM {BASE_TABLE}
        WHERE CONFERENCE_ID IN ({id_subquery})
        ORDER BY START_DATE DESC
        """,
        params,
    )


def get_conference_base(conference_id) -> pd.DataFrame:
    return run_query(
        f"SELECT * FROM {BASE_TABLE} WHERE CONFERENCE_ID = %(cid)s", {"cid": conference_id}
    )


def get_conference_score(conference_id) -> pd.DataFrame:
    return run_query(
        f"SELECT * FROM {SCORECARD_TABLE} WHERE CONFERENCE_ID = %(cid)s", {"cid": conference_id}
    )
