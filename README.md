# MTG Management  

This repository is the workflow engine for my MTG deck management system. It contains the rules, prompts, and templates that drive AI-assisted deck building and upgrade sessions. Deck files themselves live in the Obsidian vault; this repo is the **logic layer** that governs how those sessions are run.  

> **Rule of thumb:** If you were establishing how the AI should *think*, it's a Protocol. If you were telling it what to *do*, it's a Prompt.  

---
## Repo Structure
  

```
MTG_Management/
├── README.md                          # This file — authoritative source for structure
├── decks/
│   └── deck-name/
│       ├── overview.md                # Commander, theme, Bracket rating
│       ├── decklist.md                # Current list
│       ├── changelog.md               # What changed and why (populated from template)
│       ├── upgrade-candidates.md      # Researched options, tiered (populated from template)
│       └── session-handoff.md         # AI session state carry-forward (populated from template)
|
├── cards/
│   └── [optional per-card notes for heavily-used pieces]
|
├── docs/
│   ├── mtg-deck-management.md         # Moxfield organization system — human reference
│   └── inventory-notes.md             # Inventory quirks, proxies, condition flags
|
├── inventory/
│   └── moxfield_haves_[YYYY-MM-DD-HHmmZ].csv  # Raw export — retain native filename
|
├── protocols/
│   ├── master-deckbuilding-logic.md   # Core evaluation framework — always-on rules
│   ├── input-contract.md              # Defines _Global_Inventory and Current_Decklist format
│   └── bracket-constraints.md         # Bracket guardrails for all five brackets
|
├── prompts/
│   ├── web-guide-synthesis.md         # Task: audit and extract web source recommendations
│   ├── comparison-logic.md            # Task: pre-sync audit of current vs. starting deck state
│   └── deck-review-prompt.md          # Task: full deck review and upgrade pass
|
├── templates/
│   ├── changelog.md                   # template; copy → decks/[deck-name]/changelog.md
│   ├── deck-readme.md                 # template; copy → decks/[deck-name]/overview.md
│   ├── upgrade-candidates.md          # template; copy → decks/[deck-name]/upgrade-candidates.md
│   └── session-handoff.md             # template; copy → decks/[deck-name]/session-handoff.md
|
└── scripts/
    └── inventory-check.py             # CSV cross-reference automation
```

---
## Protocols

Protocols are **always-on rules**. Every AI session loads the relevant protocol files as standing instructions. The AI is expected to honor these throughout the task regardless of which prompt is active.

| File                           | Purpose                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| `master-deckbuilding-logic.md` | Core evaluation framework: land base first, tiered upgrade path, inventory priority   |
| `input-contract.md`            | Defines the expected format of `_Global_Inventory` and `Current_Decklist` inputs      |
| `bracket-constraints.md`       | Guardrail rules for all five brackets; governs upgrade evaluation and auto-exclusions |

---
## Prompts

Prompts are **task-specific triggers**. Load one when you are running that particular job. These are not standing rules — they drive a specific output.

| File                     | Purpose                                                                                      |
| ------------------------ | -------------------------------------------------------------------------------------------- |
| `web-guide-synthesis.md` | Audits attached web sources and extracts recommendations, cross-referenced against inventory |
| `comparison-logic.md`    | Runs a pre-sync audit comparing the current deck state to the starting version               |
| `deck-review-prompt.md`  | Full deck review and upgrade pass                                                            |

---
## Templates

Templates are **blank reusable formats**. Copy the relevant template into a deck folder and populate it. The version inside `templates/` should always remain blank.

| File                    | Deploys To                                |
| ----------------------- | ----------------------------------------- |
| `changelog.md`          | `decks/[deck-name]/changelog.md`          |
| `deck-readme.md`        | `decks/[deck-name]/overview.md`           |
| `upgrade-candidates.md` | `decks/[deck-name]/upgrade-candidates.md` |
| `session-handoff.md`    | `decks/[deck-name]/session-handoff.md`    |

---
## Docs

The `docs/` folder contains human reference material that governs how the system is operated. These files are not loaded into AI sessions — they exist for the operator.

|File|Purpose|
|---|---|
|`mtg-deck-management.md`|Moxfield folder structure, deck naming conventions, lifecycle prefixes, and proxy library rules|
|`inventory-notes.md`|Notes on inventory quirks, proxy status, condition flags, and known anomalies in the CSV|

---
## Workflows

Use these as a loading guide — which files to feed an AI assistant for each task.

### Upgrade a Deck

```
Load: protocols/master-deckbuilding-logic.md
      protocols/bracket-constraints.md
      protocols/input-contract.md
      prompts/web-guide-synthesis.md
      decks/[deck-name]/overview.md
      decks/[deck-name]/decklist.md
      decks/[deck-name]/upgrade-candidates.md
      inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv
```
### Pre-Sync Audit

```
Load: protocols/master-deckbuilding-logic.md
      protocols/bracket-constraints.md
      prompts/comparison-logic.md
      decks/[deck-name]/decklist.md
      decks/[deck-name]/changelog.md
```
### Full Deck Review

```
Load: protocols/master-deckbuilding-logic.md
      protocols/bracket-constraints.md
      protocols/input-contract.md
      prompts/deck-review-prompt.md
      decks/[deck-name]/overview.md
      decks/[deck-name]/decklist.md
      inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv
```

---
## Notes

- **Moxfield CSV:** Retain the native Moxfield export filename (`moxfield_haves_[YYYY-MM-DD-HHmmZ].csv`). Do not rename on ingest. When multiple exports exist in `inventory/`, the most recent datestamp is the active file.
- **Obsidian config:** The `.obsidian/` folder should be excluded via `.gitignore` — workspace state and appearance settings are local and do not belong in version control.
- **Authoritative Structure:** This README is the authoritative source for repo structure. If any other document references a folder or file layout, this document takes precedence.
- **Naming Convention:** All files and folders use hyphens, not underscores. Exception: Moxfield CSV exports retain their native datestamped filename format.