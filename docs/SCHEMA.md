# Conference ROI Data Context

_Last updated: 2026-09-29. Source of truth for table/view schemas backing this dashboard. Update this file whenever the underlying Snowflake objects change, and check `conf_dashboard/data/*_repo.py` for queries that may need to follow._

## Overview
This workspace contains a Conference ROI analytics system built on Snowflake. It tracks the performance of conferences attended by the deal sourcing team (2019+) — measuring how many companies were met (including AI-extracted counts from meeting notes), how many became HQTs (High Quality Targets), how many progressed to Top Prospect stage, and which conferences served as the catalyst for new company relationships that later reached HQM+.

## Database & Schema
- **Database**: `DEV_CHARITHA`
- **Schema**: `SILVER`
- **Role**: `DEV_ROLE`
- **Warehouse**: `DEV_S_WH` or `DEV_XS_WH`

Each object exists as both a **table** (materialized, fast reads) and a **view** (prefixed `VW_`, self-documenting via `GET_DDL`).

---

## Tables & Schemas

### 1. CONF_ROI_BASE (View: VW_CONF_ROI_BASE)
**One row per attended conference.** The core table everything else builds from.

| Column | Type | Description |
|--------|------|-------------|
| CONFERENCE_ID | VARCHAR | DealCloud conference ID (primary key) |
| CONFERENCE_NAME | VARCHAR | Conference name from DealCloud |
| START_DATE | DATE | Conference start date |
| END_DATE | DATE | Conference end date |
| CITY | VARCHAR | Conference city |
| STATE | VARCHAR | Conference state |
| COUNTRY | VARCHAR | Conference country |
| SOURCE_TYPE | VARCHAR | Type: Industry Conference, Investment Banking Conference, etc. |
| SECTORS | VARCHAR | Comma-separated sector names (e.g., "ETS, FTS, VS") |
| DC_NUM_OF_HQTS | NUMBER | DealCloud's HQT count (includes non-approved) |
| COMPANIES_MET | NUMBER | Distinct companies the team actually met (from logged activities) |
| HQTS_SOURCED | NUMBER | Approved HQTs linked to this conference |
| HQTS_AT_HQM | NUMBER | Of those HQTs, how many reached HQM or above |
| HQTS_AT_TOP_PROSPECT | NUMBER | Of those approved HQTs, how many reached Top Prospect interest level |
| TOUGH_TO_CRACK_TO_HQM | NUMBER | Companies met whose FIRST_ACTIVITY_DATE >= conference date and who later reached HQM/Top Prospect/Portfolio Company (conference was the catalyst for the relationship) |

**Filters applied**: STATUS = 'Attended', YEAR(START_DATE) >= 2019, SOURCE_TYPE != 'Buyers Guide'.

**Key join logic**:
- COMPANIES_MET: joins BRIDGE_ACTIVITY_SOURCE + BRIDGE_ACTIVITY_COMPANY on DC_CONFERENCE_ID (ID-based). Counts distinct COMPANY_ID from actual meetings, not exhibitor lists.
- HQTS_SOURCED: joins FACT_HQT_ENTRY on CONFERENCE_CITY_VISIT_THEMATIC_WORK = CONFERENCE_NAME (name-based — no conference ID exists in FACT_HQT_ENTRY). Filters to STATUS = 'Approved'.
- TOUGH_TO_CRACK_TO_HQM: joins DC_COMPANY on FIRST_ACTIVITY_DATE >= conference START_DATE (conference was the first-ever touchpoint), then checks DC_COMPANY_SCD__INTEREST_AND_COV_EOD for reaching 'HQM'/'Top Prospect'/'Portfolio Company' after the conference. No before-state check — the FIRST_ACTIVITY_DATE filter already proves the company was new to the firm.

### 2. CONF_SERIES_MAP (View: VW_CONF_SERIES_MAP)
**Maps each conference to a canonical series name.** Normalizes name variations across years.

| Column | Type | Description |
|--------|------|-------------|
| ID | VARCHAR | DealCloud conference ID |
| NAME | VARCHAR | Original conference name |
| DERIVED_SERIES | VARCHAR | Name with trailing year stripped |
| CANONICAL_SERIES | VARCHAR | Normalized series name |

