-- StudyPulse database schema (SQLite)

CREATE TABLE IF NOT EXISTS study_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date      TEXT    NOT NULL,          -- format: YYYY-MM-DD
    subject       TEXT    NOT NULL,
    hours_studied REAL    NOT NULL CHECK (hours_studied >= 0),
    sleep_hours   REAL    NOT NULL CHECK (sleep_hours >= 0)
);

CREATE TABLE IF NOT EXISTS test_scores (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    test_date  TEXT    NOT NULL,             -- format: YYYY-MM-DD
    subject    TEXT    NOT NULL,
    marks      REAL    NOT NULL CHECK (marks BETWEEN 0 AND 100)
);
