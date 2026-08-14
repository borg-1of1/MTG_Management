#!/usr/bin/env python3
"""
card-lookup.py — Scryfall oracle text fetcher for deckbuilding sessions.

USAGE:
  # Load an entire decklist at session start:
  python card-lookup.py --decklist path/to/decklist.txt

  # Look up one or more specific cards mid-session:
  python card-lookup.py --cards "Sol Ring" "Arcane Signet" "Cultivate"

  # Load a decklist AND additional candidate cards in one pass:
  python card-lookup.py --decklist path/to/decklist.txt --cards "Dockside Extortionist"

OUTPUT:
  Prints a formatted oracle block for each card, ready to paste into a
  Claude session as _Card_Oracle input. Unknown card names are reported
  at the end without halting the run.

RATE LIMITS:
  Scryfall asks for a 50–100ms delay between requests. The /cards/collection
  endpoint handles up to 75 cards per request, so a full 99-card decklist
  is fetched in two API calls. Single-card lookups use /cards/named.

DECKLIST FORMAT:
  Expects Moxfield export format — one card per line. Works with both the
  plain text export (1x prefix) and the markdown/Obsidian export (no x):
    1x Sol Ring                                  <- plain text export
    1 Sol Ring (LTC) 284                         <- markdown export, no x
    1 Krydle of Baldur's Gate (AFR) 226 *F*      <- foil marker stripped
    1 Path of Ancestry (PLST) NCC-419            <- alphanumeric collector # stripped
    1 Revitalizing Repast / Old-Growth Grove (MH3) 256 *F*  <- DFC handled
  Section headers (Commander, Deck, Sideboard), markdown headings (#),
  blank lines, and any non-card lines are silently ignored.
  Duplicate card names (e.g. basics across multiple print rows) are collapsed.
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

# ── Constants ────────────────────────────────────────────────────────────────

API_BASE = "https://api.scryfall.com"
USER_AGENT = "MTGDeckbuildingSession/1.0"
ACCEPT = "application/json"
REQUEST_DELAY = 0.1          # 100ms between requests per Scryfall guidelines
COLLECTION_BATCH_SIZE = 75   # Scryfall's max per /cards/collection call

# Fields extracted from each card — everything the deckbuilding protocol needs
ORACLE_FIELDS = [
    "name",
    "mana_cost",
    "cmc",
    "type_line",
    "oracle_text",
    "power",
    "toughness",
    "loyalty",
    "color_identity",
    "keywords",
    "card_faces",   # for DFCs, split cards, etc.
    "legalities",
]

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _get(url: str) -> dict:
    """GET a Scryfall URL and return the parsed JSON response."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": ACCEPT},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post(url: str, payload: dict) -> dict:
    """POST a JSON payload to a Scryfall URL and return the parsed JSON response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": ACCEPT,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ── Card data extraction ──────────────────────────────────────────────────────

def _extract_oracle(card: dict) -> dict:
    """
    Pull the fields we care about from a Scryfall card object.
    Handles double-faced cards by merging face data into the output.
    """
    out = {f: card.get(f) for f in ORACLE_FIELDS}

    # For DFCs and split cards, oracle_text lives on card_faces, not the root.
    # Merge face data into a readable representation.
    if card.get("card_faces") and not card.get("oracle_text"):
        faces = card["card_faces"]
        out["oracle_text"] = "\n//\n".join(
            f.get("oracle_text", "") for f in faces if f.get("oracle_text")
        )
        out["mana_cost"] = " // ".join(
            f.get("mana_cost", "") for f in faces if f.get("mana_cost")
        )
        out["type_line"] = " // ".join(
            f.get("type_line", "") for f in faces if f.get("type_line")
        )
        # Power/toughness on faces (e.g. transforming creatures)
        if not out.get("power"):
            powers = [f.get("power") for f in faces if f.get("power")]
            out["power"] = powers[0] if powers else None

    return out


def _format_oracle_block(card: dict) -> str:
    """
    Format a card's extracted data as a clean, paste-ready oracle block.
    This is what gets injected into the Claude session as _Card_Oracle.
    """
    lines = []
    lines.append(f"=== {card['name']} ===")

    mana = card.get("mana_cost") or ""
    cmc = card.get("cmc")
    if mana or cmc is not None:
        cmc_str = f"  (CMC: {int(cmc)})" if cmc is not None else ""
        lines.append(f"Mana Cost: {mana}{cmc_str}")

    if card.get("type_line"):
        lines.append(f"Type:      {card['type_line']}")

    pt = None
    if card.get("power") and card.get("toughness"):
        pt = f"{card['power']}/{card['toughness']}"
    elif card.get("loyalty"):
        pt = f"Loyalty: {card['loyalty']}"
    if pt:
        lines.append(f"P/T:       {pt}")

    if card.get("color_identity"):
        lines.append(f"Color ID:  {{{'/'.join(card['color_identity'])}}}")
    else:
        lines.append("Color ID:  Colorless")

    if card.get("keywords"):
        lines.append(f"Keywords:  {', '.join(card['keywords'])}")

    if card.get("oracle_text"):
        lines.append("")
        lines.append(card["oracle_text"])

    # Commander legality note — useful to catch banned cards early
    legalities = card.get("legalities") or {}
    commander_legal = legalities.get("commander", "unknown")
    if commander_legal != "legal":
        lines.append(f"\n[!] Commander legality: {commander_legal.upper()}")

    lines.append("")  # trailing blank line for readability
    return "\n".join(lines)

# ── Lookup functions ──────────────────────────────────────────────────────────

def lookup_single(name: str) -> Optional[dict]:
    """
    Fetch one card by exact name using /cards/named.
    Falls back to fuzzy search if exact match fails.
    Returns the extracted oracle dict, or None if not found.
    """
    encoded = urllib.parse.quote(name)

    # Try exact first
    try:
        url = f"{API_BASE}/cards/named?exact={encoded}"
        raw = _get(url)
        return _extract_oracle(raw)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    # Fall back to fuzzy
    try:
        url = f"{API_BASE}/cards/named?fuzzy={encoded}"
        raw = _get(url)
        return _extract_oracle(raw)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def lookup_batch(names: list[str]) -> tuple[list[dict], list[str]]:
    """
    Fetch up to COLLECTION_BATCH_SIZE cards in a single POST to /cards/collection.
    Returns (found_cards, not_found_names).
    Automatically chunks if len(names) > COLLECTION_BATCH_SIZE.
    """
    found = []
    not_found = []

    for i in range(0, len(names), COLLECTION_BATCH_SIZE):
        chunk = names[i : i + COLLECTION_BATCH_SIZE]
        identifiers = [{"name": n} for n in chunk]
        payload = {"identifiers": identifiers}

        resp = _post(f"{API_BASE}/cards/collection", payload)

        for card in resp.get("data", []):
            found.append(_extract_oracle(card))

        for nf in resp.get("not_found", []):
            not_found.append(nf.get("name", str(nf)))

        if i + COLLECTION_BATCH_SIZE < len(names):
            time.sleep(REQUEST_DELAY)

    return found, not_found

# ── Decklist parsing ──────────────────────────────────────────────────────────

# Section headers produced by Moxfield text export
_SECTION_HEADERS = {"commander", "deck", "sideboard", "maybeboard", "considering"}
# Matches "1x Card Name" or "1 Card Name"
_CARD_LINE = re.compile(r"^\d+x?\s+(.+)$", re.IGNORECASE)


def parse_decklist(path: str) -> list[str]:
    """
    Parse a Moxfield flat text export and return a deduplicated list of card names.
    Section headers and blank lines are skipped.
    Set codes and collector numbers (e.g. "(CMM) 175") are stripped if present.
    """
    names = []
    seen = set()

    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.lower() in _SECTION_HEADERS:
                continue

            match = _CARD_LINE.match(line)
            if not match:
                # Could be a bare section header we didn't catch — skip it
                continue

            name = match.group(1).strip()
            # Strip set code and everything after it.
            # Handles all Moxfield export variants:
            #   "Sol Ring (CMM) 175"                              -> "Sol Ring"
            #   "Krydle of Baldur's Gate (AFR) 226 *F*"          -> "Krydle of Baldur's Gate"
            #   "Path of Ancestry (PLST) NCC-419"                -> "Path of Ancestry"
            #   "Revitalizing Repast / Old-Growth Grove (MH3) 256 *F*" -> full DFC name
            name = re.sub(r"\s*\([A-Z0-9]{2,6}\).*$", "", name).strip()

            if name and name not in seen:
                names.append(name)
                seen.add(name)

    return names

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Scryfall oracle text for deckbuilding sessions."
    )
    parser.add_argument(
        "--decklist",
        metavar="FILE",
        help="Path to a Moxfield flat text export. All cards are fetched in batch.",
    )
    parser.add_argument(
        "--cards",
        metavar="CARD",
        nargs="+",
        help='One or more card names to look up. Quote multi-word names: "Sol Ring"',
    )
    args = parser.parse_args()

    if not args.decklist and not args.cards:
        parser.print_help()
        sys.exit(1)

    all_names: list[str] = []
    output_blocks: list[str] = []
    all_not_found: list[str] = []

    # ── Decklist batch lookup ────────────────────────────────────────────────
    if args.decklist:
        try:
            deck_names = parse_decklist(args.decklist)
        except FileNotFoundError:
            print(f"ERROR: Decklist file not found: {args.decklist}", file=sys.stderr)
            sys.exit(1)

        if not deck_names:
            print("WARNING: No card names found in decklist.", file=sys.stderr)
        else:
            all_names.extend(deck_names)
            print(
                f"[Decklist] {len(deck_names)} unique cards found. Fetching...",
                file=sys.stderr,
            )

    # ── Additional single/named cards ────────────────────────────────────────
    if args.cards:
        for name in args.cards:
            if name not in all_names:
                all_names.append(name)

    # ── Batch fetch everything ───────────────────────────────────────────────
    if all_names:
        found, not_found = lookup_batch(all_names)
        all_not_found.extend(not_found)

        # Sort output to match original order where possible
        name_order = {n.lower(): i for i, n in enumerate(all_names)}
        found.sort(key=lambda c: name_order.get(c["name"].lower(), 9999))

        for card in found:
            output_blocks.append(_format_oracle_block(card))

    # ── Output ───────────────────────────────────────────────────────────────
    if output_blocks:
        print("\n".join(output_blocks))

    if all_not_found:
        print("─" * 60, file=sys.stderr)
        print(
            f"NOT FOUND ({len(all_not_found)} card(s)) — check spelling or set legality:",
            file=sys.stderr,
        )
        for name in all_not_found:
            print(f"  • {name}", file=sys.stderr)
        print("─" * 60, file=sys.stderr)

    print(
        f"[Done] {len(output_blocks)} card(s) retrieved.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