Mappings were verified via DC_CONFERENCE.SOURCE_SERIES and PRIOR_YEAR_CONFERENCE chains — not just name similarity. Examples: "Money2020 USA", "Money 20/20 USA", "M2020 USA" all map to "Money2020 USA".

### 3. CONF_ROI_YOY (View: VW_CONF_ROI_YOY)
**One row per conference with series and year.** For YoY trend analysis and plotting.

| Column | Type | Description |
|--------|------|-------------|
| CONFERENCE_SERIES | VARCHAR | Canonical series name (from CONF_SERIES_MAP) |
| CONFERENCE_YEAR | NUMBER | Year of the conference |
| CONFERENCE_NAME | VARCHAR | Original conference name |
| START_DATE | DATE | Conference start date |
| END_DATE | DATE | Conference end date |
| CITY | VARCHAR | Conference city |
| STATE | VARCHAR | Conference state |
| COUNTRY | VARCHAR | Conference country |
| SOURCE_TYPE | VARCHAR | Conference type |
| SECTORS | VARCHAR | Comma-separated sectors |
| COMPANIES_MET | NUMBER | Distinct companies met (from activity bridges) |
| CONSOLIDATED_COMPANIES_MET | NUMBER | MAX(AI_COMPANIES_COUNT, COMPANIES_MET) if in CONF_ACTIVITY_NOTES; else COMPANIES_MET |
| HQTS_SOURCED | NUMBER | Approved HQTs sourced |
| HQTS_AT_HQM | NUMBER | HQTs at HQM or above |
| HQTS_AT_TOP_PROSPECT | NUMBER | Approved HQTs that reached Top Prospect |
| TOUGH_TO_CRACK_TO_HQM | NUMBER | Conference-catalyst companies that reached HQM+ |

### 5. CONF_ACTIVITY_NOTES (View: VW_CONF_ACTIVITY_NOTES)
**One row per conference with aggregated meeting notes and AI-extracted companies.** Built from FACT_ACTIVITY → BRIDGE_ACTIVITY_SOURCE → DC_CONFERENCE, filtered to activity types Meeting and Conference Attended only.

| Column | Type | Description |
|--------|------|-------------|
| CONFERENCE_ID | VARCHAR | DealCloud conference ID |
| CONFERENCE_NAME | VARCHAR | Conference name |
| CONFERENCE_SERIES | VARCHAR | Canonical series name (from CONF_SERIES_MAP) |
| CONFERENCE_START_DATE | DATE | Conference start date |
| CONFERENCE_END_DATE | DATE | Conference end date |
| SOURCE_TYPE | VARCHAR | Conference type |
| CONFERENCE_CITY | VARCHAR | Conference city |
| CONFERENCE_STATE | VARCHAR | Conference state |
| CONFERENCE_COUNTRY | VARCHAR | Conference country |
| PRIORITY | VARCHAR | Internal priority |
| COMPANIES_MET | NUMBER | Distinct companies met (from CONF_ROI_BASE) |
| BODY_FORMATTED_ARRAY | ARRAY | All meeting notes for this conference aggregated into an array |
| AI_COMPANIES_EXTRACTED | ARRAY | Company names extracted from meeting notes via AI_COMPLETE (llama3.1-70b) with structured output |
| AI_COMPANIES_COUNT | NUMBER | Count of companies in AI_COMPANIES_EXTRACTED |

**Filters applied**: STATUS = 'Attended', YEAR(START_DATE) >= 2019, SOURCE_TYPE != 'Buyers Guide', ACTIVITY_TYPE IN ('Meeting', 'Conference Attended'), BODY_FORMATTED IS NOT NULL.

**AI extraction prompt**: Splits notes into per-company sections, identifies company names from headings or text, excludes people names / conference names / fund names / shorthand (KIT, TBD, etc.), and returns a structured JSON array.

**Coverage**: 147 conferences (of 567 total attended) have meeting notes linked via BRIDGE_ACTIVITY_SOURCE. 139 of those produced AI-extracted company names.

