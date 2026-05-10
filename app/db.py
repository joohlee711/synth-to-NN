import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "synth.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS racks (
    rack_id     INTEGER PRIMARY KEY,
    format      TEXT,
    name        TEXT,
    raw_json    TEXT NOT NULL,
    fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS modules (
    module_id   INTEGER PRIMARY KEY,
    slug        TEXT,
    name        TEXT,
    vendor      TEXT,
    hp          INTEGER,
    fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS module_functions (
    module_id   INTEGER NOT NULL,
    function_id INTEGER NOT NULL,
    PRIMARY KEY (module_id, function_id)
);

CREATE TABLE IF NOT EXISTS function_taxonomy (
    function_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL
);
"""


@contextmanager
def connect(path: Path | None = None):
    p = path or DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
