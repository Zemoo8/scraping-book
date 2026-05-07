"""
database.py — SQLite storage for cleaned book data.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "books.db"
TABLE_NAME = "books"


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def save_books(df: pd.DataFrame) -> None:
    """Save (replace) the books table with the provided DataFrame."""
    if df.empty:
        print("[database] Empty DataFrame — nothing saved.")
        return
    with _get_connection() as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    print(f"[database] Saved {len(df)} books to {DB_PATH}")


def load_books() -> pd.DataFrame:
    """Load all books from the SQLite database. Returns empty DataFrame if not found."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        with _get_connection() as conn:
            df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
        return df
    except Exception as e:
        print(f"[database] Failed to load books: {e}")
        return pd.DataFrame()


def db_exists() -> bool:
    """Return True if the database file exists and has data."""
    if not DB_PATH.exists():
        return False
    try:
        with _get_connection() as conn:
            count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        return count > 0
    except Exception:
        return False
