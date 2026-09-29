"""Figure builders for the Series Trends tab."""

import pandas as pd
import plotly.graph_objects as go

from conf_dashboard.analytics.trends import SERIES_METRICS
from conf_dashboard.charts.theme import CATEGORICAL, base_layout


def build_metrics_line(yearly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for i, (col, label) in enumerate(SERIES_METRICS):
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
    return base_layout(fig, height=420)


def build_conversion_line(yearly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
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
    fig.add_trace(
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
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Conversion Rate",
        yaxis_tickformat=".0%",
        xaxis=dict(dtick=1),
        legend_title_text="Conversion",
    )
    return base_layout(fig, height=380)
