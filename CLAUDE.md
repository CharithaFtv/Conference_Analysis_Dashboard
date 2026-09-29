# Conference Analysis Dashboard

Streamlit app that scores and visualizes conference ROI for the deal sourcing team, backed by Snowflake. Primary focus is **conference series** rankings, not individual conferences.

## Data schema
Full table/view definitions, join logic, caveats, and example queries: **[docs/SCHEMA.md](docs/SCHEMA.md)**.

Read it before touching anything in `conf_dashboard/data/` (queries) or `conf_dashboard/analytics/` (score/column names) — those modules assume specific column names from that schema. `docs/SCHEMA.md` has an "App structure and schema alignment" section noting what's wired up vs. not, and one remaining unverified assumption (`PRIORITY` column) — check it before assuming a repo function matches the live database.

## Tabs (in display order)
1. **Series Rankings** (`ui/series_tab.py`) — the main tab. Ranks conference series by composite score, from `CONF_SERIES_SCORECARD`.
2. **Individual Conferences** (`ui/conferences_tab.py`) — per-conference detail, from `CONF_ROI_BASE` + `CONF_ROI_SCORECARD`.
3. **Series Trends** (`ui/trends_tab.py`) — a series' composite score by year, joining `CONF_ROI_SCORECARD` through `CONF_SERIES_MAP`.

There is no "Conference Detail" tab (removed) and no drill-down between tabs beyond `st.session_state["selected_conference_series"]`, which Series Rankings sets and Series Trends reads to preselect its dropdown.

## Code layout
- `app.py` — thin Streamlit entrypoint.
- `conf_dashboard/data/` — Snowflake connection (`db.py`) + one repository module per tab, each owning that tab's SQL.
- `conf_dashboard/filters/` — filter state, pure SQL WHERE-clause builder (`build_where_clause` for conference-level tables, `build_series_subquery` for series-level tables), sidebar widget.
- `conf_dashboard/analytics/` — pure business logic (ranking, rates, aggregation), no Streamlit/SQL imports.
- `conf_dashboard/charts/` — theme constants (`CONFERENCE_SCORE_COLUMNS` vs `SERIES_SCORE_COLUMNS` — don't conflate them, the two scorecards have different 5th factors) + pure Plotly figure builders.
- `conf_dashboard/ui/` — thin per-tab rendering that wires data → analytics → charts together.

When the schema changes, update `docs/SCHEMA.md` first, then the affected `data/*_repo.py` queries, then `analytics/` if score/column semantics changed.
