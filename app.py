import traceback

import streamlit as st

import detail_tab
import overview_tab
import trends_tab
from filters import render_sidebar_filters

st.set_page_config(
    page_title="Conference Analysis Dashboard",
    page_icon="\U0001F4CA",
    layout="wide",
)

st.title("Conference Analysis Dashboard")
st.caption(
    "See which conferences move companies through the deal pipeline, "
    "so you can weigh outcomes against time invested."
)

try:
    filters = render_sidebar_filters()
except Exception:
    st.error("Something went wrong loading the dashboard. Please refresh the page.")
    st.stop()

def _safe_render(render_fn, filters):
    try:
        render_fn(filters)
    except Exception:
        traceback.print_exc()
        st.error("Something went wrong loading this data. Please try adjusting your filters or refresh.")


tab_overview, tab_detail, tab_trends = st.tabs(
    ["\U0001F4CA Overview", "\U0001F3AF Conference Detail", "\U0001F4C8 Series Trends"]
)

with tab_overview:
    _safe_render(overview_tab.render, filters)
with tab_detail:
    _safe_render(detail_tab.render, filters)
with tab_trends:
    _safe_render(trends_tab.render, filters)
