"""Shared DealCloud deep-link construction, used by every conference-level table.

The conference name is embedded after a `#` so it survives as the link's
display text (via a regex `display_text` in the table's column_config)
without ever being sent to DealCloud's server — a URL fragment is stripped
by the browser before the request goes out, so odd characters in a
conference name (&, ?, =, ...) can't corrupt the actual navigation. Only the
conference ID (before the `#`) is part of the real request, so only it is
percent-encoded.
"""

from urllib.parse import quote

import pandas as pd

from conf_dashboard.config import DEALCLOUD_BASE_URL


def build_dealcloud_link(conference_id: str, conference_name: str) -> str:
    safe_id = quote(str(conference_id), safe="")
    return f"{DEALCLOUD_BASE_URL}{safe_id}#{conference_name}"


def with_dealcloud_link(
    df: pd.DataFrame,
    id_col: str = "CONFERENCE_ID",
    name_col: str = "CONFERENCE_NAME",
    out_col: str = "CONFERENCE_LINK",
) -> pd.DataFrame:
    df = df.copy()
    df[out_col] = [
        build_dealcloud_link(cid, name) for cid, name in zip(df[id_col], df[name_col])
    ]
    return df