### 6. CONF_ROI_SCORECARD (View: VW_CONF_ROI_SCORECARD)
**Conference scoring across 5 factors.** Each score is a 0–100 percentile rank.

| Column | Type | Description |
|--------|------|-------------|
| CONFERENCE_ID | VARCHAR | DealCloud conference ID |
| CONFERENCE_NAME | VARCHAR | Conference name |
| START_DATE | DATE | Conference start date |
| SECTORS | VARCHAR | Comma-separated sectors |
| CONSOLIDATED_COMPANIES_MET | NUMBER | Best-available companies met count |
| COMPANIES_MET | NUMBER | Activity-bridge companies met (for comparison) |
| HQTS_SOURCED | NUMBER | Approved HQTs sourced |
| HQTS_AT_HQM | NUMBER | HQTs at HQM or above |
| HQTS_AT_TOP_PROSPECT | NUMBER | Approved HQTs that reached Top Prospect |
| TOUGH_TO_CRACK_TO_HQM | NUMBER | Conference-catalyst companies that reached HQM+ |
| SCORE_COMPANIES_MET | FLOAT | Percentile: consolidated companies met (weight: 25%) |
| SCORE_HQTS_SOURCED | FLOAT | Percentile: approved HQTs sourced (weight: 25%) |
| SCORE_HQTS_TOP_PROSPECT | FLOAT | Percentile: HQTs → Top Prospect (weight: 15%) |
| SCORE_YOY_SERIES | FLOAT | Percentile: years attended × avg HQTs/year (weight: 10%) |
| SCORE_TOUGH_TO_CRACK | FLOAT | Percentile: conference-catalyst → HQM+ (weight: 25%) |
| COMPOSITE_SCORE | FLOAT | Weighted average of all 5 scores (0–100) |

### 7. CONF_SERIES_SCORECARD
**One row per conference series.** Scores series holistically with era-weighted metrics (2023-2026 weighted 65%, 2019-2022 weighted 35%) and a trend indicator.

| Column | Type | Description |
|--------|------|-------------|
| CONFERENCE_SERIES | VARCHAR | Canonical series name |
| TOTAL_YEARS_ATTENDED | NUMBER | Distinct years this series was attended |
| TOTAL_CONFERENCES | NUMBER | Total conferences in this series |
| SECTORS | VARCHAR | Sectors covered by this series |
| ERA_WEIGHTED_COMPANIES_MET | FLOAT | Era-weighted avg consolidated companies met per year |
| ERA_WEIGHTED_HQTS_SOURCED | FLOAT | Era-weighted avg approved HQTs per year |
| ERA_WEIGHTED_HQTS_TOP_PROSPECT | FLOAT | Era-weighted avg HQTs reaching Top Prospect |
| ERA_WEIGHTED_TOUGH_TO_CRACK | FLOAT | Era-weighted avg conference-catalyst → HQM+ conversions |
| YOY_CONSISTENCY_METRIC | FLOAT | YEARS_ATTENDED × era-weighted avg HQTs (rewards consistency) |
| SCORE_COMPANIES_MET | FLOAT | Percentile: era-weighted consolidated companies met (weight: 25%) |
| SCORE_HQTS_SOURCED | FLOAT | Percentile: era-weighted HQTs sourced (weight: 25%) |
| SCORE_HQTS_TOP_PROSPECT | FLOAT | Percentile: era-weighted HQTs → Top Prospect (weight: 15%) |
| SCORE_YOY_CONSISTENCY | FLOAT | Percentile: YoY consistency metric (weight: 10%) |
| SCORE_TOUGH_TO_CRACK | FLOAT | Percentile: era-weighted conference-catalyst conversions (weight: 25%) |
| COMPOSITE_SCORE | FLOAT | Weighted average of all 5 scores (0–100) |
| HQT_TREND_SLOPE | FLOAT | Linear regression slope of HQTS_SOURCED across years (2019-2026) |
| TREND | VARCHAR | Increasing (slope > 0.5), Declining (slope < -0.5), Flat, New, or Inactive |

**Era weighting**: Metrics are averaged per era then blended — early era (2019-2022) × 0.35 + recent era (2023-2026) × 0.65. Series only in one era use that era's values unblended.

