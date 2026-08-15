#!/usr/bin/env python3
"""
card-lookup.py — MTG oracle text fetcher for deckbuilding sessions.

Lookup priority:
  1. MTGJSON SQLite (AllPrintings.sqlite) — primary, offline, no rate limits
  2. Scryfall API — fallback for cards not found in MTGJSON (post-cutoff sets)

Ownership annotation:
  ATTACHes mtg-session.sqlite and LEFT JOINs owned_cards on card name.
  Each oracle block shows [Inventory — N copies] or [Not Owned].

USAGE:
  # Load an entire decklist at session start:
  python card-lookup.py --decklist path/to/decklist.txt

  # Look up one or more specific cards mid-session:
  python card-lookup.py --cards "Sol Ring" "Arcane Signet"

  # Both at once:
  python card-lookup.py --decklist path/to/decklist.txt --cards "Dockside Extortionist"

  # Override output destination:
  python card-lookup.py --decklist path/to/decklist.txt --output path/to/card-oracle.md
  python card-lookup.py --cards "Sol Ring" --output path/to/card-lookup.md

OUTPUT MODES:
  --decklist   writes card-oracle.md into the same folder as the decklist
  --cards      writes/appends to MTG_Decks/cards/card-lookup.md
  --output     overrides destination for either mode
  Stdout fallback when no output path is resolvable.

DECKLIST FORMAT:
  Moxfield flat text or markdown export. Examples handled:
    1x Sol Ring
    1 Sol Ring (LTC) 284
    1 Krydle of Baldur's Gate (AFR) 226 *F*
    1 Path of Ancestry (PLST) NCC-419
    1 Disciple of Freyalise / Garden of Freyalise (MH3) 256 *F*   <- MDFC
    1 Thranduil, Sindarin Liege / Silvan Rally (LTR) 200           <- Adventure
  MDFCs, Adventures, and Omens are reduced to the front face name for lookup.
  Section headers, markdown headings, blank lines silently ignored.
  Duplicate names collapsed.

RATE LIMITS:
  Scryfall fallback: 100ms delay between calls per Scryfall guidelines.
  /cards/collection handles up to 75 cards per POST.
"""

import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

INVENTORY_DIR      = Path(r"G:\My Drive\MTG_Decks\inventory")
ALLPRINTINGS_DB    = INVENTORY_DIR / "AllPrintings.sqlite"
SESSION_DB         = INVENTORY_DIR / "mtg-session.sqlite"
CARDS_DIR          = Path(r"G:\My Drive\MTG_Decks\cards")
PERSISTENT_CACHE   = CARDS_DIR / "card-lookup.md"

# ---------------------------------------------------------------------------
# Scryfall constants
# ---------------------------------------------------------------------------

API_BASE             = "https://api.scryfall.com"
USER_AGENT           = "MTGDeckbuildingSession/1.0"
ACCEPT               = "application/json"
REQUEST_DELAY        = 0.1   # 100ms between Scryfall requests
COLLECTION_BATCH     = 75    # Scryfall max per /cards/collection call

# ---------------------------------------------------------------------------
# Decklist parsing
# ---------------------------------------------------------------------------

_SECTION_HEADERS = {"commander", "deck", "sideboard", "maybeboard", "considering"}
_CARD_LINE       = re.compile(r"^\d+x?\s+(.+)$", re.IGNORECASE)
_SET_SUFFIX      = re.compile(r"\s*\([A-Z0-9]{2,6}\).*$")


def parse_decklist(path: str) -> list[str]:
    """
    Parse a Moxfield flat text or markdown export.
    Returns a deduplicated list of front-face card names.

    MDFCs, Adventures, and Omens with ' / ' in the name are reduced to
    the front face only — Scryfall and MTGJSON both accept this form,
    and it avoids the single-slash vs double-slash ambiguity in the
    collection endpoint.
    """
    names: list[str] = []
    seen:  set[str]  = set()

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.lstrip("#").strip().lower() in _SECTION_HEADERS:
                continue

            match = _CARD_LINE.match(line)
            if not match:
                continue

            name = match.group(1).strip()
            # Strip set code + collector number + foil markers
            name = _SET_SUFFIX.sub("", name).strip()
            # MDFCs / Adventures / Omens: keep front face only
            if " / " in name:
                name = name.split(" / ")[0].strip()

            if name and name not in seen:
                names.append(name)
                seen.add(name)

    return names

