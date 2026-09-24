import os
import time

import pandas as pd
import snowflake.connector
import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
    "SNOWFLAKE_PRIVATE_KEY_PATH",
]


def _load_private_key(path: str, passphrase: str | None) -> bytes:
    with open(path, "rb") as f:
        p_key = serialization.load_pem_private_key(
            f.read(),
            password=passphrase.encode() if passphrase else None,
            backend=default_backend(),
        )
    return p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@st.cache_resource(show_spinner=False)
def get_connection():
    missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your values."
        )

    passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE") or None
    private_key_der = _load_private_key(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"], passphrase)

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        private_key=private_key_der,
    )


@st.cache_data(ttl=60, show_spinner=False)
def run_query(sql: str, params: tuple | dict | None = None) -> pd.DataFrame:
    last_exc: Exception | None = None
    for attempt in range(3):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetch_pandas_all()
        except Exception as exc:
            last_exc = exc
            get_connection.clear()
            time.sleep(0.5 * (attempt + 1))
        finally:
            cur.close()
    raise last_exc
