"""Figure builders for the Series Rankings tab."""

import pandas as pd
import plotly.graph_objects as go

from conf_dashboard.charts.theme import SERIES_SCORE_COLORS, SERIES_SCORE_COLUMNS, SEQUENTIAL_BLUE, base_layout


def build_top_performers_bar(top_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=top_df["COMPOSITE_SCORE"],
            y=top_df["CONFERENCE_SERIES"],
            orientation="h",
            marker_color=SEQUENTIAL_BLUE[2],
            hovertemplate="%{y}<br>Score: %{x:.1f}<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Score (0–100)", yaxis_title=None)
    return base_layout(fig, height=max(320, 28 * len(top_df)))


def build_score_breakdown_bar(breakdown_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col, label in SERIES_SCORE_COLUMNS:
        fig.add_trace(
            go.Bar(
                name=label,
                x=breakdown_df[col],
                y=breakdown_df["CONFERENCE_SERIES"],
                orientation="h",
                marker_color=SERIES_SCORE_COLORS[col],
                hovertemplate=f"%{{y}}<br>{label}: %{{x:.1f}}<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="group",
        xaxis_title="Percentile Score (0–100)",
        yaxis_title=None,
        legend_title_text="Score Factor",
    )
    return base_layout(fig, height=max(400, 40 * len(breakdown_df)))
