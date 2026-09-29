"""Conference Detail-tab computations."""

import pandas as pd


def clean(val, default="—"):
    return default if val is None or (isinstance(val, float) and val != val) else val


def format_location(row: pd.Series) -> str:
    bits = [clean(x, None) for x in [row["CITY"], row["STATE"], row["COUNTRY"]]]
    return ", ".join(x for x in bits if x) or "—"


def compute_hqt_conversion_rate(row: pd.Series) -> float:
    return (row["HQTS_SOURCED"] / row["COMPANIES_MET"] * 100) if row["COMPANIES_MET"] else 0.0


def option_labels(options_df: pd.DataFrame) -> list[str]:
    return [
        f"{row.CONFERENCE_NAME} ({row.START_DATE:%Y-%m-%d})" for row in options_df.itertuples()
    ]
