"""Figure builders for the Series Trends tab."""

import pandas as pd
import plotly.graph_objects as go

from conf_dashboard.charts.theme import CATEGORICAL, base_layout


def build_score_trend(history_df: pd.DataFrame, yearly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly_df["CONFERENCE_YEAR"],
            y=yearly_df["COMPOSITE_SCORE"],
            mode="lines+markers",
            name="Yearly Avg Score",
            line=dict(color=CATEGORICAL[0], width=2),
            marker=dict(size=9),
            hovertemplate="%{x}<br>Avg Score: %{y:.1f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=history_df["CONFERENCE_YEAR"],
            y=history_df["COMPOSITE_SCORE"],
            mode="markers",
            name="Individual Conferences",
            marker=dict(size=7, color=CATEGORICAL[1], symbol="circle-open"),
            text=history_df["CONFERENCE_NAME"],
            hovertemplate="%{text}<br>%{x}: %{y:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Composite Score (0–100)",
        yaxis=dict(range=[0, 100]),
        xaxis=dict(dtick=1),
        legend_title_text=None,
    )
    return base_layout(fig, height=420)
