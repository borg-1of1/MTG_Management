# Starting a Session

This guide covers how to load your files and initiate an AI-assisted session against
an existing deck. Use this guide when starting a fresh session — either the deck has
no prior session handoff, or enough time has passed that you want to re-orient the AI
from scratch rather than resume from a handoff.

If you have a recent session-handoff.md and want to resume mid-cycle, see
`guides/continuing-a-session.md` instead.

---

## When to Use This Guide

- First session against a deck that has completed initial setup (overview.md populated,
  decklist.md current, changelog.md exists)
- Returning to a deck after a long gap where the handoff file may be stale
- Starting a new upgrade cycle after a prior cycle completed cleanly
- Running a periodic review with no specific upgrade phase in progress

---

## What to Prepare Before You Start

### 1. Confirm your decklist is current

Before loading anything into an AI session, verify that your `decklist.md` matches
your current Moxfield decklist. If you made physical changes since the last session
that are not reflected in Moxfield, sync Moxfield first. The AI works from what is
in the files — if the decklist is stale, the session output will be stale.

### 2. Export a fresh inventory CSV if needed

If your collection has changed since your last export, pull a new CSV from Moxfield
Haves before the session. Save it to `MTG_Decks/inventory/` without renaming it.
The workflow uses the most recent datestamped file automatically.

### 3. Know your goal for the session

The protocol files define five upgrade phases and a review path. Before you start,
have a rough sense of what you want to accomplish:

- **Full deck review** — use `prompts/deck-review-prompt.md`. Good for periodic
  check-ins, decks returning from a long gap, or decks you have not run through
  the workflow before.
- **Upgrade session** — use `prompts/deck-review-prompt.md` to orient, then proceed
  through the upgrade phases defined in `protocols/master-deckbuilding-logic.md`.
  Start at Phase 1 unless a prior session confirmed the land base is already optimized.
- **Targeted upgrade** — if a prior review identified a specific gap, you can skip
  directly to Phase 2 and scope the session to that gap. Note this in your starter
  prompt so the AI does not re-run the full diagnostic.

---

## Files to Load

Load these files into your AI assistant before sending your starter prompt. Most AI
assistants accept file uploads or pasted text — either works.

### Always load (every session)

```
From MTG_Management/:
    protocols/master-deckbuilding-logic.md
    protocols/bracket-constraints.md
    protocols/input-contract.md

From MTG_Decks/:
    decks/[deck-name]/overview.md
    decks/[deck-name]/decklist.md
    decks/[deck-name]/changelog.md
    inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv
```

### Load based on session goal

```
Full deck review:
    prompts/deck-review-prompt.md
    decks/[deck-name]/mechanics-notes.md  (if it exists for this deck)

Upgrade session (Phase 3 — web synthesis):
    prompts/web-guide-synthesis.md
    (plus any web guides or EDHREC pages you want synthesized)

Pre-sync audit or session close:
    prompts/comparison-logic.md

Targeted upgrade (Phase 2 only):
    No additional prompt file needed — master-deckbuilding-logic.md drives Phase 2
```

---

## How the AI Uses These Files

The protocol files (`master-deckbuilding-logic.md`, `bracket-constraints.md`,
`input-contract.md`) are standing instructions — the AI applies them throughout the
entire session regardless of which prompt is active. Load them every time.

The prompt files are task drivers — they tell the AI what specific job to do. Load
only the prompt that matches your session goal.

The deck files provide the working context. The changelog is especially important —
the AI reads it to identify binding constraints (cards that were previously cut or
rejected cannot be suggested again without your explicit instruction).

---

## The Phase Gate Rule

The upgrade path defined in `master-deckbuilding-logic.md` is divided into five phases.
The AI will not advance from one phase to the next without your explicit confirmation.
At the end of each phase it will present output and wait.

This is intentional. Each phase boundary is a checkpoint where you can:
- Review what was proposed
- Update Moxfield before continuing
- Make physical changes to your deck
- End the session and pick up later

You are always in control of the pace. The AI waits for you.

---

## Starter Prompt — Starting a Fresh Session

The following prompt is designed for a session against a deck with an existing file
set and changelog. Copy it into your AI assistant, fill in the bracketed fields, and
attach or paste the listed files before sending.

Adapt the wording to suit your goal — the session goal block is where you tell the AI
what you want to accomplish.

---

```
I am starting an AI-assisted deck session using the MTG Management workflow. I am
providing the workflow files from my MTG_Management repository and the deck files
from my MTG_Decks vault. Please read all loaded files carefully before responding.

## Files Loaded

From MTG_Management/:
- protocols/master-deckbuilding-logic.md
- protocols/bracket-constraints.md
- protocols/input-contract.md
- prompts/[prompt-file-name].md

From MTG_Decks/:
- decks/[deck-name]/overview.md
- decks/[deck-name]/decklist.md
- decks/[deck-name]/changelog.md
- decks/[deck-name]/mechanics-notes.md  [remove this line if file does not exist]
- inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv

## Ground Rules

1. Read all loaded protocol files as standing instructions before doing anything else.
2. Confirm the bracket target from overview.md before any evaluation begins.
3. Read changelog.md and apply all confirmed OUT and Rejected entries as binding
   constraints before making any suggestions.
4. Do not suggest YAML frontmatter. Plain Markdown only throughout.
5. Do not embed or reconstruct the Game Changers list from memory. GC status is
   verified against the Moxfield [REF] Game Changers list.
6. GC tracking lives in master-deckbuilding-logic.md. Do not restate GC rules in
   any output you produce.
7. The phase gate rule is non-negotiable. Wait for my confirmation before advancing
   between phases.
8. Inventory cards are always preferred over purchase recommendations at equivalent
   power level. Label every recommendation as [Inventory — $0] or [Purchase — ~$X].

## Session Goal

[Describe what you want to accomplish. Examples:]

[For a full review:]
Run a full periodic deck review using deck-review-prompt.md. The deck has been in
service since [date of last upgrade]. Treat the diagnostic as forward-looking —
assess current health, surface any gaps, and produce recommendations. Do not begin
an upgrade phase unless I confirm after reviewing the output.

[For a targeted upgrade:]
The last review identified an interaction gap as an Address-level priority. Skip the
full diagnostic and open a Phase 2 upgrade session scoped to interaction. The
following candidates were already identified and confirmed owned — evaluate these
for inclusion and identify appropriate cuts:
- [Card 1] [Inventory — $0]
- [Card 2] [Inventory — $0]
- [Card 3] [Inventory — $0]

[For a full upgrade cycle starting at Phase 1:]
Run a full upgrade cycle starting at Phase 1 — Land and Mana. Work through the
phases in order and wait for my confirmation at each phase gate before continuing.

## First Task

Before any work begins, confirm you have read all loaded files and state:
1. The bracket target
2. Current GC slot usage
3. Any binding constraints from the changelog
4. The session goal you will be pursuing
```
