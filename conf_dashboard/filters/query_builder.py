"""Pure translation of `FilterState` into SQL WHERE clauses.

No Streamlit or database imports here: these functions are plain data-in,
data-out, so they can be unit tested without a Snowflake connection.
"""

from conf_dashboard.config import BASE_TABLE, SERIES_MAP_TABLE
from conf_dashboard.filters.model import FilterState


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


def build_series_subquery(filters: FilterState) -> tuple[str, dict]:
    """Canonical series names of conferences matching the filters.

    Series-level tables (CONF_SERIES_SCORECARD) don't carry per-conference
    attributes like country/city/sector, so filtering them means resolving
    to the set of qualifying series via the conference-level base table.
    """
    where_sql, params = build_where_clause(filters, table_alias="cb")
    subquery = (
        f"SELECT DISTINCT m.CANONICAL_SERIES FROM {BASE_TABLE} cb "
        f"JOIN {SERIES_MAP_TABLE} m ON cb.CONFERENCE_ID = m.ID WHERE {where_sql}"
    )
    return subquery, params
