import sqlite3
import os

DB_FILE = "../data/cases.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

# ----- Core tables -----
cur.execute("""
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY,
    division TEXT NOT NULL,
    case_title TEXT,
    panel_date TEXT,
    oral_arguments INTEGER,
    opinion_date TEXT,
    opinion_publication_status TEXT,
    disposition_status TEXT DEFAULT 'normal',
    lower_court TEXT,
    lower_court_case_number TEXT,
    court_level TEXT DEFAULT 'appeals',
    scraped_at TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS case_numbers (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL,
    case_number TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    UNIQUE(case_id, case_number)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS litigants (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    UNIQUE(case_id, name, role)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attorneys (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    UNIQUE(case_id, name)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS judges (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
    UNIQUE(case_id, name)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS opinions_metadata (
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    scraped_at TEXT NOT NULL,
    PRIMARY KEY (year, month)
);
""")

conn.commit()
conn.close()
print(f"Database schema created in {DB_FILE}")



