# Input Contract

This document defines the format and handling rules for every input that gets passed into an AI-assisted deckbuilding session. All prompt and protocol files reference these definitions. If an input format changes, update this document first.

---
## Inputs Overview

|Variable|Source|Format|Required|
|---|---|---|---|
|`_Global_Inventory`|Moxfield full collection export|CSV|Yes|
|`_Current_Decklist`|`decklist.md` — populated from Moxfield "Copy for Moxfield" export|Markdown file|Yes|
|`_Bracket_Target`|Deck's `deck-readme.md`|Single value (1–5)|Yes|
|`_Session_Changelog`|Deck's `changelog.md`|Markdown|Recommended|
|`_Card_Oracle`|`card-lookup.py` output|Plain text block|Recommended|
|`_Web_Sources`|URLs or pasted guide text|Plain text / URLs|Optional|

---
## `_Global_Inventory`

**Source:** Moxfield full collection export (CSV)  
**Export path:** `inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv`  
**Do not rename** the export file — use the native Moxfield filename format. When multiple exports exist, the most recent datestamp is the active inventory. Scripts should glob for `moxfield_haves_*.csv` and sort by date to find the current file.

### Column Schema

These are the exact column headers produced by Moxfield's collection export:

|Column|Type|Notes|
|---|---|---|
|`Count`|Integer|Total copies owned across all decks and binders|
|`Tradelist Count`|Integer|Copies marked available for trade — not relevant for deckbuilding|
|`Name`|String|Card name — primary lookup key|
|`Edition`|String|Set code (e.g., `afr`, `cmm`) — not relevant for deckbuilding purposes|
|`Condition`|String|`Near Mint`, `Lightly Played`, etc.|
|`Language`|String|Typically `English`|
|`Foil`|String|`foil` if foil, empty string if non-foil|
|`Tags`|String|Per-card tags — **confirmed to not export** in Moxfield's collection CSV (tested June 2026). Tags are UI-only and cannot be relied upon in any automated or AI-assisted workflow. Always empty in exported data.|
|`Last Modified`|Datetime|Timestamp of last edit — not relevant for deckbuilding|
|`Collector Number`|String|Not relevant for deckbuilding|
|`Alter`|Boolean|`True` if the card is an alter — treat as owned for deckbuilding purposes|
|`Proxy`|Boolean|`True` if the card is a proxy — see proxy handling rules below|
|`Purchase Price`|Decimal|Original purchase price — not relevant for deckbuilding; reserved for future cost analysis|

### Proxy Handling Rules

The `Proxy` flag distinguishes physical proxies from real cards. Apply these rules during any inventory check:

- **Proxy = False:** Card is a real copy. Treat as `$0 cost` per the Zero-Cost Rule in `master-deckbuilding-logic.md`. Physical location (e.g., proxy binder vs. sleeved deck) cannot be determined from the CSV — the user must confirm availability if a card is likely committed elsewhere.
- **Proxy = True:** Card is a proxy. It is **physically playable** but should be flagged separately in upgrade candidate output. A proxied copy does not satisfy a "purchase needed" recommendation — the real card may still need to be acquired.

> **Note:** Moxfield tags do not export in the collection CSV (confirmed June 2026). Physical location tracking such as `proxybinder` status cannot be automated and must be confirmed manually during the session.

### Deduplication Note

The full collection export contains **one row per unique (Name, Edition, Foil, Condition) combination**, not one row per card name. A single card you own in multiple printings or conditions will appear as multiple rows.

For deckbuilding purposes, the AI should aggregate `Count` across all rows sharing the same `Name` to determine total owned copies. Example:

```
2x Sol Ring (cmm, Near Mint, non-foil)
1x Sol Ring (c21, Lightly Played, foil)
→ Total owned: 3 copies
```

> **Known optimization:** A post-export dedup script that collapses to unique card names with summed counts would reduce context overhead significantly (~7,400 rows in current export). This is a candidate for `scripts/inventory-check.py`. Until that script exists, pass the full CSV and rely on the aggregation rule above.

---
## `_Current_Decklist`

**Source:** `MTG_Decks/decks/[deck-name]/decklist.md`  
**Populated from:** Moxfield deck export — "Copy for Moxfield" format (see below)  
**Format:** Raw Moxfield export pasted into the file as-is — no stripping required  
**Used by:** Both `card-lookup.py` (oracle fetch) and the AI session (card name extraction)

### File Location

`decklist.md` lives in the deck's folder in `MTG_Decks/`:

```
MTG_Decks/decks/[deck-name]/decklist.md
```

This is a static filename — one file per deck, overwritten when the list changes. Moxfield remains the authoritative source; `decklist.md` is the local working copy.

### How to Update

1. Open the deck in Moxfield
2. Use **"Copy for Moxfield"** export (top option in the export menu)
3. Paste the output into `decklist.md`, replacing all previous content

### Moxfield Export Formats

Moxfield offers four export options. This system standardizes on **"Copy for Moxfield"** because it contains the most information and is the format `card-lookup.py` was built and validated against. The others are not used:

| Export Option | Format | Why Not Used |
|---|---|---|
| **Copy for Moxfield** ✓ | `1 Card Name (SET) 123 *F*` | **Canonical format for this system** |
| Copy for Arena | Includes deck name header and Arena-specific fields | Lossy — extra metadata, Arena-only cards |
| Copy for MTGO | `1 Card Name` with commander last, separated by blank line | Lossy — drops set/collector/foil data |
| Copy Plain Text | Same as MTGO format | Lossy — drops set/collector/foil data |

