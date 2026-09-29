import streamlit as st

from conf_dashboard.analytics.series import (
    compute_kpis,
    rank_by_score,
    search_by_name,
    to_display_table,
    top_performers,
)
from conf_dashboard.charts.series_charts import build_score_breakdown_bar, build_top_performers_bar
from conf_dashboard.data.series_repo import get_series_rankings
from conf_dashboard.filters.model import FilterState
from conf_dashboard.filters.query_builder import build_series_subquery


def render(filters: FilterState) -> None:
    series_subquery, params = build_series_subquery(filters)
    rankings_df = get_series_rankings(series_subquery, params)

    if rankings_df.empty:
        st.warning("No conference series match the current filters. Try widening your filter selection.")
        return

    kpis = compute_kpis(rankings_df)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Series", f"{kpis['total_series']:,}")
    k2.metric("Conferences", f"{kpis['total_conferences']:,}")
    k3.metric("📈 Increasing", f"{kpis['increasing_count']:,}")
    k4.metric("📉 Declining", f"{kpis['declining_count']:,}")

    st.divider()

    full_df = rank_by_score(rankings_df)

    st.subheader(f"All Conference Series ({len(full_df)})")
    search = st.text_input("Search by series name", placeholder="e.g. Money2020, RSA, SaaStr...")
    table_df = search_by_name(full_df, search)
    display_df = to_display_table(table_df)

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
            "Rank": st.column_config.NumberColumn(format="%d"),
        },
        selection_mode="single-row",
        on_select="rerun",
        key="series_table",
    )

    selected_rows = event.selection.rows if event and event.selection else []
    if selected_rows:
        picked = table_df.iloc[selected_rows[0]]
        st.session_state["selected_conference_series"] = picked["CONFERENCE_SERIES"]
        st.info(
            f"Selected **{picked['CONFERENCE_SERIES']}** — open the "
            "**Series Trends** tab to see its year-by-year score trend."
        )

    st.divider()

    top_df = top_performers(full_df, n=15)
    if top_df.empty:
        return

    st.subheader("Top Performers")
    st.plotly_chart(build_top_performers_bar(top_df), use_container_width=True)

    st.subheader("Score Breakdown — Top 10")
    breakdown_df = top_performers(full_df, n=10)
    st.plotly_chart(build_score_breakdown_bar(breakdown_df), use_container_width=True)
