import streamlit as st

from conf_dashboard.filters.sidebar import render_sidebar_filters
from conf_dashboard.ui import detail_tab, overview_tab, trends_tab
from conf_dashboard.ui.error_boundary import safe_render

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

tab_overview, tab_detail, tab_trends = st.tabs(
    ["\U0001F4CA Overview", "\U0001F3AF Conference Detail", "\U0001F4C8 Series Trends"]
)

with tab_overview:
    safe_render(overview_tab.render, filters)
with tab_detail:
    safe_render(detail_tab.render, filters)
with tab_trends:
    safe_render(trends_tab.render, filters)