# ---------------------------------------------------------------------------
# MTGJSON SQLite lookup
# ---------------------------------------------------------------------------

# Columns we need from AllPrintings cards table (all confirmed from schema)
# The WHERE clause matches both:
#   exact name  — single-faced cards and any card looked up by full name
#   LIKE prefix — MDFCs/Adventures stored as "Front // Back" when we only
#                 have the front-face name (Moxfield exports single slash,
#                 we strip to front face, MTGJSON stores double slash)
_MTGJSON_SELECT = """
    SELECT
        c.name,
        c.manaCost,
        c.manaValue,
        c.type,
        c.text,
        c.power,
        c.toughness,
        c.loyalty,
        c.colorIdentity,
        c.keywords,
        c.layout,
        c.side,
        cl.commander
    FROM mtgjson.cards c
    LEFT JOIN mtgjson.cardLegalities cl ON cl.uuid = c.uuid
    INNER JOIN mtgjson.sets s ON s.code = c.setCode
    WHERE (c.name = ? OR c.name LIKE ? || ' //%')
      AND (c.language IS NULL OR c.language = 'English')
      AND c.isPromo  = 0
      AND c.isRebalanced = 0
    ORDER BY s.releaseDate DESC
    LIMIT 1
"""

# Front face query for MDFCs — fetch both faces by the front-face name,
# then stitch them together.
_MTGJSON_DFC_FACES = """
    SELECT
        c.name,
        c.manaCost,
        c.manaValue,
        c.type,
        c.text,
        c.power,
        c.toughness,
        c.loyalty,
        c.colorIdentity,
        c.keywords,
        c.layout,
        c.side,
        cl.commander,
        s.releaseDate
    FROM mtgjson.cards c
    LEFT JOIN mtgjson.cardLegalities cl ON cl.uuid = c.uuid
    INNER JOIN mtgjson.sets s ON s.code = c.setCode
    WHERE c.uuid IN (
        SELECT uuid FROM mtgjson.cards
        WHERE (name = ? OR name LIKE ? || ' //%')
          AND (language IS NULL OR language = 'English')
          AND isPromo = 0
          AND isRebalanced = 0
        ORDER BY (
            SELECT releaseDate FROM mtgjson.sets WHERE code = setCode
        ) DESC
        LIMIT 1
    )
    OR c.uuid IN (
        -- Back faces share otherFaceIds with the front face uuid
        SELECT uuid FROM mtgjson.cards
        WHERE otherFaceIds LIKE (
            '%' || (
                SELECT uuid FROM mtgjson.cards
                WHERE (name = ? OR name LIKE ? || ' //%')
                  AND (language IS NULL OR language = 'English')
                  AND isPromo = 0
                  AND isRebalanced = 0
                ORDER BY (
                    SELECT releaseDate FROM mtgjson.sets WHERE code = setCode
                ) DESC
                LIMIT 1
            ) || '%'
        )
        AND (language IS NULL OR language = 'English')
        AND isPromo = 0
        AND isRebalanced = 0
    )
    ORDER BY c.side ASC, s.releaseDate DESC
"""

_DFC_LAYOUTS = {"transform", "modal_dfc", "adventure", "split", "flip", "meld"}


def _mtgjson_row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "name":          row["name"],
        "manaCost":      row["manaCost"],
        "manaValue":     row["manaValue"],
        "type":          row["type"],
        "text":          row["text"],
        "power":         row["power"],
        "toughness":     row["toughness"],
        "loyalty":       row["loyalty"],
        "colorIdentity": row["colorIdentity"],
        "keywords":      row["keywords"],
        "layout":        row["layout"],
        "side":          row["side"],
        "commander":     row["commander"],
    }


