import streamlit as st

from conf_dashboard.analytics.dealcloud import with_dealcloud_link
from conf_dashboard.analytics.trends import (
    has_duplicate_years,
    series_option_labels,
    to_detail_table,
    yearly_score_trend,
)
from conf_dashboard.charts.trends_charts import build_score_trend
from conf_dashboard.data.trends_repo import get_recurring_series, get_series_score_history
from conf_dashboard.filters.model import FilterState
from conf_dashboard.filters.query_builder import build_series_subquery


def render(filters: FilterState) -> None:
    series_subquery, params = build_series_subquery(filters)
    series_df = get_recurring_series(series_subquery, params)

    if series_df.empty:
        st.warning(
            "No recurring conference series (2+ years of history) match the current filters."
        )
        return

    series_labels = series_option_labels(series_df)

    preselected = st.session_state.get("selected_conference_series")
    default_index = (
        series_df["CONFERENCE_SERIES"].tolist().index(preselected)
        if preselected in series_df["CONFERENCE_SERIES"].tolist()
        else 0
    )

    selected_label = st.selectbox("Select a conference series", options=series_labels, index=default_index)
    selected_series = series_df.iloc[series_labels.index(selected_label)]["CONFERENCE_SERIES"]

    history_df = with_dealcloud_link(get_series_score_history(selected_series))

    st.subheader(selected_series)

    if history_df["COMPOSITE_SCORE"].isna().all():
        st.info("No conferences in this series have enough history yet for a percentile score.")
        return

    if has_duplicate_years(history_df):
        st.caption(
            "Note: some years have multiple logged events for this series "
            "(e.g. a renamed or re-run conference) — the trend line averages scores per year; "
            "the detail table below shows each event separately."
        )

    yearly_df = yearly_score_trend(history_df)

    st.plotly_chart(build_score_trend(history_df, yearly_df), use_container_width=True)

    st.subheader("Year-by-Year Detail")
    st.dataframe(
        to_detail_table(history_df),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
            "Conference": st.column_config.LinkColumn(
                "Conference", display_text=r"#(.*)$", help="Click to open in DealCloud"
            ),
        },
    )
