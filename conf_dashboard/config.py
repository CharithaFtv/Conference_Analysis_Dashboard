"""Environment configuration and table-name constants shared across the app."""

import os

from dotenv import load_dotenv

load_dotenv()

_ca_bundle = os.getenv("SNOWFLAKE_CA_BUNDLE")
if _ca_bundle:
    os.environ.setdefault("REQUESTS_CA_BUNDLE", _ca_bundle)
    os.environ.setdefault("SSL_CERT_FILE", _ca_bundle)

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_PRIVATE_KEY_PATH",
]

BASE_TABLE = "CONF_ROI_BASE"
SCORECARD_TABLE = "CONF_ROI_SCORECARD"
YOY_TABLE = "CONF_ROI_YOY"
SERIES_MAP_TABLE = "CONF_SERIES_MAP"
SERIES_SCORECARD_TABLE = "CONF_SERIES_SCORECARD"

DEALCLOUD_BASE_URL = "https://ftvcapital.dealcloud.com/portal/pages/12167/reports/12170/entries/"
