import streamlit as st

from conf_dashboard.analytics.trends import (
    aggregate_yearly,
    has_duplicate_years,
    series_option_labels,
    to_detail_table,
    with_conversion_rates,
)
from conf_dashboard.charts.trends_charts import build_conversion_line, build_metrics_line
from conf_dashboard.data.trends_repo import get_recurring_series, get_series_history
from conf_dashboard.filters.model import FilterState
from conf_dashboard.filters.query_builder import build_where_clause


def render(filters: FilterState) -> None:
    where_sql, params = build_where_clause(filters, table_alias="")
    where_sql_yoy = where_sql.replace("YEAR(START_DATE)", "CONFERENCE_YEAR")

    series_df = get_recurring_series(where_sql_yoy, params)

    if series_df.empty:
        st.warning(
            "No recurring conference series (2+ years of history) match the current filters."
        )
        return

    series_labels = series_option_labels(series_df)
    selected_label = st.selectbox("Select a conference series", options=series_labels)
    selected_series = series_df.iloc[series_labels.index(selected_label)]["CONFERENCE_SERIES"]

    yoy_df = get_series_history(selected_series)

    st.subheader(selected_series)

    if has_duplicate_years(yoy_df):
        st.caption(
            "Note: some years have multiple logged events for this series "
            "(e.g. a renamed or re-run conference) — charts sum metrics per year; "
            "the detail table below shows each event separately."
        )

    yearly_df = with_conversion_rates(aggregate_yearly(yoy_df))

    st.plotly_chart(build_metrics_line(yearly_df), use_container_width=True)
    st.plotly_chart(build_conversion_line(yearly_df), use_container_width=True)

    st.subheader("Year-by-Year Detail")
    st.dataframe(
        to_detail_table(yoy_df),
        use_container_width=True,
        hide_index=True,
        column_config={
            "HQT Conv. Rate": st.column_config.NumberColumn(format="percent"),
            "HQM Conv. Rate": st.column_config.NumberColumn(format="percent"),
        },
    )
