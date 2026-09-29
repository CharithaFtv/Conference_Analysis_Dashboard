"""Figure builders for the Conference Detail tab."""

import plotly.graph_objects as go

from conf_dashboard.charts.theme import CATEGORICAL, base_layout


def build_score_radar(labels: list[str], values: list[float]) -> go.Figure:
    fig = go.Figure(
        go.Scatterpolar(
            r=values + values[:1],
            theta=labels + labels[:1],
            fill="toself",
            line_color=CATEGORICAL[0],
            fillcolor="rgba(42, 120, 214, 0.25)",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], gridcolor="#e1e0d9")),
        showlegend=False,
    )
    return base_layout(fig, height=380)


def build_score_bar(labels: list[str], values: list[float]) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=CATEGORICAL[: len(labels)],
            hovertemplate="%{y}: %{x:.1f}<extra></extra>",
        )
    )
    fig.update_layout(xaxis_title="Percentile (0–100)", yaxis_title=None)
    return base_layout(fig, height=380)
