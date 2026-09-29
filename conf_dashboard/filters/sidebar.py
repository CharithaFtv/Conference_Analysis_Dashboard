"""The sidebar filter widget: UI only, delegates data loading to filters_repo."""

import streamlit as st

from conf_dashboard.data.filters_repo import get_distinct_options, get_sector_options, get_year_range
from conf_dashboard.filters.model import FILTER_WIDGET_KEYS, FilterState


def render_sidebar_filters() -> FilterState:
    min_year, max_year = get_year_range()

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

    sectors = st.sidebar.multiselect("Sector", options=get_sector_options(), key="filter_sectors")

    countries = st.sidebar.multiselect(
        "Country", options=get_distinct_options("COUNTRY"), key="filter_countries"
    )
    states = st.sidebar.multiselect(
        "State", options=get_distinct_options("STATE"), key="filter_states"
    )
    cities = st.sidebar.multiselect(
        "City", options=get_distinct_options("CITY"), key="filter_cities"
    )

    source_types = st.sidebar.multiselect(
        "Source Type", options=get_distinct_options("SOURCE_TYPE"), key="filter_source_types"
    )

    return FilterState(
        year_range=year_range,
        sectors=sectors,
        countries=countries,
        states=states,
        cities=cities,
        source_types=source_types,
    )
