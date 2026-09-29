"""Queries backing the sidebar filter options."""

import streamlit as st

from conf_dashboard.config import BASE_TABLE
from conf_dashboard.data.db import run_query


@st.cache_data(ttl=300, show_spinner=False)
def get_year_range() -> tuple[int, int]:
    df = run_query(
        f"SELECT MIN(YEAR(START_DATE)) AS MIN_YEAR, MAX(YEAR(START_DATE)) AS MAX_YEAR "
        f"FROM {BASE_TABLE}"
    )
    row = df.iloc[0]
    return int(row["MIN_YEAR"]), int(row["MAX_YEAR"])


@st.cache_data(ttl=300, show_spinner=False)
def get_sector_options() -> list[str]:
    df = run_query(f"SELECT DISTINCT SECTORS FROM {BASE_TABLE} WHERE SECTORS IS NOT NULL")
    sectors: set[str] = set()
    for raw in df["SECTORS"].dropna():
        for s in str(raw).split(","):
            s = s.strip()
            if s:
                sectors.add(s)
    return sorted(sectors)


@st.cache_data(ttl=300, show_spinner=False)
def get_distinct_options(column: str) -> list[str]:
    df = run_query(
        f"SELECT DISTINCT {column} AS VAL FROM {BASE_TABLE} "
        f"WHERE {column} IS NOT NULL ORDER BY 1"
    )
    return df["VAL"].tolist()
