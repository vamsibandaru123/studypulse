"""Database helpers for StudyPulse (SQLite)."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "studypulse.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables from schema.sql if they don't exist."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text())


def add_study_log(log_date, subject, hours, sleep):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO study_log (log_date, subject, hours_studied, sleep_hours) "
            "VALUES (?, ?, ?, ?)",
            (log_date, subject.strip().title(), hours, sleep),
        )


def add_test_score(test_date, subject, marks):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO test_scores (test_date, subject, marks) VALUES (?, ?, ?)",
            (test_date, subject.strip().title(), marks),
        )


def run_query(sql, params=()):
    """Run a SELECT query and return (column_names, rows)."""
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return cols, cur.fetchall()
