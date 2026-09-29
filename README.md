# Conference Analysis Dashboard

A Streamlit dashboard for understanding which conferences the deal sourcing team benefits from, and how — which conferences move companies through the deal pipeline (Companies Met → HQTs Sourced → Top Prospect / HQM+), so associates can weigh outcomes against time invested. Backed by Snowflake.

The primary lens is **conference series** (a conference attended repeatedly across years, e.g. "Money2020 USA"), not one-off individual conferences.

## Tabs

1. **🏆 Series Rankings** (main tab) — ranks conference series by composite score; shows actual totals aggregated across the whole series (companies met, HQTs sourced, etc.) and a trend indicator (Increasing/Declining/Flat/New/Inactive).
2. **📋 Individual Conferences** — per-conference detail and scoring; conference names link directly to their DealCloud entry.
3. **📈 Series Trends** — a series' composite score plotted year over year, with a year-by-year detail table (also DealCloud-linked).

Selecting a series in Series Rankings preselects it in Series Trends.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your Snowflake credentials (account, user, role, warehouse, database/schema, and the path to your RSA private key).
3. If you hit `certificate verify failed` errors on larger queries (common with corporate security software on macOS), run `scripts/build_ca_bundle.sh` once and set `SNOWFLAKE_CA_BUNDLE` in `.env` to the path it prints.
4. Run the app:
   ```
   streamlit run app.py
   ```

## Project layout

See **[CLAUDE.md](CLAUDE.md)** for the code layout (data access, filters, analytics, charts, UI layers) and **[docs/SCHEMA.md](docs/SCHEMA.md)** for the full Snowflake schema this dashboard is built on — table/view definitions, join logic, caveats, and what's changed recently.
