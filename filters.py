from dataclasses import dataclass, field

import streamlit as st

from db import run_query

BASE_TABLE = "CONF_ROI_BASE"


@dataclass
class FilterState:
    year_range: tuple[int, int]
    sectors: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    cities: list[str] = field(default_factory=list)
    source_types: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)


@st.cache_data(ttl=300, show_spinner=False)
def _load_years() -> tuple[int, int]:
    df = run_query(
        f"SELECT MIN(YEAR(START_DATE)) AS MIN_YEAR, MAX(YEAR(START_DATE)) AS MAX_YEAR "
        f"FROM {BASE_TABLE}"
    )
    row = df.iloc[0]
    return int(row["MIN_YEAR"]), int(row["MAX_YEAR"])


@st.cache_data(ttl=300, show_spinner=False)
def _load_sectors() -> list[str]:
    df = run_query(f"SELECT DISTINCT SECTORS FROM {BASE_TABLE} WHERE SECTORS IS NOT NULL")
    sectors: set[str] = set()
    for raw in df["SECTORS"].dropna():
        for s in str(raw).split(","):
            s = s.strip()
            if s:
                sectors.add(s)
    return sorted(sectors)


@st.cache_data(ttl=300, show_spinner=False)
def _load_distinct(column: str) -> list[str]:
    df = run_query(
        f"SELECT DISTINCT {column} AS VAL FROM {BASE_TABLE} "
        f"WHERE {column} IS NOT NULL ORDER BY 1"
    )
    return df["VAL"].tolist()


FILTER_WIDGET_KEYS = [
    "filter_year",
    "filter_sectors",
    "filter_countries",
    "filter_states",
    "filter_cities",
    "filter_source_types",
    "filter_priorities",
]


def render_sidebar_filters() -> FilterState:
    min_year, max_year = _load_years()

    st.sidebar.header("Filters")

    if st.sidebar.button("Reset filters"):
        for key in FILTER_WIDGET_KEYS:
            st.session_state.pop(key, None)
        st.rerun()

    year_range = st.sidebar.slider(
        "Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        key="filter_year",
    )

    sectors = st.sidebar.multiselect("Sector", options=_load_sectors(), key="filter_sectors")

    countries = st.sidebar.multiselect(
        "Country", options=_load_distinct("COUNTRY"), key="filter_countries"
    )
    states = st.sidebar.multiselect("State", options=_load_distinct("STATE"), key="filter_states")
    cities = st.sidebar.multiselect("City", options=_load_distinct("CITY"), key="filter_cities")

    source_types = st.sidebar.multiselect(
        "Source Type", options=_load_distinct("SOURCE_TYPE"), key="filter_source_types"
    )
    priorities = st.sidebar.multiselect(
        "Priority", options=_load_distinct("PRIORITY"), key="filter_priorities"
    )

    return FilterState(
        year_range=year_range,
        sectors=sectors,
        countries=countries,
        states=states,
        cities=cities,
        source_types=source_types,
        priorities=priorities,
    )


def build_where_clause(filters: FilterState, table_alias: str = "") -> tuple[str, dict]:
    prefix = f"{table_alias}." if table_alias else ""
    clauses = [f"YEAR({prefix}START_DATE) BETWEEN %(year_min)s AND %(year_max)s"]
    params: dict = {"year_min": filters.year_range[0], "year_max": filters.year_range[1]}

    def _in_clause(col: str, values: list[str], key: str) -> None:
        if not values:
            return
        names = []
        for i, v in enumerate(values):
            pname = f"{key}_{i}"
            params[pname] = v
            names.append(f"%({pname})s")
        clauses.append(f"{prefix}{col} IN ({', '.join(names)})")

    _in_clause("COUNTRY", filters.countries, "country")
    _in_clause("STATE", filters.states, "state")
    _in_clause("CITY", filters.cities, "city")
    _in_clause("SOURCE_TYPE", filters.source_types, "source_type")
    _in_clause("PRIORITY", filters.priorities, "priority")

    if filters.sectors:
        sector_ors = []
        normalized = f"(',' || REPLACE({prefix}SECTORS, ' ', '') || ',')"
        for i, s in enumerate(filters.sectors):
            pname = f"sector_{i}"
            params[pname] = f",{s},"
            sector_ors.append(f"{normalized} LIKE '%%' || %({pname})s || '%%'")
        clauses.append(f"({' OR '.join(sector_ors)})")

    return " AND ".join(clauses), params


def build_conference_id_subquery(filters: FilterState) -> tuple[str, dict]:
    where_sql, params = build_where_clause(filters, table_alias="cb")
    subquery = f"SELECT cb.CONFERENCE_ID FROM {BASE_TABLE} cb WHERE {where_sql}"
    return subquery, params
