# Continuing a Session

This guide covers how to resume an AI-assisted session using a session handoff file.
Use this guide when you have a recent `session-handoff.md` for the deck and want to
pick up where you left off without re-running initialization from scratch.

If you are starting fresh — no handoff file, long gap since the last session, or
beginning a new upgrade cycle — see `guides/starting-a-session.md` instead.

---

## When to Use This Guide

- Resuming a session that ended mid-upgrade-cycle (phase gate was reached but not all
  phases were completed)
- Starting a new session to execute an upgrade recommended in a prior review
- Picking up within a few days of a prior session where the handoff file is current
  and the decklist has not changed

---

## What to Check Before You Load

### 1. Is the handoff file current?

Open `session-handoff.md` for the deck. Check the Last Session Date. If significant
time has passed — a month or more, a new set release, or notable collection changes —
consider using `guides/starting-a-session.md` instead and running a fresh review
before resuming the upgrade path. A stale handoff can carry forward outdated context.

### 2. Is the decklist still accurate?

If you made any changes to the physical deck or in Moxfield since the last session,
update `decklist.md` to match before loading it. The handoff file's Context Notes
section should describe any pending physical updates — if those are now done, note
that when you start the session so the AI does not flag them as outstanding.

### 3. Has your inventory changed?

If you acquired or traded away cards since the last export, pull a fresh CSV from
Moxfield Haves and save it to `MTG_Decks/inventory/` before the session.

---

## Files to Load

### Always load (every session)

```
From MTG_Management/:
    protocols/master-deckbuilding-logic.md
    protocols/bracket-constraints.md
    protocols/input-contract.md

From MTG_Decks/:
    decks/[deck-name]/session-handoff.md
    decks/[deck-name]/overview.md
    decks/[deck-name]/decklist.md
    decks/[deck-name]/changelog.md
    inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv
```

### Load based on where you are in the cycle

```
Resuming at Phase 3 — web synthesis:
    prompts/web-guide-synthesis.md
    (plus any web guides or EDHREC pages to synthesize)

Running a pre-sync audit or closing out a phase:
    prompts/comparison-logic.md

Picking up a review recommendation (targeted Phase 2 upgrade):
    No additional prompt needed — master-deckbuilding-logic.md drives Phase 2

If mechanics-notes.md exists for this deck:
    decks/[deck-name]/mechanics-notes.md
```

---

## How the Handoff File Works

The session handoff file is a single-file snapshot of where the deck stands at the
end of a session. It carries:

- The current phase and session status
- Any confirmed swaps that have not yet been made physically
- Active constraints beyond the standard changelog rules
- The specific goals and card candidates for the next session
- Any open questions that need resolving before or during the session

The AI reads the handoff file at the start of the session and uses it to orient
without re-running the full initialization sequence. The handoff does not replace
the changelog — it is a working document that gets overwritten each session.
The changelog is the permanent record.

At the end of a continuing session, the handoff file should be updated to reflect
the new current state. If the session completes a phase and opens the next one, the
handoff carries forward what the next session needs to know.

---

## What the AI Should Do at Session Start

When you load a handoff file, the AI should:

1. Confirm it has read the handoff and summarize the current state — phase, status,
   and next session goals as documented
2. Flag any conflict between the handoff and the other loaded files (e.g., decklist
   changes not reflected in the handoff's context notes)
3. State the bracket target and GC budget
4. Confirm active changelog constraints
5. Wait for your confirmation before beginning work

If any of those steps are missing from the AI's opening response, prompt it to
complete them before proceeding.

---

## Starter Prompt — Continuing from a Handoff

The following prompt is designed for resuming a session using a handoff file. Copy
it into your AI assistant, fill in the bracketed fields, and attach or paste the
listed files before sending.

---

```
I am continuing an AI-assisted deck session using the MTG Management workflow.
I am providing a session handoff file that carries full context from the prior
session. Please read it carefully before responding — it is the authoritative
source for current session state.

## Files Loaded

From MTG_Management/:
- protocols/master-deckbuilding-logic.md
- protocols/bracket-constraints.md
- protocols/input-contract.md
- prompts/[prompt-file-name].md  [include only if running Phase 3 or comparison-logic]

From MTG_Decks/:
- decks/[deck-name]/session-handoff.md
- decks/[deck-name]/overview.md
- decks/[deck-name]/decklist.md
- decks/[deck-name]/changelog.md
- decks/[deck-name]/mechanics-notes.md  [remove this line if file does not exist]
- inventory/moxfield_haves_[YYYY-MM-DD-HHmmZ].csv

## Ground Rules

1. The session handoff file is the authoritative source for current session state.
   If anything I say conflicts with it, flag the conflict rather than silently
   choosing one over the other.
2. Read all loaded protocol files as standing instructions before doing anything else.
3. Read changelog.md and apply all confirmed OUT and Rejected entries as binding
   constraints. The handoff may also carry short-term Cards to Avoid — apply those
   as well.
4. Do not suggest YAML frontmatter. Plain Markdown only throughout.
5. Do not embed or reconstruct the Game Changers list from memory. GC status is
   verified against the Moxfield [REF] Game Changers list.
6. GC tracking lives in master-deckbuilding-logic.md. Do not restate GC rules in
   any output you produce.
7. The phase gate rule is non-negotiable. Wait for my confirmation before advancing
   between phases.
8. Inventory cards are always preferred over purchase recommendations at equivalent
   power level. Label every recommendation as [Inventory — $0] or [Purchase — ~$X].

## Session Context

[Optional — add any context the handoff does not already capture. Examples:]

[If the decklist changed since the handoff:]
The decklist has been updated since the last session — [brief description of what
changed]. Treat the loaded decklist.md as current.

[If inventory has been updated:]
I exported a fresh inventory CSV before this session — collection changes since the
last session are reflected in the loaded file.

[If picking up a specific recommendation:]
The prior session ended with a review recommendation to open a Phase 2 upgrade
targeting interaction. The candidates are documented in the handoff Context Notes.
Skip re-running the diagnostic and proceed directly to Phase 2 scoped to those
candidates.

## First Task

Before any work begins, confirm you have read the handoff and summarize:
1. Current deck state — phase, status, and what was accomplished last session
2. Next session goals as documented in the handoff
3. Bracket target and GC budget
4. Any active constraints beyond the standard changelog rules

Do not begin any work until I confirm we are aligned.
```
