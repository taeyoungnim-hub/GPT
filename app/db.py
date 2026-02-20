import sqlite3
from pathlib import Path

DB_PATH = Path("data.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    published_at TEXT NOT NULL,
    region TEXT,
    category TEXT,
    summary TEXT,
    status TEXT
);

CREATE TABLE IF NOT EXISTS validations (
    document_id INTEGER PRIMARY KEY,
    score REAL,
    rationale TEXT,
    demand_signal INTEGER,
    policy_signal INTEGER,
    transit_signal INTEGER,
    stakeholder_signal INTEGER,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);
"""


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
