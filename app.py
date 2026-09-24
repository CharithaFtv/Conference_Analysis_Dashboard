import streamlit as st

from db import run_query

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

with st.sidebar:
    st.header("Filters")
    st.caption("Global filters land here in step 2.")

try:
    df = run_query("SELECT CURRENT_VERSION() AS VERSION")
    st.success(f"Connected to Snowflake (version {df.iloc[0]['VERSION']}).")
except Exception as exc:
    st.error(f"Snowflake connection failed: {exc}")
    st.stop()

st.info("Overview, per-conference, and series-trend pages land in the next steps.")
