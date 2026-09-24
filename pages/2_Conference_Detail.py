import plotly.graph_objects as go
import streamlit as st

from db import run_query
from filters import build_conference_id_subquery, build_where_clause, render_sidebar_filters
from viz import CATEGORICAL, SCORE_COLUMNS, base_layout

st.set_page_config(page_title="Conference Detail | Conference Analysis", page_icon="\U0001F3AF", layout="wide")

st.title("Conference Detail")
st.caption("Drill into a single conference's outcomes and score breakdown.")

filters = render_sidebar_filters()
id_subquery, sub_params = build_conference_id_subquery(filters)

options_df = run_query(
    f"""
    SELECT CONFERENCE_ID, CONFERENCE_NAME, START_DATE
    FROM CONF_ROI_BASE
    WHERE CONFERENCE_ID IN ({id_subquery})
    ORDER BY START_DATE DESC
    """,
    sub_params,
)

if options_df.empty:
    st.warning("No conferences match the current filters.")
    st.stop()

labels = [
    f"{row.CONFERENCE_NAME} ({row.START_DATE:%Y-%m-%d})" for row in options_df.itertuples()
]
selected_label = st.selectbox("Select a conference", options=labels)
selected_id = options_df.iloc[labels.index(selected_label)]["CONFERENCE_ID"]

base_df = run_query(
    "SELECT * FROM CONF_ROI_BASE WHERE CONFERENCE_ID = %(cid)s", {"cid": selected_id}
)
score_df = run_query(
    "SELECT * FROM CONF_ROI_SCORECARD WHERE CONFERENCE_ID = %(cid)s", {"cid": selected_id}
)

if base_df.empty:
    st.warning("No detail row found for this conference.")
    st.stop()

b = base_df.iloc[0]

def _clean(val, default="—"):
    return default if val is None or (isinstance(val, float) and val != val) else val


st.subheader(b["CONFERENCE_NAME"])
loc_bits = [x for x in [b["CITY"], b["STATE"], b["COUNTRY"]] if x]
st.caption(
    f"{b['START_DATE']:%b %d, %Y} – {b['END_DATE']:%b %d, %Y}  |  "
    f"{', '.join(loc_bits) or '—'}  |  {_clean(b['SOURCE_TYPE'])}  |  "
    f"Priority: {_clean(b['PRIORITY'])}  |  Sectors: {_clean(b['SECTORS'])}"
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Companies Met", int(b["COMPANIES_MET"] or 0))
k2.metric("HQTs Sourced", int(b["HQTS_SOURCED"] or 0))
k3.metric("HQTs at HQM+", int(b["HQTS_AT_HQM"] or 0))
k4.metric("Tough→HQM", int(b["TOUGH_TO_CRACK_TO_HQM"] or 0))
hqt_rate = (b["HQTS_SOURCED"] / b["COMPANIES_MET"] * 100) if b["COMPANIES_MET"] else 0.0
k5.metric("HQT Conversion", f"{hqt_rate:.1f}%")

st.divider()

if score_df.empty:
    st.info("This conference has no scorecard row (insufficient data for percentile ranking).")
else:
    s = score_df.iloc[0]
    st.subheader(f"Composite Score: {s['COMPOSITE_SCORE']:.1f} / 100")

    labels6 = [label for _, label in SCORE_COLUMNS]
    values6 = [s[col] for col, _ in SCORE_COLUMNS]

    col1, col2 = st.columns([1, 1])
    with col1:
        radar = go.Figure(
            go.Scatterpolar(
                r=values6 + values6[:1],
                theta=labels6 + labels6[:1],
                fill="toself",
                line_color=CATEGORICAL[0],
                fillcolor="rgba(42, 120, 214, 0.25)",
            )
        )
        radar.update_layout(
            polar=dict(radialaxis=dict(range=[0, 100], gridcolor="#e1e0d9")),
            showlegend=False,
        )
        base_layout(radar, height=380)
        st.plotly_chart(radar, use_container_width=True)

    with col2:
        bar = go.Figure(
            go.Bar(
                x=values6,
                y=labels6,
                orientation="h",
                marker_color=CATEGORICAL[: len(labels6)],
                hovertemplate="%{y}: %{x:.1f}<extra></extra>",
            )
        )
        bar.update_layout(xaxis_title="Percentile (0–100)", yaxis_title=None)
        base_layout(bar, height=380)
        st.plotly_chart(bar, use_container_width=True)

with st.expander("Raw record"):
    st.dataframe(base_df, use_container_width=True, hide_index=True)
    if not score_df.empty:
        st.dataframe(score_df, use_container_width=True, hide_index=True)
