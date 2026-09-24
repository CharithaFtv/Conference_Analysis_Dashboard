import plotly.graph_objects as go
import streamlit as st

from db import run_query
from filters import FilterState, build_where_clause
from viz import SCORE_COLORS, SCORE_COLUMNS, SEQUENTIAL_BLUE, base_layout

DISPLAY_COLUMNS = {
    "RANK": "Rank",
    "CONFERENCE_NAME": "Conference",
    "START_DATE": "Start Date",
    "CITY": "City",
    "STATE": "State",
    "COUNTRY": "Country",
    "SOURCE_TYPE": "Type",
    "PRIORITY": "Priority",
    "SECTORS": "Sectors",
    "COMPANIES_MET": "Companies Met",
    "HQTS_SOURCED": "HQTs Sourced",
    "HQTS_AT_HQM": "HQTs at HQM",
    "TOUGH_TO_CRACK_TO_HQM": "Tough→HQM",
    "HQT_CONVERSION_RATE": "HQT Conv. Rate",
    "HQM_CONVERSION_RATE": "HQM Conv. Rate",
    "COMPOSITE_SCORE": "Score",
}


def render(filters: FilterState) -> None:
    where_sql, params = build_where_clause(filters, table_alias="b")

    kpi_df = run_query(
        f"""
        SELECT
            COUNT(*) AS TOTAL_CONFERENCES,
            SUM(b.COMPANIES_MET) AS TOTAL_COMPANIES_MET,
            SUM(b.HQTS_SOURCED) AS TOTAL_HQTS_SOURCED,
            SUM(b.HQTS_AT_HQM) AS TOTAL_HQTS_AT_HQM
        FROM CONF_ROI_BASE b
        WHERE {where_sql}
        """,
        params,
    )
    row = kpi_df.iloc[0]
    total_conferences = int(row["TOTAL_CONFERENCES"] or 0)

    if total_conferences == 0:
        st.warning("No conferences match the current filters. Try widening your filter selection.")
        return

    total_companies_met = int(row["TOTAL_COMPANIES_MET"] or 0)
    total_hqts = int(row["TOTAL_HQTS_SOURCED"] or 0)
    total_hqm = int(row["TOTAL_HQTS_AT_HQM"] or 0)
    hqm_rate = (total_hqm / total_hqts * 100) if total_hqts else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Conferences", f"{total_conferences:,}")
    k2.metric("Companies Met", f"{total_companies_met:,}")
    k3.metric("HQTs Sourced", f"{total_hqts:,}")
    k4.metric("HQT → HQM Rate", f"{hqm_rate:.1f}%")

    st.divider()

    full_df = run_query(
        f"""
        SELECT
            b.CONFERENCE_ID, b.CONFERENCE_NAME, b.START_DATE, b.END_DATE,
            b.CITY, b.STATE, b.COUNTRY, b.SOURCE_TYPE, b.PRIORITY, b.SECTORS,
            b.COMPANIES_MET, b.HQTS_SOURCED, b.HQTS_AT_HQM, b.TOUGH_TO_CRACK_TO_HQM,
            s.HQT_CONVERSION_RATE, s.HQM_CONVERSION_RATE, s.COMPOSITE_SCORE,
            s.SCORE_COMPANIES_MET, s.SCORE_HQT_CONVERSION, s.SCORE_HQM_POTENTIAL,
            s.SCORE_YOY_SERIES, s.SCORE_SECTOR_IMPACT, s.SCORE_TOUGH_TO_CRACK
        FROM CONF_ROI_BASE b
        LEFT JOIN CONF_ROI_SCORECARD s ON b.CONFERENCE_ID = s.CONFERENCE_ID
        WHERE {where_sql}
        """,
        params,
    )

    full_df = full_df.sort_values("COMPOSITE_SCORE", ascending=False, na_position="last").reset_index(
        drop=True
    )
    full_df.insert(0, "RANK", full_df.index + 1)

    st.subheader(f"All Conferences ({len(full_df)})")
    search = st.text_input("Search by conference name", placeholder="e.g. Money2020, RSA, SaaStr...")
    table_df = full_df
    if search:
        table_df = full_df[full_df["CONFERENCE_NAME"].str.contains(search, case=False, na=False)]

    display_df = table_df.rename(columns=DISPLAY_COLUMNS)[list(DISPLAY_COLUMNS.values())]

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
            "HQT Conv. Rate": st.column_config.NumberColumn(format="%.2f"),
            "HQM Conv. Rate": st.column_config.NumberColumn(format="%.2f"),
            "Rank": st.column_config.NumberColumn(format="%d"),
        },
        selection_mode="single-row",
        on_select="rerun",
        key="overview_table",
    )

    selected_rows = event.selection.rows if event and event.selection else []
    if selected_rows:
        picked = table_df.iloc[selected_rows[0]]
        st.session_state["selected_conference_id"] = picked["CONFERENCE_ID"]
        st.info(
            f"Selected **{picked['CONFERENCE_NAME']}** — open the "
            "**Conference Detail** tab to see its full breakdown."
        )

    st.divider()

    scored_df = full_df.dropna(subset=["COMPOSITE_SCORE"])
    if scored_df.empty:
        return

    st.subheader("Top Performers")
    top_n = min(15, len(scored_df))
    top_df = scored_df.head(top_n).sort_values("COMPOSITE_SCORE")

    bar_fig = go.Figure(
        go.Bar(
            x=top_df["COMPOSITE_SCORE"],
            y=top_df["CONFERENCE_NAME"],
            orientation="h",
            marker_color=SEQUENTIAL_BLUE[2],
            hovertemplate="%{y}<br>Score: %{x:.1f}<extra></extra>",
        )
    )
    bar_fig.update_layout(xaxis_title="Score (0–100)", yaxis_title=None)
    base_layout(bar_fig, height=max(320, 28 * top_n))
    st.plotly_chart(bar_fig, use_container_width=True)

    st.subheader("Score Breakdown — Top 10")
    breakdown_df = scored_df.head(10).sort_values("COMPOSITE_SCORE")
    breakdown_fig = go.Figure()
    for col, label in SCORE_COLUMNS:
        breakdown_fig.add_trace(
            go.Bar(
                name=label,
                x=breakdown_df[col],
                y=breakdown_df["CONFERENCE_NAME"],
                orientation="h",
                marker_color=SCORE_COLORS[col],
                hovertemplate=f"%{{y}}<br>{label}: %{{x:.1f}}<extra></extra>",
            )
        )
    breakdown_fig.update_layout(
        barmode="group",
        xaxis_title="Percentile Score (0–100)",
        yaxis_title=None,
        legend_title_text="Score Factor",
    )
    base_layout(breakdown_fig, height=max(400, 40 * len(breakdown_df)))
    st.plotly_chart(breakdown_fig, use_container_width=True)
