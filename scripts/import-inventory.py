#!/usr/bin/env python3
"""
import-inventory.py

Reads a Moxfield collection export CSV, aggregates owned card counts by name,
and upserts into mtg-session.sqlite owned_cards table.

Default paths (all relative to the inventory directory):
  Input:  G:\\My Drive\\MTG_Decks\\inventory\\moxfield_haves_*.csv  (most recent by mtime)
  Output: G:\\My Drive\\MTG_Decks\\inventory\\mtg-session.sqlite

Usage:
  python import-inventory.py
  python import-inventory.py --input "C:\path\to\export.csv"
  python import-inventory.py --output "C:\path\to\mtg-session.sqlite"
  python import-inventory.py --input export.csv --output session.sqlite
  python import-inventory.py --dry-run
"""

import argparse
import csv
import glob
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

INVENTORY_DIR = Path(r"G:\My Drive\MTG_Decks\inventory")
DEFAULT_DB     = INVENTORY_DIR / "mtg-session.sqlite"
CSV_GLOB       = str(INVENTORY_DIR / "moxfield_haves_*.csv")

# Moxfield CSV column names (confirmed against header row 2026-08-14)
COL_COUNT  = "Count"
COL_NAME   = "Name"
COL_PROXY  = "Proxy"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS owned_cards (
    card_name     TEXT PRIMARY KEY,
    total_copies  INTEGER NOT NULL DEFAULT 0,
    has_proxy     INTEGER NOT NULL DEFAULT 0,   -- 1 = at least one proxy copy
    last_imported TEXT NOT NULL                 -- ISO-8601 UTC timestamp
);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_latest_csv(pattern: str) -> Path:
    """Return the most recently modified file matching glob pattern."""
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(
            f"No Moxfield export found matching: {pattern}\n"
            f"Drop the CSV into {INVENTORY_DIR} or pass --input explicitly."
        )
    return Path(max(matches, key=os.path.getmtime))


def parse_csv(path: Path) -> dict[str, dict]:
    """
    Read the Moxfield CSV and aggregate by card name.

    Returns:
        { card_name: { "total_copies": int, "has_proxy": bool } }
    """
    aggregated: dict[str, dict] = {}

    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)  # comma-delimited with quoted fields (Moxfield default)

        # Validate expected columns are present
        required = {COL_COUNT, COL_NAME, COL_PROXY}
        if reader.fieldnames is None:
            raise ValueError("CSV appears to be empty — no header row found.")
        actual = set(reader.fieldnames)
        missing = required - actual
        if missing:
            raise ValueError(
                f"CSV is missing expected columns: {missing}\n"
                f"Found columns: {actual}"
            )

        for lineno, row in enumerate(reader, start=2):  # start=2: row 1 is header
            name = row[COL_NAME].strip()
            if not name:
                print(f"  Warning: empty Name on line {lineno}, skipping.", file=sys.stderr)
                continue

            try:
                count = int(row[COL_COUNT])
            except (ValueError, KeyError):
                print(
                    f"  Warning: invalid Count '{row.get(COL_COUNT)}' on line {lineno} "
                    f"({name}), skipping.",
                    file=sys.stderr,
                )
                continue

            proxy_raw = row[COL_PROXY].strip().upper()
            is_proxy  = proxy_raw == "TRUE"

            if name not in aggregated:
                aggregated[name] = {"total_copies": 0, "has_proxy": False}

            aggregated[name]["total_copies"] += count
            if is_proxy:
                aggregated[name]["has_proxy"] = True

    return aggregated


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Create owned_cards table if it doesn't exist."""
    conn.execute(DDL)
    conn.commit()


def upsert(conn: sqlite3.Connection, aggregated: dict[str, dict], timestamp: str) -> tuple[int, int]:
    """
    Upsert all aggregated rows into owned_cards.

    Returns (inserted_count, updated_count) — approximate; SQLite's
    changes() reports total rows affected, so we track via a pre-check.
    """
    inserted = 0
    updated  = 0

    cur = conn.cursor()

    for name, data in aggregated.items():
        cur.execute("SELECT 1 FROM owned_cards WHERE card_name = ?", (name,))
        exists = cur.fetchone() is not None

        cur.execute(
            """
            INSERT INTO owned_cards (card_name, total_copies, has_proxy, last_imported)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(card_name) DO UPDATE SET
                total_copies  = excluded.total_copies,
                has_proxy     = excluded.has_proxy,
                last_imported = excluded.last_imported
            """,
            (name, data["total_copies"], int(data["has_proxy"]), timestamp),
        )

        if exists:
            updated += 1
        else:
            inserted += 1

    conn.commit()
    return inserted, updated


def report_stale(conn: sqlite3.Connection, timestamp: str) -> None:
    """
    Print any rows whose last_imported predates this run.
    These are cards present in the DB but absent from the current CSV —
    potentially traded/sold away. They are NOT deleted; just flagged.
    """
    cur = conn.execute(
        "SELECT card_name, total_copies, last_imported FROM owned_cards WHERE last_imported < ?",
        (timestamp,),
    )
    stale = cur.fetchall()
    if stale:
        print(f"\n  Stale rows (not in this export — {len(stale)} card(s)):")
        for row in stale:
            print(f"    {row[0]}  [{row[1]} copies, last seen {row[2]}]")
        print("  These rows were NOT removed. Delete manually if no longer owned.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import Moxfield collection CSV into mtg-session.sqlite."
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Path to Moxfield export CSV. Default: most recent moxfield_haves_*.csv in inventory dir.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=str(DEFAULT_DB),
        help=f"Path to mtg-session.sqlite. Default: {DEFAULT_DB}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and aggregate the CSV but do not write to the database.",
    )
    args = parser.parse_args()

    # --- Resolve input CSV ---
    if args.input:
        csv_path = Path(args.input)
        if not csv_path.exists():
            print(f"Error: input file not found: {csv_path}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            csv_path = find_latest_csv(CSV_GLOB)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    db_path = Path(args.output)

    print(f"Input:  {csv_path}")
    print(f"Output: {db_path}")
    if args.dry_run:
        print("Mode:   DRY RUN — no database writes.")
    print()

    # --- Parse CSV ---
    print("Parsing CSV...")
    try:
        aggregated = parse_csv(csv_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    unique_names = len(aggregated)
    total_copies = sum(d["total_copies"] for d in aggregated.values())
    proxy_count  = sum(1 for d in aggregated.values() if d["has_proxy"])

    print(f"  {unique_names} unique card names")
    print(f"  {total_copies} total copies")
    print(f"  {proxy_count} card names with at least one proxy")

    if args.dry_run:
        print("\nDry run complete. No database written.")
        return

    # --- Upsert into DB ---
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"\nOpening database: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        ensure_schema(conn)
        print("Upserting records...")
        inserted, updated = upsert(conn, aggregated, timestamp)
        print(f"  {inserted} new rows inserted")
        print(f"  {updated} existing rows updated")
        report_stale(conn, timestamp)

    print(f"\nDone. Import timestamp: {timestamp}")


if __name__ == "__main__":
    main()
