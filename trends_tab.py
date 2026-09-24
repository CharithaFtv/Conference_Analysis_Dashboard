import plotly.graph_objects as go
import streamlit as st

from db import run_query
from filters import FilterState, build_where_clause
from viz import CATEGORICAL, base_layout


def render(filters: FilterState) -> None:
    where_sql, params = build_where_clause(filters, table_alias="")
    where_sql_yoy = where_sql.replace("YEAR(START_DATE)", "CONFERENCE_YEAR")

    series_df = run_query(
        f"""
        SELECT CONFERENCE_SERIES, COUNT(DISTINCT CONFERENCE_YEAR) AS N_YEARS
        FROM CONF_ROI_YOY
        WHERE {where_sql_yoy}
        GROUP BY 1
        HAVING N_YEARS >= 2
        ORDER BY N_YEARS DESC, CONFERENCE_SERIES
        """,
        params,
    )

    if series_df.empty:
        st.warning(
            "No recurring conference series (2+ years of history) match the current filters."
        )
        return

    series_labels = [
        f"{row.CONFERENCE_SERIES} ({row.N_YEARS} yrs)" for row in series_df.itertuples()
    ]
    selected_label = st.selectbox("Select a conference series", options=series_labels)
    selected_series = series_df.iloc[series_labels.index(selected_label)]["CONFERENCE_SERIES"]

    yoy_df = run_query(
        """
        SELECT CONFERENCE_YEAR, CONFERENCE_NAME, START_DATE, CITY, STATE, COUNTRY,
               COMPANIES_MET, HQTS_SOURCED, HQTS_AT_HQM, TOUGH_TO_CRACK_TO_HQM
        FROM CONF_ROI_YOY
        WHERE CONFERENCE_SERIES = %(series)s
        ORDER BY CONFERENCE_YEAR
        """,
        {"series": selected_series},
    )

    st.subheader(selected_series)

    if yoy_df["CONFERENCE_YEAR"].duplicated().any():
        st.caption(
            "Note: some years have multiple logged events for this series "
            "(e.g. a renamed or re-run conference) — charts sum metrics per year; "
            "the detail table below shows each event separately."
        )

    yearly_df = (
        yoy_df.groupby("CONFERENCE_YEAR", as_index=False)[
            ["COMPANIES_MET", "HQTS_SOURCED", "HQTS_AT_HQM", "TOUGH_TO_CRACK_TO_HQM"]
        ]
        .sum()
        .sort_values("CONFERENCE_YEAR")
    )

    metrics = [
        ("COMPANIES_MET", "Companies Met"),
        ("HQTS_SOURCED", "HQTs Sourced"),
        ("HQTS_AT_HQM", "HQTs at HQM+"),
    ]

    fig = go.Figure()
    for i, (col, label) in enumerate(metrics):
        fig.add_trace(
            go.Scatter(
                x=yearly_df["CONFERENCE_YEAR"],
                y=yearly_df[col],
                mode="lines+markers",
                name=label,
                line=dict(color=CATEGORICAL[i], width=2),
                marker=dict(size=8),
                hovertemplate=f"%{{x}}<br>{label}: %{{y}}<extra></extra>",
            )
        )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Count",
        xaxis=dict(dtick=1),
        legend_title_text="Metric",
    )
    base_layout(fig, height=420)
    st.plotly_chart(fig, use_container_width=True)

    yearly_df["HQT_CONVERSION_RATE"] = (
        yearly_df["HQTS_SOURCED"] / yearly_df["COMPANIES_MET"]
    ).where(yearly_df["COMPANIES_MET"] > 0)
    yearly_df["HQM_CONVERSION_RATE"] = (
        yearly_df["HQTS_AT_HQM"] / yearly_df["HQTS_SOURCED"]
    ).where(yearly_df["HQTS_SOURCED"] > 0)

    conv_fig = go.Figure()
    conv_fig.add_trace(
        go.Scatter(
            x=yearly_df["CONFERENCE_YEAR"],
            y=yearly_df["HQT_CONVERSION_RATE"],
            mode="lines+markers",
            name="Companies Met → HQT",
            line=dict(color=CATEGORICAL[0], width=2),
            marker=dict(size=8),
            hovertemplate="%{x}<br>Companies Met → HQT: %{y:.1%}<extra></extra>",
        )
    )
    conv_fig.add_trace(
        go.Scatter(
            x=yearly_df["CONFERENCE_YEAR"],
            y=yearly_df["HQM_CONVERSION_RATE"],
            mode="lines+markers",
            name="HQT → HQM",
            line=dict(color=CATEGORICAL[1], width=2),
            marker=dict(size=8),
            hovertemplate="%{x}<br>HQT → HQM: %{y:.1%}<extra></extra>",
        )
    )
    conv_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Conversion Rate",
        yaxis_tickformat=".0%",
        xaxis=dict(dtick=1),
        legend_title_text="Conversion",
    )
    base_layout(conv_fig, height=380)
    st.plotly_chart(conv_fig, use_container_width=True)

    yoy_df["HQT_CONVERSION_RATE"] = (yoy_df["HQTS_SOURCED"] / yoy_df["COMPANIES_MET"]).where(
        yoy_df["COMPANIES_MET"] > 0
    )
    yoy_df["HQM_CONVERSION_RATE"] = (yoy_df["HQTS_AT_HQM"] / yoy_df["HQTS_SOURCED"]).where(
        yoy_df["HQTS_SOURCED"] > 0
    )

    st.subheader("Year-by-Year Detail")
    st.dataframe(
        yoy_df.rename(
            columns={
                "CONFERENCE_YEAR": "Year",
                "CONFERENCE_NAME": "Conference",
                "START_DATE": "Start Date",
                "COMPANIES_MET": "Companies Met",
                "HQTS_SOURCED": "HQTs Sourced",
                "HQTS_AT_HQM": "HQTs at HQM",
                "TOUGH_TO_CRACK_TO_HQM": "Tough→HQM",
                "HQT_CONVERSION_RATE": "HQT Conv. Rate",
                "HQM_CONVERSION_RATE": "HQM Conv. Rate",
            }
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "HQT Conv. Rate": st.column_config.NumberColumn(format="percent"),
            "HQM Conv. Rate": st.column_config.NumberColumn(format="percent"),
        },
    )
