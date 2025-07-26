import argparse
import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cases.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def query_cases_for_attorney(pattern: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            c.case_title,
            c.panel_date,
            c.division,
            a.name AS attorney_name,
            cn.case_number,
            cn.is_primary
        FROM cases c
        JOIN attorneys a ON c.id = a.case_id
        JOIN case_numbers cn ON c.id = cn.case_id
        WHERE LOWER(a.name) LIKE LOWER(?)
        ORDER BY c.panel_date;
    """, (f"%{pattern}%",))
    rows = cur.fetchall()
    conn.close()
    return rows

def query_unique_attorneys():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name
        FROM attorneys
        GROUP BY LOWER(name)
        ORDER BY name;
    """)
    names = [row[0] for row in cur.fetchall()]
    conn.close()
    return names

def query_unique_judges():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT name
        FROM judges
        GROUP BY LOWER(name)
        ORDER BY name;
    """)
    names = [row[0] for row in cur.fetchall()]
    conn.close()
    return names

def export_to_csv(filename: str, rows: list, headers: list):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"✅ Exported {len(rows)} rows to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Query WA appellate cases database."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Subcommand: attorney-cases ---
    p_attorney = subparsers.add_parser(
        "attorney-cases", help="Find cases for an attorney name pattern."
    )
    p_attorney.add_argument("pattern", help="Attorney name substring (case-insensitive).")
    p_attorney.add_argument(
        "--csv", help="Optional CSV filename to export results.", default=None
    )

    # --- Subcommand: unique-attorneys ---
    subparsers.add_parser(
        "unique-attorneys", help="List unique attorney names."
    )

    # --- Subcommand: unique-judges ---
    subparsers.add_parser(
        "unique-judges", help="List unique judge names."
    )

    args = parser.parse_args()

    if args.command == "attorney-cases":
        rows = query_cases_for_attorney(args.pattern)
        headers = ["case_title", "panel_date", "division", "attorney_name", "case_number", "is_primary"]
        # Print first few rows
        for row in rows[:10]:
            print(row)
        print(f"Total rows: {len(rows)}")
        if args.csv:
            export_to_csv(args.csv, rows, headers)

    elif args.command == "unique-attorneys":
        names = query_unique_attorneys()
        print(f"Total unique attorneys: {len(names)}")
        for name in names[:20]:
            print(name)

    elif args.command == "unique-judges":
        names = query_unique_judges()
        print(f"Total unique judges: {len(names)}")
        for name in names[:20]:
            print(name)

if __name__ == "__main__":
    main()
