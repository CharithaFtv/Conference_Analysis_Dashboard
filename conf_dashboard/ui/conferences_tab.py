import streamlit as st

from conf_dashboard.analytics.conferences import (
    compute_kpis,
    rank_by_score,
    search_by_name,
    to_display_table,
    top_performers,
    with_conversion_rates,
)
from conf_dashboard.charts.conferences_charts import build_score_breakdown_bar, build_top_performers_bar
from conf_dashboard.data.conferences_repo import get_kpi_totals, get_scored_conferences
from conf_dashboard.filters.model import FilterState
from conf_dashboard.filters.query_builder import build_where_clause


def render(filters: FilterState) -> None:
    where_sql, params = build_where_clause(filters, table_alias="b")

    kpis = compute_kpis(get_kpi_totals(where_sql, params))
    if kpis["total_conferences"] == 0:
        st.warning("No conferences match the current filters. Try widening your filter selection.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Conferences", f"{kpis['total_conferences']:,}")
    k2.metric("Companies Met", f"{kpis['total_companies_met']:,}")
    k3.metric("HQTs Sourced", f"{kpis['total_hqts']:,}")
    k4.metric("HQT → TP Rate", f"{kpis['tp_rate']:.1f}%")

    st.divider()

    full_df = rank_by_score(with_conversion_rates(get_scored_conferences(where_sql, params)))

    st.subheader(f"All Conferences ({len(full_df)})")
    search = st.text_input("Search by conference name", placeholder="e.g. Money2020, RSA, SaaStr...")
    table_df = search_by_name(full_df, search)
    display_df = to_display_table(table_df)

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
            "HQT Conv. Rate": st.column_config.NumberColumn(format="%.1f%%"),
            "HQM Conv. Rate": st.column_config.NumberColumn(format="%.1f%%"),
            "Rank": st.column_config.NumberColumn(format="%d"),
        },
        selection_mode="single-row",
        on_select="rerun",
        key="conferences_table",
    )

    selected_rows = event.selection.rows if event and event.selection else []
    if selected_rows:
        picked = table_df.iloc[selected_rows[0]]
        with st.expander(f"All fields — {picked['CONFERENCE_NAME']}", expanded=True):
            st.dataframe(picked.to_frame().T, use_container_width=True, hide_index=True)

    st.divider()

    top_df = top_performers(full_df, n=15)
    if top_df.empty:
        return

    st.subheader("Top Performers")
    st.plotly_chart(build_top_performers_bar(top_df), use_container_width=True)

    st.subheader("Score Breakdown — Top 10")
    breakdown_df = top_performers(full_df, n=10)
    st.plotly_chart(build_score_breakdown_bar(breakdown_df), use_container_width=True)
