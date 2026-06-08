# MTG Management

This repository is the workflow engine for my MTG deck management system. It contains the rules, prompts, and templates that drive AI-assisted deck building and upgrade sessions. Deck files themselves live in a companion Obsidian vault (`MTG_Decks`); this repo is the **logic layer** that governs how those sessions are run.

> **Rule of thumb:** If you are establishing how the AI should *think*, it belongs in a Protocol. If you are telling it what to *do*, it belongs in a Prompt.

---
## System Overview

This system is split across two roots. They are kept separate by design — the logic layer is stable and version controlled; the working layer is active and session-driven.

| Root | Purpose | Versioned? |
|---|---|---|
| `MTG_Management/` | Workflow engine — protocols, prompts, templates, scripts | Yes — GitHub |
| `MTG_Decks/` | Working directory — decks, inventory, collection notes | No — local only |

Templates live in the repo. When starting a new deck, copy the relevant templates from `MTG_Management/templates/` into a new folder under `MTG_Decks/decks/`. The repo copy stays blank and reusable.

Moxfield is the authoritative source for decklists and inventory. The repo and vault are workflow tooling, not card databases.

---
## Repo Structure (`MTG_Management/`)

```
MTG_Management/
├── README.md                          # This file — authoritative source for structure
│
├── docs/
│   └── mtg-deck-management.md         # Moxfield organization system — human reference
│
├── protocols/
│   ├── master-deckbuilding-logic.md   # Core evaluation framework — always-on rules
│   ├── input-contract.md              # Defines _Global_Inventory and _Current_Decklist format
│   └── bracket-constraints.md        # Bracket guardrails for all five brackets
│
├── prompts/
│   ├── web-guide-synthesis.md         # Task: audit and extract web source recommendations
│   ├── comparison-logic.md            # Task: pre-sync audit of current vs. starting deck state
│   └── deck-review-prompt.md          # Task: full deck review and upgrade pass
│
├── guides/
│   ├── getting-started.md             # First-time setup and first session walkthrough
│   ├── starting-a-session.md          # How to load files and initiate a fresh session
│   └── continuing-a-session.md        # How to resume from a session handoff file
│
├── templates/
│   ├── changelog.md                   # template; copy → MTG_Decks/decks/[deck-name]/changelog.md
│   ├── deck-readme.md                 # template; copy → MTG_Decks/decks/[deck-name]/overview.md
│   ├── upgrade-candidates.md          # template; copy → MTG_Decks/decks/[deck-name]/upgrade-candidates.md
│   └── session-handoff.md             # template; copy → MTG_Decks/decks/[deck-name]/session-handoff.md
│
└── scripts/
    └── inventory-check.py             # CSV cross-reference automation
```

---
## Vault Structure (`MTG_Decks/`)

```
MTG_Decks/
├── decks/
│   └── deck-name/
│       ├── overview.md                # Commander, theme, bracket target
│       ├── decklist.md                # Current list — Moxfield is authoritative
│       ├── changelog.md               # Append-only session ledger (populated from template)
│       ├── upgrade-candidates.md      # Researched options, tiered (populated from template)
│       ├── session-handoff.md         # AI session state carry-forward (populated from template)
│       └── mechanics-notes.md         # Deck-specific interaction rulings — not in template set
│
├── inventory/
│   └── moxfield_haves_[YYYY-MM-DD-HHmmZ].csv  # Raw Moxfield export — retain native filename
│
├── cards/
│   └── [optional per-card notes for heavily-used pieces]
│
└── collection-notes/
    └── inventory-notes.md             # Inventory quirks, proxy flags, condition anomalies, scratchpad
```

> `mechanics-notes.md` is a deck-specific file for complex interaction rulings. It is not part of the standard template set and is created only when needed.

---
## Protocols

Protocols are **always-on rules**. Every AI session loads the relevant protocol files as standing instructions. The AI honors these throughout the session regardless of which prompt is active.

| File | Purpose |
|---|---|
| `master-deckbuilding-logic.md` | Core evaluation framework: land base first, tiered upgrade path, inventory priority |
| `input-contract.md` | Defines the expected format of `_Global_Inventory` and `_Current_Decklist` inputs |
| `bracket-constraints.md` | Guardrail rules for all five brackets; governs upgrade evaluation and auto-exclusions |

---
## Prompts

Prompts are **task-specific triggers**. Load one when running that particular job. These are not standing rules — they drive a specific output.

| File | Purpose |
|---|---|
| `web-guide-synthesis.md` | Audits attached web sources and extracts recommendations, cross-referenced against inventory |
| `comparison-logic.md` | Runs a pre-sync audit comparing the current deck state to the starting version |
| `deck-review-prompt.md` | Full deck review and upgrade pass |

---
## Guides

