CATEGORICAL = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]

SEQUENTIAL_BLUE = ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#104281"]

STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
SURFACE = "#fcfcfb"

SCORE_COLUMNS = [
    ("SCORE_COMPANIES_MET", "Companies Met"),
    ("SCORE_HQT_CONVERSION", "HQT Conversion"),
    ("SCORE_HQM_POTENTIAL", "HQM Potential"),
    ("SCORE_YOY_SERIES", "YoY Series"),
    ("SCORE_SECTOR_IMPACT", "Sector Impact"),
    ("SCORE_TOUGH_TO_CRACK", "Tough to Crack"),
]

SCORE_COLORS = dict(zip([c for c, _ in SCORE_COLUMNS], CATEGORICAL))


def base_layout(fig, height: int | None = None):
    fig.update_layout(
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", color=INK_PRIMARY),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE, color=INK_MUTED)
    fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE, color=INK_MUTED)
    if height:
        fig.update_layout(height=height)
    return fig
