"""Shared render-failure guard so one tab's error can't break the others."""

import traceback
from typing import Callable

import streamlit as st

from conf_dashboard.filters.model import FilterState


def safe_render(render_fn: Callable[[FilterState], None], filters: FilterState) -> None:
    try:
        render_fn(filters)
    except Exception:
        traceback.print_exc()
        st.error("Something went wrong loading this data. Please try adjusting your filters or refresh.")