Guides are **operator-facing how-to documents**. They are not loaded into AI sessions —
they exist to help you use the workflow correctly. Each guide includes a ready-to-use
starter prompt you can copy directly into your AI assistant or adapt to your own style.

| File | Purpose |
|---|---|
| `getting-started.md` | First-time setup: repo, vault, card management tool, and first deck |
| `starting-a-session.md` | How to load files and initiate a fresh session against an existing deck |
| `continuing-a-session.md` | How to resume mid-cycle from a session handoff file |

> New to this workflow? Start with `guides/getting-started.md`.

---
## Templates

Templates are **blank reusable formats**. Copy the relevant template into a deck folder under `MTG_Decks/decks/` and populate it. The version inside `templates/` should always remain blank.

| File | Deploys To |
|---|---|
| `changelog.md` | `MTG_Decks/decks/[deck-name]/changelog.md` |
| `deck-readme.md` | `MTG_Decks/decks/[deck-name]/overview.md` |
| `upgrade-candidates.md` | `MTG_Decks/decks/[deck-name]/upgrade-candidates.md` |
| `session-handoff.md` | `MTG_Decks/decks/[deck-name]/session-handoff.md` |

---
## Docs

The `docs/` folder contains human reference material that governs how the system is operated. These files are not loaded into AI sessions — they exist for the operator.

| File | Purpose |
|---|---|
| `mtg-deck-management.md` | Moxfield folder structure, deck naming conventions, lifecycle prefixes, and proxy library rules |

> Personal collection-specific notes and scratchpad content live in `MTG_Decks/collection-notes/`, not here. `docs/` contains system documentation useful to any operator of this workflow. Collection-specific notes (inventory quirks, proxy flags, condition anomalies) are personal to a given user and belong in the vault.

---
## Workflows

Use these as a loading guide — which files to feed an AI assistant for each task. Deck files are loaded from `MTG_Decks/`; protocol and prompt files are loaded from `MTG_Management/`.

### Upgrade a Deck

```
From MTG_Management/:
      protocols/master-deckbuilding-logic.md
      protocols/bracket-constraints.md
      protocols/input-contract.md
      prompts/web-guide-synthesis.md

From MTG_Decks/:
      decks/[deck-name]/overview.md
      decks/[deck-name]/decklist.md
      decks/[deck-name]/upgrade-candidates.md
      decks/[deck-name]/changelog.md
      inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv
```

### Pre-Sync Audit

```
From MTG_Management/:
      protocols/master-deckbuilding-logic.md
      protocols/bracket-constraints.md
      prompts/comparison-logic.md

From MTG_Decks/:
      decks/[deck-name]/decklist.md
      decks/[deck-name]/changelog.md
```

### Full Deck Review

```
From MTG_Management/:
      protocols/master-deckbuilding-logic.md
      protocols/bracket-constraints.md
      protocols/input-contract.md
      prompts/deck-review-prompt.md

From MTG_Decks/:
      decks/[deck-name]/overview.md
      decks/[deck-name]/decklist.md
      decks/[deck-name]/changelog.md
      inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv
```

---
## Replicating This System

Setting up this workflow requires four things: downloading the repository, creating a
companion folder for your deck files, setting up a card management tool with a
collection export, and copying the templates into your first deck folder. The process
takes about 15–30 minutes for initial setup and another 10–15 minutes per new deck
added afterward.

No coding experience is required. You do not need to use Git or the command line —
the repository can be downloaded as a ZIP file from GitHub. The workflow runs entirely
in plain Markdown files and your AI assistant of choice.

> For the full step-by-step setup guide, see `guides/getting-started.md`. That document
> is the authoritative source for setup instructions and includes a starter prompt for
> your first session.

---
## Notes

- **Naming convention:** All files and folders use hyphens, not underscores. Exception: Moxfield CSV exports retain their native datestamped filename format (`moxfield_haves_[YYYY-MM-DD-HHmmZ].csv`).
- **Moxfield CSV:** Do not rename on ingest. When multiple exports exist in `inventory/`, the most recent datestamp is the active file. Scripts glob for `moxfield_haves_*.csv` and sort by date.
- **Moxfield tags:** Tags do not export in Moxfield's collection CSV (confirmed June 2026). They are UI-only and cannot be relied upon in automated or AI-assisted workflows.
- **Plain Markdown only:** No YAML frontmatter anywhere in this system. All files use plain Markdown for frontend agnosticism.
- **Authoritative structure:** This README is the authoritative source for repo and vault structure. If any other document references a folder or file layout, this document takes precedence.
- **Obsidian config:** The `.obsidian/` folder is excluded via `.gitignore` — workspace state and appearance settings are local and do not belong in version control. Since the vault is now a separate directory from the repo, this entry is retained for safety but is effectively inert.
