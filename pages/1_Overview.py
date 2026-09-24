import plotly.graph_objects as go
import streamlit as st

from db import run_query
from filters import build_conference_id_subquery, build_where_clause, render_sidebar_filters
from viz import SCORE_COLORS, SCORE_COLUMNS, SEQUENTIAL_BLUE, base_layout

st.set_page_config(page_title="Overview | Conference Analysis", page_icon="\U0001F4CA", layout="wide")

st.title("Overview")
st.caption("Overall conference performance and composite scores across attended conferences.")

filters = render_sidebar_filters()
where_sql, base_params = build_where_clause(filters)
id_subquery, sub_params = build_conference_id_subquery(filters)

kpi_df = run_query(
    f"""
    SELECT
        COUNT(*) AS TOTAL_CONFERENCES,
        SUM(COMPANIES_MET) AS TOTAL_COMPANIES_MET,
        SUM(HQTS_SOURCED) AS TOTAL_HQTS_SOURCED,
        SUM(HQTS_AT_HQM) AS TOTAL_HQTS_AT_HQM
    FROM CONF_ROI_BASE
    WHERE {where_sql}
    """,
    base_params,
)

row = kpi_df.iloc[0]
total_conferences = int(row["TOTAL_CONFERENCES"] or 0)
total_companies_met = int(row["TOTAL_COMPANIES_MET"] or 0)
total_hqts = int(row["TOTAL_HQTS_SOURCED"] or 0)
total_hqm = int(row["TOTAL_HQTS_AT_HQM"] or 0)
hqm_rate = (total_hqm / total_hqts * 100) if total_hqts else 0.0

if total_conferences == 0:
    st.warning("No conferences match the current filters.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Conferences", f"{total_conferences:,}")
k2.metric("Companies Met", f"{total_companies_met:,}")
k3.metric("HQTs Sourced", f"{total_hqts:,}")
k4.metric("HQT → HQM Rate", f"{hqm_rate:.1f}%")

st.divider()

scorecard_df = run_query(
    f"""
    SELECT CONFERENCE_ID, CONFERENCE_NAME, START_DATE, SECTORS, PRIORITY,
           COMPANIES_MET, HQTS_SOURCED, HQTS_AT_HQM, TOUGH_TO_CRACK_TO_HQM,
           HQT_CONVERSION_RATE, HQM_CONVERSION_RATE,
           SCORE_COMPANIES_MET, SCORE_HQT_CONVERSION, SCORE_HQM_POTENTIAL,
           SCORE_YOY_SERIES, SCORE_SECTOR_IMPACT, SCORE_TOUGH_TO_CRACK,
           COMPOSITE_SCORE
    FROM CONF_ROI_SCORECARD
    WHERE CONFERENCE_ID IN ({id_subquery})
    ORDER BY COMPOSITE_SCORE DESC
    """,
    sub_params,
)

if scorecard_df.empty:
    st.warning("No scorecard rows for the current filters.")
    st.stop()

st.subheader("Top Conferences by Composite Score")
top_n = min(15, len(scorecard_df))
top_df = scorecard_df.head(top_n).sort_values("COMPOSITE_SCORE")

bar_fig = go.Figure(
    go.Bar(
        x=top_df["COMPOSITE_SCORE"],
        y=top_df["CONFERENCE_NAME"],
        orientation="h",
        marker_color=SEQUENTIAL_BLUE[2],
        hovertemplate="%{y}<br>Composite score: %{x:.1f}<extra></extra>",
    )
)
bar_fig.update_layout(xaxis_title="Composite Score (0–100)", yaxis_title=None)
base_layout(bar_fig, height=max(320, 28 * top_n))
st.plotly_chart(bar_fig, use_container_width=True)

st.subheader("Score Breakdown — Top 10")
breakdown_df = scorecard_df.head(10).sort_values("COMPOSITE_SCORE")
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

st.subheader("Full Scorecard")
st.dataframe(
    scorecard_df.rename(
        columns={
            "CONFERENCE_NAME": "Conference",
            "START_DATE": "Start Date",
            "SECTORS": "Sectors",
            "PRIORITY": "Priority",
            "COMPANIES_MET": "Companies Met",
            "HQTS_SOURCED": "HQTs Sourced",
            "HQTS_AT_HQM": "HQTs at HQM",
            "TOUGH_TO_CRACK_TO_HQM": "Tough→HQM",
            "HQT_CONVERSION_RATE": "HQT Conv. Rate",
            "HQM_CONVERSION_RATE": "HQM Conv. Rate",
            "COMPOSITE_SCORE": "Composite Score",
        }
    ).drop(columns=["CONFERENCE_ID"]),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Composite Score": st.column_config.ProgressColumn(
            "Composite Score", min_value=0, max_value=100, format="%.1f"
        ),
        "HQT Conv. Rate": st.column_config.NumberColumn(format="%.2f"),
        "HQM Conv. Rate": st.column_config.NumberColumn(format="%.2f"),
    },
)
