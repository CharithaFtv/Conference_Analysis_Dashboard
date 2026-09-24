import streamlit as st

from db import run_query
from filters import build_where_clause, render_sidebar_filters

st.set_page_config(
    page_title="Conference Analysis Dashboard",
    page_icon="\U0001F4CA",
    layout="wide",
)

st.title("Conference Analysis Dashboard")
st.caption(
    "Live view into which conferences move companies through the deal pipeline, "
    "so associates can weigh outcomes against time invested."
)

try:
    filters = render_sidebar_filters()
except Exception as exc:
    st.error(f"Snowflake connection failed while loading filters: {exc}")
    st.stop()

where_sql, params = build_where_clause(filters)

try:
    df = run_query(
        f"SELECT COUNT(*) AS N FROM CONF_ROI_BASE WHERE {where_sql}", params
    )
    st.success(f"Connected to Snowflake — {int(df.iloc[0]['N'])} conferences match current filters.")
except Exception as exc:
    st.error(f"Query failed: {exc}")
    st.stop()

st.info("Overview, per-conference, and series-trend pages land in the next steps.")