def lookup_mtgjson(
    conn: sqlite3.Connection,
    name: str,
) -> Optional[dict]:
    """
    Look up a card in the attached MTGJSON database.
    Returns a normalised card dict, or None if not found.
    Handles single-faced cards and multi-faced layouts.
    """
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # First pass: fetch the canonical single row for this name.
    # Query takes 2 params: exact name and prefix for the LIKE fallback.
    cur.execute(_MTGJSON_SELECT, (name, name))
    row = cur.fetchone()
    if row is None:
        return None

    card = _mtgjson_row_to_dict(row)

    # If it's a multi-faced layout, fetch all faces and stitch.
    # Query takes 4 params: (name, name, name, name) — two pairs for the
    # two LIKE-or-exact clauses in the front-face and back-face subqueries.
    if card["layout"] in _DFC_LAYOUTS:
        cur.execute(_MTGJSON_DFC_FACES, (name, name, name, name))
        face_rows = cur.fetchall()

        if len(face_rows) >= 2:
            faces = [_mtgjson_row_to_dict(r) for r in face_rows]
            # Deduplicate by (name, side) — the join can produce extras
            seen_faces: set[tuple] = set()
            deduped = []
            for f in faces:
                key = (f["name"], f["side"])
                if key not in seen_faces:
                    seen_faces.add(key)
                    deduped.append(f)
            card["faces"] = deduped
        # If we only got 1 face back, treat as single-faced — card dict is fine as-is

    return card

# ---------------------------------------------------------------------------
# Scryfall fallback
# ---------------------------------------------------------------------------

