#!/usr/bin/env python3
"""
new-deck.py — Scaffold a new deck folder in MTG_Decks.

Creates the deck directory and populates it with blank template files
using bare filenames (no deck slug prefix) to match the established
convention across existing decks.

USAGE:
  python new-deck.py <deck-slug>

EXAMPLES:
  python new-deck.py ur-dragon
  python new-deck.py wilhelt-zombies
  python new-deck.py simic-stompy

OUTPUT:
  C:\\MTG_Decks\\decks\\<deck-slug>\\
    decklist.md
    overview.md
    changelog.md
    session-handoff.md
    upgrade-candidates.md

Templates are read from C:\\MTG_Decks\\templates\\ and
C:\\repos\\MTG_Management\\templates\\ (repo templates take precedence
for any filename present in both locations).

The deck slug should be lowercase with hyphens — e.g. "ur-dragon",
not "UR Dragon" or "ur_dragon".
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import date

# ── Path configuration ────────────────────────────────────────────────────────

DECKS_ROOT     = Path(r"C:\MTG_Decks\decks")
DECK_TEMPLATES = Path(r"C:\MTG_Decks\templates")
REPO_TEMPLATES = Path(r"D:\repos\MTG_Management\templates")

# ── Template map ──────────────────────────────────────────────────────────────
# Maps output filename → template filename.
# Template lookup order: REPO_TEMPLATES first, then DECK_TEMPLATES.
# "decklist.md" uses no template — it is created as a blank stub.

TEMPLATE_MAP = {
    "overview.md":          "deck-readme.md",
    "changelog.md":         "changelog-template.md",
    "session-handoff.md":   "session-handoff-template.md",
    "upgrade-candidates.md":"upgrade-candidates.md",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def resolve_template(template_filename: str) -> Path | None:
    """Return the path to a template file, repo taking precedence over decks."""
    for base in (REPO_TEMPLATES, DECK_TEMPLATES):
        candidate = base / template_filename
        if candidate.exists():
            return candidate
    return None


def stamp_template(content: str, deck_slug: str, deck_title: str) -> str:
    """Replace placeholder tokens in template content."""
    today = date.today().strftime("%Y-%m-%d")
    replacements = {
        "[Deck Name]": deck_title,
        "[deck-slug]": deck_slug,
        "[YYYY-MM-DD]": today,
    }
    for token, value in replacements.items():
        content = content.replace(token, value)
    return content


def slug_to_title(slug: str) -> str:
    """Convert a hyphenated slug to a display title — e.g. 'ur-dragon' → 'Ur Dragon'."""
    return " ".join(word.capitalize() for word in slug.split("-"))

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print("Usage: python new-deck.py <deck-slug>")
        print('Example: python new-deck.py ur-dragon')
        sys.exit(1)

    deck_slug  = sys.argv[1].strip().lower()
    deck_title = slug_to_title(deck_slug)
    deck_dir   = DECKS_ROOT / deck_slug

    # ── Guard: deck already exists ────────────────────────────────────────────
    if deck_dir.exists():
        print(f"ERROR: Deck folder already exists: {deck_dir}")
        print("Rename or remove it before scaffolding.")
        sys.exit(1)

    print(f"\nScaffolding new deck: {deck_title} ({deck_slug})")
    print(f"Target directory: {deck_dir}\n")

    # ── Create deck directory ─────────────────────────────────────────────────
    deck_dir.mkdir(parents=True)
    print(f"  [+] Created {deck_dir}")

    # ── Create decklist.md stub ───────────────────────────────────────────────
    decklist_path = deck_dir / "decklist.md"
    decklist_path.write_text(
        f"# Decklist — {deck_title}\n\n"
        "Paste Moxfield 'Copy for Moxfield' export here.\n"
        "Replace this entire file contents — do not preserve this stub text.\n",
        encoding="utf-8",
    )
    print(f"  [+] Created decklist.md (stub)")

    # ── Create templated files ────────────────────────────────────────────────
    errors = []

    for output_filename, template_filename in TEMPLATE_MAP.items():
        output_path = deck_dir / output_filename

        template_path = resolve_template(template_filename)
        if template_path is None:
            errors.append(f"  [!] Template not found: {template_filename} — skipped {output_filename}")
            continue

        content = template_path.read_text(encoding="utf-8")
        content = stamp_template(content, deck_slug, deck_title)
        output_path.write_text(content, encoding="utf-8")
        print(f"  [+] Created {output_filename}  (from {template_path.parent.name}/{template_filename})")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if errors:
        print("Completed with warnings:")
        for e in errors:
            print(e)
    else:
        print("Done. Next steps:")
        print(f"  1. Open overview.md and fill in commander, bracket, strategy.")
        print(f"  2. Paste your Moxfield export into decklist.md.")
        print(f"  3. Run card-lookup.py --decklist decklist.md to generate _Card_Oracle.")
        print(f"  4. Start a session — load protocols + this deck's files.")

if __name__ == "__main__":
    main()