**Trend**: Uses `REGR_SLOPE(HQTS_SOURCED, CONFERENCE_YEAR)` across the full 2019-2026 range. Series with ≤1 year get "New" (recent only), "Inactive" (early only), or "Insufficient Data".

---

## Interest Level Funnel (company progression)
```
Sourcing Pool → Suspect → Tough to Crack → HQM → Top Prospect → Portfolio Company
                                                    (also: Uninvestable, Acquired/OoB/IPO)
```

## Key Data Caveats
1. **COMPANIES_MET** comes from activity bridges (actual meetings logged in DealCloud), NOT from exhibitor/attendee lists.
2. **CONSOLIDATED_COMPANIES_MET** = MAX(AI_COMPANIES_COUNT, COMPANIES_MET) for conferences with meeting notes in CONF_ACTIVITY_NOTES; plain COMPANIES_MET otherwise. This is the primary companies-met metric used in scoring.
3. **HQTS_SOURCED** joins on conference NAME (string match), not ID — FACT_HQT_ENTRY has no conference ID column. Verified: no actual conference name mismatches causing data loss. Unmatched entries are city visits or thematic work.
4. **TOUGH_TO_CRACK_TO_HQM** counts companies whose FIRST_ACTIVITY_DATE >= conference date and who later reached HQM+. The conference was the first-ever engagement with the firm.
5. **SECTORS** values are abbreviations: ETS (Enterprise Tech & Services), FTS (Financial Tech & Services), VS (Vertical Software), HC (Healthcare).
6. **DC_NUM_OF_HQTS** (from DealCloud) includes non-approved HQTs. **HQTS_SOURCED** only counts approved.
7. **AI_COMPANIES_EXTRACTED** uses `llama3.1-70b` with structured output (`response_format => TYPE OBJECT(companies ARRAY(STRING))`). Results are non-deterministic; re-running AI_COMPLETE may produce slightly different extractions.

## Source Tables (in PROD.SILVER)
- `DC_CONFERENCE` — conference dimension
- `FACT_ACTIVITY` — activity records (meetings, calls, emails) with BODY_FORMATTED notes
- `FACT_HQT_ENTRY` — HQT entries with company, interest level, conference link
- `BRIDGE_ACTIVITY_SOURCE` — links activities → conferences (by ID)
- `BRIDGE_ACTIVITY_COMPANY` — links activities → companies (by ID)
- `DC_COMPANY_SCD__INTEREST_AND_COV_EOD` — daily interest level snapshots
- `DC_COMPANY` — company dimension (FIRST_ACTIVITY_DATE used for conference impact check)
- `DIM_COMPANY` — company dimension (maps surrogate ID ↔ DealCloud ID via IDS:"DEALCLOUD")
- `DIM_INTEREST_LEVEL` — interest level reference data

## SQL Files in Workspace
- `conf_roi_base.sql` — creates CONF_ROI_BASE table
- `conf_roi_yoy.sql` — creates CONF_SERIES_MAP + CONF_ROI_YOY tables
- `conf_roi_scorecard.sql` — creates CONF_ROI_SCORECARD table
- `conf_series_scorecard.sql` — creates CONF_SERIES_SCORECARD table
- `conf_activity_notes.sql` — creates CONF_ACTIVITY_NOTES table + view (includes AI_COMPLETE extraction)

Run order: conf_roi_base.sql → conf_activity_notes.sql → conf_roi_yoy.sql → conf_roi_scorecard.sql → conf_series_scorecard.sql

## Example Queries

### Top conferences by composite score
```sql
SELECT CONFERENCE_NAME, COMPOSITE_SCORE, CONSOLIDATED_COMPANIES_MET, HQTS_SOURCED, HQTS_AT_TOP_PROSPECT
FROM DEV_CHARITHA.SILVER.CONF_ROI_SCORECARD
ORDER BY COMPOSITE_SCORE DESC
LIMIT 20;
```

