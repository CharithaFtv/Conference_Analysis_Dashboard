import streamlit as st

from conf_dashboard.analytics.detail import clean, compute_hqt_conversion_rate, format_location, option_labels
from conf_dashboard.charts.detail_charts import build_score_bar, build_score_radar
from conf_dashboard.charts.theme import SCORE_COLUMNS
from conf_dashboard.data.detail_repo import get_conference_base, get_conference_options, get_conference_score
from conf_dashboard.filters.model import FilterState
from conf_dashboard.filters.query_builder import build_conference_id_subquery


def render(filters: FilterState) -> None:
    id_subquery, sub_params = build_conference_id_subquery(filters)
    options_df = get_conference_options(id_subquery, sub_params)

    if options_df.empty:
        st.warning("No conferences match the current filters. Try widening your filter selection.")
        return

    ids = options_df["CONFERENCE_ID"].tolist()
    labels = option_labels(options_df)

    preselected = st.session_state.get("selected_conference_id")
    default_index = ids.index(preselected) if preselected in ids else 0

    selected_label = st.selectbox("Select a conference", options=labels, index=default_index)
    selected_id = ids[labels.index(selected_label)]

    base_df = get_conference_base(selected_id)
    score_df = get_conference_score(selected_id)

    if base_df.empty:
        st.warning("No details found for this conference.")
        return

    b = base_df.iloc[0]

    st.subheader(b["CONFERENCE_NAME"])
    st.caption(
        f"{b['START_DATE']:%b %d, %Y} – {b['END_DATE']:%b %d, %Y}  |  "
        f"{format_location(b)}  |  {clean(b['SOURCE_TYPE'])}  |  "
        f"Priority: {clean(b['PRIORITY'])}  |  Sectors: {clean(b['SECTORS'])}"
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Companies Met", int(b["COMPANIES_MET"] or 0))
    k2.metric("HQTs Sourced", int(b["HQTS_SOURCED"] or 0))
    k3.metric("HQTs at HQM+", int(b["HQTS_AT_HQM"] or 0))
    k4.metric("Tough→HQM", int(b["TOUGH_TO_CRACK_TO_HQM"] or 0))
    k5.metric("HQT Conversion", f"{compute_hqt_conversion_rate(b):.1f}%")

    st.divider()

    if score_df.empty:
        st.info("This conference doesn't have enough history yet for a percentile score.")
    else:
        s = score_df.iloc[0]
        st.subheader(f"Score: {s['COMPOSITE_SCORE']:.1f} / 100")

        labels6 = [label for _, label in SCORE_COLUMNS]
        values6 = [s[col] for col, _ in SCORE_COLUMNS]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(build_score_radar(labels6, values6), use_container_width=True)
        with col2:
            st.plotly_chart(build_score_bar(labels6, values6), use_container_width=True)

    with st.expander("All fields for this conference"):
        st.dataframe(base_df, use_container_width=True, hide_index=True)
        if not score_df.empty:
            st.dataframe(score_df, use_container_width=True, hide_index=True)
