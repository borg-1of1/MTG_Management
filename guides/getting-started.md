# Getting Started

This guide walks you through setting up the MTG Management workflow for the first time.
By the end you will have the two-root structure in place, a deck file set ready to go,
and a starter prompt you can use to run your first AI-assisted deck session.

---

## What This System Is

This workflow is a set of rules, prompts, and templates that govern how you run
AI-assisted Magic: The Gathering deck building and upgrade sessions. It is not a deck
tracker or card database — Moxfield handles that. Think of it as the playbook your AI
assistant follows when you sit down to work on a deck.

The system is split across two locations by design:

- **MTG_Management** — the workflow engine. This is the repository you downloaded from
  GitHub. It contains the rules (protocols), task instructions (prompts), and blank
  file formats (templates). This folder is stable — you update it when the workflow
  itself changes, not when your decks change.

- **MTG_Decks** — your working directory. This is a folder you create on your own
  machine. It holds your deck files, your card inventory export, and your session
  notes. The folder structure itself is stable once created — what changes is the
  content inside it as you work on decks, update inventory exports, and log sessions.

These two locations are kept separate on purpose. Your deck files are personal and
session-driven. The workflow logic is reusable across any deck and any player.

---

## Step 1 — Get the Repository

Download the MTG_Management repository from GitHub and place it somewhere on your
local machine where you can find it easily. A folder like `Documents/MTG` works well.

You do not need to use Git or the command line if you are not comfortable with those
tools. GitHub allows you to download the entire repository as a ZIP file from the
main repository page. Unzip it and you have everything you need.

> If you are comfortable with Git, cloning the repository gives you the ability to pull
> updates as the workflow evolves. Either approach works.

---

## Step 2 — Create Your Vault

Create a folder called `MTG_Decks` on your local machine. Place it alongside
MTG_Management, not inside it — they should be siblings, not nested.

Inside MTG_Decks, create these four subfolders:

```
MTG_Decks/
├── decks/
├── inventory/
├── cards/
└── collection-notes/
```

If you use Obsidian as your note-taking tool, open this folder as a vault. The workflow
is plain Markdown throughout — no Obsidian-specific features are required, and the files
will work in any text editor. Obsidian is a convenient front end, not a requirement.

---

## Step 3 — Set Up Your Card Management Tool

This workflow was built around Moxfield and is documented with Moxfield in mind. That
said, any web-based card management tool that can export your collection as a CSV should
work. Use whatever tool you are comfortable with. If you use something other than
Moxfield, you may need to adapt the column references in `protocols/input-contract.md`
to match your tool's export format — the card Name and Count columns are what the
workflow relies on most heavily.

If you are using Moxfield, you will need:

- A Moxfield account with your collection entered under **Collection**
- A reference list called **[REF] Game Changers** under **LIBRARY/Tools** — this is a
  manually maintained copy of the official WotC Commander Game Changers list. During
  sessions, this list is the source of truth for whether a card is a Game Changer.
  Keep it synced when WotC publishes updates.

`docs/mtg-deck-management.md` in the repository documents one specific Moxfield folder
structure, deck naming convention, and lifecycle prefix system. Treat it as a reference
and starting point — adapt it to your own tool and organizational preferences rather
than following it prescriptively. The goal is a system that makes sense to you.

---

## Step 4 — Set Up Your First Deck

For each deck you want to manage with this workflow, create a folder under
`MTG_Decks/decks/` using the deck name with hyphens, not spaces or underscores.
Example: `MTG_Decks/decks/mutant-menace/`

Copy the four template files from `MTG_Management/templates/` into that folder:

| Template file | Rename to |
|---|---|
| `deck-readme.md` | `deck-readme.md` |
| `changelog.md` | `changelog.md` |
| `upgrade-candidates.md` | `upgrade-candidates.md` |
| `session-handoff.md` | `session-handoff.md` |

Open `overview.md` and fill in the Identity section: commander name, color identity,
bracket target, origin, and your Moxfield deck URL. The bracket target is the single
most important field — every card evaluation during sessions is filtered against it.

If your deck has complex interactions that need rulings, create a `mechanics-notes.md`
file in the deck folder. This is not required for every deck — only create it when you
have interactions that are ambiguous enough to be worth documenting.

---

## Step 5 — Export Your Inventory

Export your collection as a CSV from the Collection section of your card management
tool. Save it to `MTG_Decks/inventory/` using the filename your tool generates — do
not rename it. If you are using Moxfield, the filename format is
`moxfield_haves_[YYYY-MM-DD-HHmmZ].csv`.

When you export a new copy, keep the old ones in the folder. The workflow always uses
the most recent datestamped file. Old exports serve as a historical record.

> **Note:** Moxfield tags do not appear in the CSV export — they are display-only in
> the Moxfield interface. Physical location tracking (proxy binders, deck boxes) cannot
> be automated and must be confirmed manually during sessions.

---

## You Are Ready

Once Steps 1–5 are complete you have everything needed to run a session. The next step
is loading your files into an AI assistant and starting work.

See `guides/starting-a-session.md` for how to load files and run your first session
against a deck, and the starter prompt at the end of this guide for a copy-paste
starting point.

---

## Starter Prompt — First Session on a New Deck

The following prompt is designed for your very first session against a deck that has
no prior session history. Copy it into your AI assistant, fill in the bracketed fields,
and attach or paste the listed files before sending.

Adapt the wording to suit your style — this is a starting point, not a script.

---

```
I am starting my first AI-assisted deck building session using the MTG Management
workflow. I am providing the workflow files from the MTG_Management repository and
my deck files from my MTG_Decks vault. Please read all loaded files carefully before
responding.

## Files Loaded

From MTG_Management/:
- protocols/master-deckbuilding-logic.md
- protocols/bracket-constraints.md
- protocols/input-contract.md
- prompts/deck-review-prompt.md

From MTG_Decks/:
- decks/[deck-name]/overview.md
- decks/[deck-name]/decklist.md
- inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv

## Context

This is the first session for this deck using this workflow. There is no prior
changelog or session handoff — do not apply changelog constraints and note the
absence at initialization.

The deck is [brief description — e.g., "a Bracket 3 proliferate and counters deck
built around The Wise Mothman"].

## Ground Rules

1. Read all loaded protocol files as standing instructions before doing anything else.
2. Confirm the bracket target from overview.md before any evaluation begins.
3. Do not suggest YAML frontmatter. Plain Markdown only throughout.
4. Do not embed or reconstruct the Game Changers list from memory. GC status is
   verified against the Moxfield [REF] Game Changers list.
5. GC tracking lives in master-deckbuilding-logic.md. Do not restate GC rules in
   any output you produce.
6. The phase gate rule is non-negotiable. Wait for my confirmation before advancing
   between phases.
7. Inventory cards are always preferred over purchase recommendations at equivalent
   power level. Label every recommendation as [Inventory — $0] or [Purchase — ~$X].

## First Task

Run a full deck review using deck-review-prompt.md. This is a periodic review —
the deck has not been through this workflow before. Treat the diagnostic as
forward-looking: assess current health, surface gaps, and produce recommendations.

Do not begin any work until you confirm you have read all loaded files and state
the bracket target and GC budget status.
```
