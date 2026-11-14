"""Read-only database access layer."""
import logging
import os
from contextlib import contextmanager

import pyodbc
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def build_connection_string() -> str:
    parts = [
        f"DRIVER={{{os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server')}}}",
        f"SERVER={os.getenv('DB_SERVER', 'localhost')}",
        f"DATABASE={os.getenv('DB_NAME', 'AdventureWorksDW_Custom')}",
    ]
    if os.getenv("DB_TRUSTED_CONNECTION", "yes").lower() == "yes":
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={os.getenv('DB_USER', '')}")
        parts.append(f"PWD={os.getenv('DB_PASSWORD', '')}")
    if os.getenv("DB_TRUST_CERT", "yes").lower() == "yes":
        parts.append("TrustServerCertificate=yes")
    return ";".join(parts)


@contextmanager
def get_connection():
    conn = pyodbc.connect(build_connection_string(), timeout=10)
    try:
        yield conn
    finally:
        conn.close()


def run_query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a read-only query and return rows as a list of dicts."""
    stripped = sql.strip()
    first_word = stripped.split(None, 1)[0].upper() if stripped else ""
    if first_word not in ("SELECT", "WITH"):
        raise ValueError("Only SELECT queries are allowed.")
    logger.info("Running query: %s", " ".join(stripped.split())[:200])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