### Expected Format ("Copy for Moxfield")

```
Commander
1 Thranduil, King of Mirkwood (LTR) 200

Deck
1 Sol Ring (CMM) 451
1 Command Tower (CMM) 298
1 Arcane Signet (CMM) 263 *F*
1 Arid Mesa (MH3) 237 *E*
1 Titania's Song (NCC) 419
...
```

Key characteristics of this format:
- Count is a bare integer (no `x` suffix)
- Set code in parentheses — always 2–6 uppercase alphanumeric characters
- Collector number follows the set code — may be numeric (`451`) or alphanumeric (`NCC-419`)
- Foil markers appear as `*F*` or similar suffixes after the collector number
- Commander is listed first under its own section header
- DFC names use a slash separator: `Westvale Abbey // Ormendahl, Profane Prince`

### What the AI Ignores

The AI extracts card names only. The following fields are present in the file but ignored during session evaluation:

- Set codes
- Collector numbers
- Foil markers

These fields are used by `card-lookup.py` for parsing only and have no bearing on deckbuilding logic. Card names are unambiguous for evaluation purposes.

---
## `_Bracket_Target`

**Source:** Deck's `deck-readme.md` — the `Bracket` field  
**Format:** Single integer, 1 through 5

This value governs which rules from `bracket-constraints.md` apply for the entire session. The AI must confirm the bracket target at the start of every session before evaluating any upgrade candidate.

If `deck-readme.md` is not provided, the AI must ask for the bracket target before proceeding. Defaulting to Bracket 3 without confirmation is not permitted.

---
## `_Session_Changelog`

**Source:** Deck's `changelog.md`  
**Format:** Markdown (see `templates/changelog.md`)

The session changelog carries forward decisions from prior sessions. The AI must read this before making any suggestions and must honor these rules:

- **Do not suggest cards marked as OUT** in any prior session entry.
- **Do not suggest cards marked as IN** that are already in the current list.
- **Do not reverse a prior cut** without explicit instruction from the user.

If no changelog exists for a deck, note this at the start of the session and proceed without changelog constraints.

---
## `_Card_Oracle`

**Source:** Output of `scripts/card-lookup.py`  
**Format:** Plain text block (`_Card_Oracle` block as printed by the script)  
**Generated by:** `python card-lookup.py --decklist <moxfield-export>` before session start, or `--cards "Name" "Name"` for mid-session spot lookups  
**Data source:** Scryfall API — no auth required

### Purpose

The AI pattern-matches card names against training data, which is lossy and does not include post-cutoff cards. `_Card_Oracle` grounds all mechanical evaluation against verified oracle text fetched at session time, eliminating description errors caused by training memory drift.

### Contents

Each card entry includes: name, mana cost, CMC, type line, P/T or loyalty (where applicable), color identity, keywords, oracle text, and Commander legality flag. DFCs and split cards have face data merged with a `//` separator.

### Set-Agnostic Data

`_Card_Oracle` data is **printing-agnostic by design.** Set codes present in `_Current_Decklist` or `_Global_Inventory` are intentionally absent from `_Card_Oracle` — oracle text does not vary by printing, and set codes are discarded during lookup. A mismatch between set codes in other inputs and the absence of set codes in `_Card_Oracle` is expected and correct, not an error.

### Oracle Verification Rule

When `_Card_Oracle` is present:

- Oracle text from `_Card_Oracle` **supersedes** any card text recalled from training memory.
- Any candidate card suggested during the session that is **not present in `_Card_Oracle`** must be flagged as **unverified** before mechanical evaluation. Do not describe mechanics from memory for unverified cards without explicit user acknowledgment.

When `_Card_Oracle` is absent, the AI must note this at session start and rely on the manual Scryfall fallback: the user may paste individual oracle text blocks inline during the session as needed.

### Mid-Session Lookups

For cards added to consideration during a session (e.g., user-suggested additions, cards pulled from web sources), run:

```
python card-lookup.py --cards "Card Name" "Card Name"
```

Paste the output into the session as a supplemental `_Card_Oracle` block. The AI should treat supplemental blocks with the same authority as the initial block.

---
## `_Web_Sources`

**Source:** URLs or pasted text from guides (EDHREC, Command Zone, etc.)  
**Format:** Plain text, pasted inline, or as URLs for the AI to fetch  
**Handled by:** `prompts/web-guide-synthesis.md`

Web sources are optional context. They are only relevant when running a web guide synthesis pass. If no web sources are provided, skip Phase 3 (Web Guide Synthesis) of the upgrade path defined in `master-deckbuilding-logic.md` and note this to the user.

---
## Session Loading Checklist

Before beginning any deckbuilding session, confirm the following inputs are present:

- [ ] `_Global_Inventory` — collection CSV loaded
- [ ] `_Current_Decklist` — flat text decklist loaded
- [ ] `_Bracket_Target` — confirmed from `deck-readme.md`
- [ ] `_Session_Changelog` — loaded if it exists; absence noted if not
- [ ] `_Card_Oracle` — generated by `card-lookup.py --decklist` if available; absence noted if not, manual Scryfall fallback applies
- [ ] `protocols/master-deckbuilding-logic.md` — loaded
- [ ] `protocols/bracket-constraints.md` — loaded

If any required input is missing, pause and request it before proceeding.
