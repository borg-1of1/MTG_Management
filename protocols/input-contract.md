# Input Contract

This document defines the format and handling rules for every input that gets passed into an AI-assisted deckbuilding session. All prompt and protocol files reference these definitions. If an input format changes, update this document first.

---
## Inputs Overview

|Variable|Source|Format|Required|
|---|---|---|---|
|`_Global_Inventory`|Moxfield full collection export|CSV|Yes|
|`_Current_Decklist`|Moxfield deck text export|Plain text|Yes|
|`_Bracket_Target`|Deck's `deck-readme.md`|Single value (1–5)|Yes|
|`_Session_Changelog`|Deck's `changelog.md`|Markdown|Recommended|
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

**Source:** Moxfield deck text export (flat list format)  
**Format:** One card per line in the form `[Count]x [Card Name]`

### Expected Format

```
1x Sol Ring
1x Command Tower
1x Arcane Signet
37x Forest
...
```

### Sections

Moxfield's text export separates the decklist into sections with headers. Preserve these headers when passing the decklist — they provide structural context:

```
Commander
1x Atraxa, Praetors' Voice

Deck
1x Sol Ring
1x Command Tower
...

Sideboard (if present)
```

### What to Omit

The following are **not needed** for deckbuilding sessions and should be omitted if present:

- Set codes in parentheses (e.g., `1x Sol Ring (CMM) 175`)
- Collector numbers
- Foil indicators
- Price data

The plain name list is sufficient. Card names are unambiguous for deckbuilding purposes.

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
- [ ] `protocols/master-deckbuilding-logic.md` — loaded
- [ ] `protocols/bracket-constraints.md` — loaded

If any required input is missing, pause and request it before proceeding.