def _sf_get(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": ACCEPT},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _sf_post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent":   USER_AGENT,
            "Accept":       ACCEPT,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _scryfall_to_card(raw: dict) -> dict:
    """Normalise a Scryfall card object into our internal card dict."""
    card: dict = {
        "name":          raw.get("name"),
        "manaCost":      raw.get("mana_cost"),
        "manaValue":     raw.get("cmc"),
        "type":          raw.get("type_line"),
        "text":          raw.get("oracle_text"),
        "power":         raw.get("power"),
        "toughness":     raw.get("toughness"),
        "loyalty":       raw.get("loyalty"),
        "colorIdentity": ",".join(raw.get("color_identity", [])),
        "keywords":      ",".join(raw.get("keywords", [])),
        "layout":        raw.get("layout"),
        "side":          None,
        "commander":     raw.get("legalities", {}).get("commander"),
        "source":        "scryfall",
    }

    # Handle multi-faced Scryfall cards
    if raw.get("card_faces") and not raw.get("oracle_text"):
        faces = raw["card_faces"]
        card["text"] = "\n//\n".join(
            f.get("oracle_text", "") for f in faces if f.get("oracle_text")
        )
        card["manaCost"] = " // ".join(
            f.get("mana_cost", "") for f in faces if f.get("mana_cost")
        )
        card["type"] = " // ".join(
            f.get("type_line", "") for f in faces if f.get("type_line")
        )
        if not card["power"]:
            powers = [f.get("power") for f in faces if f.get("power")]
            card["power"] = powers[0] if powers else None

    return card


def scryfall_batch(names: list[str]) -> tuple[list[dict], list[str]]:
    """
    POST to /cards/collection in chunks of COLLECTION_BATCH.
    Returns (found_cards, not_found_names).
    """
    found:     list[dict] = []
    not_found: list[str]  = []

    for i in range(0, len(names), COLLECTION_BATCH):
        chunk = names[i : i + COLLECTION_BATCH]
        resp  = _sf_post(
            f"{API_BASE}/cards/collection",
            {"identifiers": [{"name": n} for n in chunk]},
        )
        for raw in resp.get("data", []):
            found.append(_scryfall_to_card(raw))
        for nf in resp.get("not_found", []):
            not_found.append(nf.get("name", str(nf)))

        if i + COLLECTION_BATCH < len(names):
            time.sleep(REQUEST_DELAY)

    return found, not_found

# ---------------------------------------------------------------------------
# Ownership annotation
# ---------------------------------------------------------------------------

def annotate_ownership(
    conn: sqlite3.Connection,
    card_name: str,
) -> str:
    """
    Query owned_cards in the attached session DB.
    Returns a formatted ownership string for the oracle block footer.
    """
    try:
        cur = conn.execute(
            "SELECT total_copies, has_proxy FROM session.owned_cards WHERE card_name = ?",
            (card_name,),
        )
        row = cur.fetchone()
        if row is None:
            return "[Not Owned]"
        copies, has_proxy = row
        label = f"[Inventory — {copies} {'copy' if copies == 1 else 'copies'}]"
        if has_proxy:
            label += "  [Proxy available]"
        return label
    except sqlite3.OperationalError:
        # session DB or owned_cards table not present — degrade gracefully
        return "[Inventory unknown — run import-inventory.py]"

# ---------------------------------------------------------------------------
# Oracle block formatting
# ---------------------------------------------------------------------------

def _format_color_identity(raw: Optional[str]) -> str:
    if not raw:
        return "Colorless"
    # MTGJSON stores as comma-separated "W,U,B,R,G"
    # Scryfall normalised version stores same way after our conversion
    colors = [c.strip() for c in raw.split(",") if c.strip()]
    return "{" + "/".join(colors) + "}" if colors else "Colorless"


def format_oracle_block(card: dict, ownership: str) -> str:
    """
    Render a card dict as a paste-ready oracle block.
    Handles both single-faced and multi-faced cards.
    """
    lines: list[str] = []
    source_tag = "  [via Scryfall]" if card.get("source") == "scryfall" else ""

    lines.append(f"=== {card['name']} ==={source_tag}")

    # ── Single-faced ────────────────────────────────────────────────────────
    if not card.get("faces"):
        mana = card.get("manaCost") or ""
        cmc  = card.get("manaValue")
        if mana or cmc is not None:
            cmc_str = f"  (CMC: {int(cmc)})" if cmc is not None else ""
            lines.append(f"Mana Cost: {mana}{cmc_str}")

        if card.get("type"):
            lines.append(f"Type:      {card['type']}")

        if card.get("power") and card.get("toughness"):
            lines.append(f"P/T:       {card['power']}/{card['toughness']}")
        elif card.get("loyalty"):
            lines.append(f"Loyalty:   {card['loyalty']}")

        lines.append(f"Color ID:  {_format_color_identity(card.get('colorIdentity'))}")

        if card.get("keywords"):
            kws = [k.strip() for k in card["keywords"].split(",") if k.strip()]
            if kws:
                lines.append(f"Keywords:  {', '.join(kws)}")

        if card.get("text"):
            lines.append("")
            lines.append(card["text"])

    # ── Multi-faced ─────────────────────────────────────────────────────────
    else:
        faces = card["faces"]

        # Color identity lives on the front face (or the root for Scryfall)
        lines.append(
            f"Color ID:  {_format_color_identity(card.get('colorIdentity') or faces[0].get('colorIdentity'))}"
        )

        for face in faces:
            lines.append("")
            lines.append(f"--- {face['name']} ---")

            mana = face.get("manaCost") or ""
            cmc  = face.get("manaValue")
            if mana or cmc is not None:
                cmc_str = f"  (CMC: {int(cmc)})" if cmc is not None else ""
                lines.append(f"Mana Cost: {mana}{cmc_str}")

            if face.get("type"):
                lines.append(f"Type:      {face['type']}")

            if face.get("power") and face.get("toughness"):
                lines.append(f"P/T:       {face['power']}/{face['toughness']}")
            elif face.get("loyalty"):
                lines.append(f"Loyalty:   {face['loyalty']}")

            if face.get("keywords"):
                kws = [k.strip() for k in face["keywords"].split(",") if k.strip()]
                if kws:
                    lines.append(f"Keywords:  {', '.join(kws)}")

            if face.get("text"):
                lines.append("")
                lines.append(face["text"])

    # ── Footer ───────────────────────────────────────────────────────────────
    lines.append("")

    commander_legal = card.get("commander") or (
        card["faces"][0].get("commander") if card.get("faces") else None
    )
    if commander_legal and commander_legal != "legal":
        lines.append(f"[!] Commander legality: {commander_legal.upper()}")

    lines.append(ownership)
    lines.append("")   # trailing blank line
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Core lookup orchestration
# ---------------------------------------------------------------------------

def lookup_all(
    names: list[str],
    conn: sqlite3.Connection,
) -> tuple[list[tuple[str, dict]], list[str]]:
    """
    Look up all names. MTGJSON first; Scryfall for any misses.

    Returns:
        found     — list of (original_name, card_dict), in input order
        not_found — names that failed both sources
    """
    found_map:  dict[str, dict] = {}
    need_scryfall: list[str]    = []

    # ── Pass 1: MTGJSON ──────────────────────────────────────────────────────
    for name in names:
        card = lookup_mtgjson(conn, name)
        if card:
            found_map[name] = card
        else:
            need_scryfall.append(name)

    if need_scryfall:
        print(
            f"[MTGJSON miss — Scryfall fallback for {len(need_scryfall)} card(s)]",
            file=sys.stderr,
        )

    # ── Pass 2: Scryfall fallback ────────────────────────────────────────────
    not_found: list[str] = []
    if need_scryfall:
        try:
            sf_found, sf_not_found = scryfall_batch(need_scryfall)
            for card in sf_found:
                # Match back to the requested name. Scryfall returns canonical
                # names which may differ from what we sent:
                #   - Exact match:   "Sol Ring" -> "Sol Ring"          OK
                #   - MDFC/Adv:      we sent "Disciple of Freyalise",
                #                    Scryfall returns
                #                    "Disciple of Freyalise // Garden of Freyalise"
                # Strategy: exact match first, then check whether the Scryfall
                # name starts with the requested name followed by " //" (the
                # canonical MDFC separator Scryfall uses).
                matched = False
                sf_name_lower = card["name"].lower()
                for req_name in need_scryfall:
                    req_lower = req_name.lower()
                    if (sf_name_lower == req_lower or
                            sf_name_lower.startswith(req_lower + " //")):
                        found_map[req_name] = card
                        matched = True
                        break
                if not matched:
                    # Couldn't match to a request — store under Scryfall's name
                    # so it still appears in output rather than being silently lost
                    found_map[card["name"]] = card
            not_found.extend(sf_not_found)
        except Exception as e:
            print(f"[Scryfall error: {e}]", file=sys.stderr)
            not_found.extend(need_scryfall)

    # Preserve input order
    found_ordered = [
        (name, found_map[name])
        for name in names
        if name in found_map
    ]
    return found_ordered, not_found

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def resolve_output_path(
    mode: str,
    decklist_path: Optional[str],
    override: Optional[str],
) -> Optional[Path]:
    """
    Determine the output file path.
      --decklist mode : <decklist_dir>/card-oracle.md  (or --output override)
      --cards mode    : PERSISTENT_CACHE               (or --output override)
    Returns None if path cannot be resolved (triggers stdout fallback).
    """
    if override:
        return Path(override)
    if mode == "decklist" and decklist_path:
        return Path(decklist_path).parent / "card-oracle.md"
    if mode == "cards":
        return PERSISTENT_CACHE
    return None


def write_output(
    blocks: list[str],
    out_path: Optional[Path],
    mode: str,
) -> None:
    """
    Write oracle blocks to file (append for cards mode, overwrite for decklist),
    or stdout if no path.
    """
    content = "\n".join(blocks)

    if out_path is None:
        print(content)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    file_mode = "a" if mode == "cards" else "w"
    with open(out_path, file_mode, encoding="utf-8") as fh:
        if mode == "cards":
            # Append header with timestamp so the cache is scannable
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            fh.write(f"\n<!-- lookup: {ts} -->\n")
        fh.write(content)
        fh.write("\n")

    print(f"[Output written to {out_path}]", file=sys.stderr)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch MTG oracle text for deckbuilding sessions."
    )
    parser.add_argument(
        "--decklist", metavar="FILE",
        help="Path to a Moxfield flat text export. Writes card-oracle.md alongside it.",
    )
    parser.add_argument(
        "--cards", metavar="CARD", nargs="+",
        help='One or more card names. Appends to MTG_Decks/cards/card-lookup.md.',
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="Override output file path for either mode.",
    )
    parser.add_argument(
        "--allprintings", metavar="FILE", default=str(ALLPRINTINGS_DB),
        help=f"Path to AllPrintings.sqlite. Default: {ALLPRINTINGS_DB}",
    )
    parser.add_argument(
        "--sessiondb", metavar="FILE", default=str(SESSION_DB),
        help=f"Path to mtg-session.sqlite. Default: {SESSION_DB}",
    )
    args = parser.parse_args()

    if not args.decklist and not args.cards:
        parser.print_help()
        sys.exit(1)

    # ── Determine mode ───────────────────────────────────────────────────────
    # If both flags given, mode is "decklist" for output path resolution
    mode = "decklist" if args.decklist else "cards"

    # ── Build name list ──────────────────────────────────────────────────────
    all_names: list[str] = []
    seen_names: set[str] = set()

    if args.decklist:
        try:
            deck_names = parse_decklist(args.decklist)
        except FileNotFoundError:
            print(f"ERROR: decklist not found: {args.decklist}", file=sys.stderr)
            sys.exit(1)
        if not deck_names:
            print("WARNING: no card names found in decklist.", file=sys.stderr)
        else:
            print(f"[Decklist] {len(deck_names)} unique cards", file=sys.stderr)
            for n in deck_names:
                if n not in seen_names:
                    all_names.append(n)
                    seen_names.add(n)

    if args.cards:
        for n in args.cards:
            if n not in seen_names:
                all_names.append(n)
                seen_names.add(n)

    if not all_names:
        print("ERROR: no card names to look up.", file=sys.stderr)
        sys.exit(1)

    # ── Open databases ───────────────────────────────────────────────────────
    allprintings_path = Path(args.allprintings)
    sessiondb_path    = Path(args.sessiondb)

    if not allprintings_path.exists():
        print(
            f"ERROR: AllPrintings.sqlite not found at {allprintings_path}\n"
            f"Download from https://mtgjson.com/downloads/all-files/ and place in {INVENTORY_DIR}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Connect to a lightweight in-memory coordination DB, then ATTACH both files.
    # Use forward slashes in the path strings — SQLite on Windows accepts them
    # and it avoids backslash escaping issues inside SQL string literals.
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    ap_posix = allprintings_path.as_posix()
    conn.execute(f"ATTACH DATABASE '{ap_posix}' AS mtgjson")

    if sessiondb_path.exists():
        sd_posix = sessiondb_path.as_posix()
        conn.execute(f"ATTACH DATABASE '{sd_posix}' AS session")
        session_attached = True
    else:
        print(
            f"[Warning] mtg-session.sqlite not found — ownership annotations unavailable. "
            f"Run import-inventory.py to create it.]",
            file=sys.stderr,
        )
        session_attached = False

    # ── Diagnostics — confirm ATTACH and table access ────────────────────────
    try:
        cur = conn.execute("SELECT COUNT(*) FROM mtgjson.cards")
        count = cur.fetchone()[0]
        print(f"[Diag] mtgjson.cards row count: {count}", file=sys.stderr)
    except Exception as e:
        print(f"[Diag] mtgjson.cards not accessible: {e}", file=sys.stderr)

    try:
        cur = conn.execute(
            "SELECT name FROM mtgjson.cards WHERE name = 'Sol Ring' LIMIT 1"
        )
        row = cur.fetchone()
        print(f"[Diag] Sol Ring lookup: {row[0] if row else 'NOT FOUND'}", file=sys.stderr)
    except Exception as e:
        print(f"[Diag] Sol Ring query failed: {e}", file=sys.stderr)

    # ── Lookup ───────────────────────────────────────────────────────────────
    found_ordered, not_found = lookup_all(all_names, conn)

    # ── Format blocks ────────────────────────────────────────────────────────
    blocks: list[str] = []
    for req_name, card in found_ordered:
        ownership = (
            annotate_ownership(conn, card["name"])
            if session_attached
            else "[Inventory unknown — run import-inventory.py]"
        )
        blocks.append(format_oracle_block(card, ownership))

    # ── Write output ─────────────────────────────────────────────────────────
    out_path = resolve_output_path(mode, args.decklist, args.output)
    write_output(blocks, out_path, mode)

    # ── Not-found report ─────────────────────────────────────────────────────
    if not_found:
        print("─" * 60, file=sys.stderr)
        print(
            f"NOT FOUND ({len(not_found)}) — check spelling or set legality:",
            file=sys.stderr,
        )
        for name in not_found:
            print(f"  • {name}", file=sys.stderr)
        print("─" * 60, file=sys.stderr)

    print(
        f"[Done] {len(found_ordered)} card(s) retrieved, "
        f"{len(not_found)} not found.",
        file=sys.stderr,
    )

    conn.close()


if __name__ == "__main__":
    main()
