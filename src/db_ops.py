import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "cases.db")

def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with foreign keys enabled."""
    conn = sqlite3.Connection(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def close_connection(conn) -> None:
    """Close a SQLite connection"""
    conn.close()

def update_metadata(key: str, value: str) -> None:
    """Insert or update a key/value in the metadata table."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO metadata (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value;
    """, (key, value))
    conn.commit()
    conn.close()

def get_metadata(key: str) -> str | None:
    """Fetch a value from metadata table, or None if not set."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM metadata WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def insert_case_with_details(
    conn: sqlite3.Connection,
    division: str,
    case_numbers: list[tuple[str, bool]],
    case_title: str,
    panel_date: str,
    oral_arguments: bool,
    judges: list[str],
    litigants: list[tuple[str, str]],
    attorneys: list[str],
    opinion_date: str | None = None,
    opinion_publication_status: str | None = None,
    disposition_status: str = "normal",
    lower_court: str | None = None,
    lower_court_case_number: str | None = None,
    court_level: str = "appeals"
):
    """
        Insert a single case and its related data using an existing connection. Caller controls transaction
        and must call commit().
    """
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    scraped_at = datetime.utcnow().isoformat(timespec="seconds")

    # Insert into cases
    cur.execute("""
        INSERT OR IGNORE INTO cases
        (division, case_title, panel_date, oral_arguments,
         opinion_date, opinion_publication_status, disposition_status,
         lower_court, lower_court_case_number, court_level, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        division,
        case_title,
        panel_date,
        1 if oral_arguments else 0,
        opinion_date,
        opinion_publication_status,
        disposition_status,
        lower_court,
        lower_court_case_number,
        court_level,
        scraped_at
    ))
    case_id = cur.lastrowid

    # case_numbers
    for num, is_primary in case_numbers:
        num = num.strip()
        if num:
            cur.execute("""
                INSERT OR IGNORE INTO case_numbers (case_id, case_number, is_primary)
                VALUES (?, ?, ?)
            """, (case_id, num, 1 if is_primary else 0))

    # judges
    for judge in judges:
        judge = judge.strip()
        if judge:
            cur.execute("""
                INSERT OR IGNORE INTO judges (case_id, name)
                VALUES (?, ?)
            """, (case_id, judge))

    # litigants
    for name, role in litigants:
        name = name.strip()
        role = role.strip() if role else ""
        if name:
            cur.execute("""
                INSERT OR IGNORE INTO litigants (case_id, name, role)
                VALUES (?, ?, ?)
            """, (case_id, name, role))

    # attorneys
    for attorney in attorneys:
        attorney = attorney.strip()
        if attorney:
            cur.execute("""
                INSERT OR IGNORE INTO attorneys (case_id, name)
                VALUES (?, ?)
            """, (case_id, attorney))


def update_case_opinion(
    conn: sqlite3.Connection,
    case_number: str,
    opinion_date: str,
    opinion_type: str
) -> bool:
    """
    Update opinion_date and opinion_publication_status for the case
    with the given primary case_number, using an existing connection.
    Returns True if a row was updated.
    """
    cur = conn.cursor()

    # Look up the case_id by primary case number
    cur.execute("""
        SELECT case_id
        FROM case_numbers
        WHERE case_number = ? 
    """, (case_number,))
    row = cur.fetchone()
    if not row:
        return False

    case_id = row[0]

    # Update the opinion fields
    cur.execute("""
        UPDATE cases
        SET opinion_date = ?, opinion_publication_status = ?
        WHERE id = ?
    """, (opinion_date, opinion_type, case_id))

    # No commit here — caller controls transaction boundaries
    return cur.rowcount > 0