### YoY trend for a series
```sql
SELECT CONFERENCE_SERIES, CONFERENCE_YEAR, CONSOLIDATED_COMPANIES_MET, HQTS_SOURCED, HQTS_AT_TOP_PROSPECT
FROM DEV_CHARITHA.SILVER.CONF_ROI_YOY
WHERE CONFERENCE_SERIES = 'Money2020 USA'
ORDER BY CONFERENCE_YEAR;
```

### Top series by composite score with trend
```sql
SELECT CONFERENCE_SERIES, COMPOSITE_SCORE, TREND, TOTAL_YEARS_ATTENDED,
       ERA_WEIGHTED_HQTS_SOURCED, ERA_WEIGHTED_TOUGH_TO_CRACK
FROM DEV_CHARITHA.SILVER.CONF_SERIES_SCORECARD
ORDER BY COMPOSITE_SCORE DESC
LIMIT 20;
```

### Series that consistently produce HQTs
```sql
SELECT CONFERENCE_SERIES, COUNT(DISTINCT CONFERENCE_YEAR) AS YEARS,
       AVG(HQTS_SOURCED) AS AVG_HQTS, SUM(HQTS_SOURCED) AS TOTAL_HQTS
FROM DEV_CHARITHA.SILVER.CONF_ROI_YOY
GROUP BY CONFERENCE_SERIES
HAVING COUNT(DISTINCT CONFERENCE_YEAR) >= 2 AND AVG(HQTS_SOURCED) > 0
ORDER BY AVG_HQTS DESC;
```

---

## App structure and schema alignment (as of 2026-09-29)

The dashboard now has three tabs, reflecting a shift in focus from individual conferences to conference series as the primary lens:

1. **Series Rankings** (main tab) — `conf_dashboard/ui/series_tab.py`, backed by `CONF_SERIES_SCORECARD` (`conf_dashboard/data/series_repo.py`). Ranks series by `COMPOSITE_SCORE`, shows the 5-factor era-weighted breakdown and `TREND`.
2. **Individual Conferences** (renamed from the old "Overview") — `conf_dashboard/ui/conferences_tab.py`, backed by `CONF_ROI_BASE` + `CONF_ROI_SCORECARD` (`conf_dashboard/data/conferences_repo.py`).
3. **Series Trends** — `conf_dashboard/ui/trends_tab.py`, backed by `conf_dashboard/data/trends_repo.py`, which now joins `CONF_ROI_SCORECARD` through `CONF_SERIES_MAP` to plot each conference's own `COMPOSITE_SCORE` by year (average per year + individual events), instead of raw yearly counts from `CONF_ROI_YOY`.

The "Conference Detail" tab was removed; the old previously-flagged divergence (stale 6-factor score columns, `HQT_CONVERSION_RATE`/`HQM_CONVERSION_RATE` that no longer exist) was fixed as part of this pass:
- `charts/theme.py` now defines `CONFERENCE_SCORE_COLUMNS` and `SERIES_SCORE_COLUMNS` matching the current 5-factor schemas of `CONF_ROI_SCORECARD` and `CONF_SERIES_SCORECARD` respectively.
- Conversion rates (`HQT_CONVERSION_RATE`, `HQM_CONVERSION_RATE`) are now computed in `analytics/conferences.py` from raw counts (`HQTS_SOURCED`, `CONSOLIDATED_COMPANIES_MET`/`COMPANIES_MET`, `HQTS_AT_HQM`) rather than queried as scorecard columns.
- `CONSOLIDATED_COMPANIES_MET` and `HQTS_AT_TOP_PROSPECT` are now used in the Individual Conferences and Series Trends tabs.

**Still not wired up**: `CONF_ACTIVITY_NOTES` (AI-extracted companies from meeting notes) has no repo/UI yet. Table names in the repos remain unqualified, relying on the Snowflake connection's default database/schema (via `.env`) matching `DEV_CHARITHA.SILVER`.

**Removed**: the `Priority` sidebar filter and all `PRIORITY` column references were dropped from the app (`filters/model.py`, `filters/sidebar.py`, `filters/query_builder.py`, `data/conferences_repo.py`, `analytics/conferences.py`) — `CONF_ROI_BASE` isn't documented as having that column above (only `CONF_ACTIVITY_NOTES` does), and it was an unverified assumption in the code.
