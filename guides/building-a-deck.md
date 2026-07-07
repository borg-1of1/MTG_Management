# Guide: Building a Deck From Inventory

## Overview

This guide walks through how to run a complete deck-building session using the build-from-inventory workflow. This workflow is distinct from the upgrade workflow — you are starting from zero and constructing a full 99-card Commander deck using cards you already own.

The process is phased and disciplined. Each phase has a clear purpose and a defined output. You will review candidates at each phase boundary before advancing.

---

## When to Use This Workflow

Use this workflow when:
- You want to build a new deck from scratch
- You want to see what a given commander or archetype can look like with your existing collection
- You are exploring whether you have enough cards to build a particular strategy before committing to purchases

Use the **upgrade workflow** instead when:
- A decklist already exists and you want to improve it
- You are evaluating specific card swaps

---

## Files to Load

Before starting a session, provide the AI with the following files. You do not need to paste them manually — reference them by name and confirm they are loaded.

| File | Required? | Purpose |
|------|-----------|---------|
| `protocols/build-from-inventory-logic.md` | **Required** | Phase structure, rules, and build principles |
| `protocols/bracket-constraints.md` | **Required** | Card legality by bracket |
| `protocols/master-deckbuilding-logic.md` | **Required** | Foundational deckbuilding principles |
| `protocols/input-contract.md` | **Required** | Input validation and formatting rules |
| `prompts/build-from-inventory-prompt.md` | Recommended | Session prompt template |
| `templates/build-candidates.md` | Recommended | Output template reference |

---

## Step-by-Step

### Step 1 — Fill Out the Session Prompt

Open `prompts/build-from-inventory-prompt.md` and copy the template. Fill in:

- **Entry Mode** — Are you starting with a commander, a theme, or both?
- **Commander** — Name your commander, or leave TBD if theme-led
- **Theme / Archetype** — Describe what the deck does
- **Bracket** — This is required before the session can begin
- **Inventory** — Paste your card list or export. More detail = better results.
- **Additional Context** — Anything the AI should know upfront

**You do not need to answer everything before submitting.** The AI will ask clarifying questions for anything missing. Bracket and Inventory are the only hard requirements before Phase 1 starts.

### Step 2 — Phase 0: Session Setup

The AI will confirm your inputs, identify the entry mode, and ask any remaining clarifying questions. If you chose Theme-Led, it will propose 2–3 commander options that fit your theme and inventory — you select one before proceeding.

Review the Phase 0 summary the AI produces before saying "proceed."

### Step 3 — Phases 1–5: Building the Deck

The AI will work through each phase in sequence, presenting candidates at each step. At each phase boundary you can:

- **Approve and advance** — "Looks good, proceed to Phase 3"
- **Remove a candidate** — "Cut [card], I don't want that in this deck"
- **Add a candidate** — "Also consider [card] for Phase 2 ramp"
- **Ask for alternatives** — "What else from my inventory fits this role?"

The deck will grow over 99 cards during these phases. That is expected and correct.

### Step 4 — Phase 6: Review & Cuts

This is where the deck becomes 99 cards. The AI will:
1. Count all candidates across all phases
2. Present a cut list with reasoning
3. Move cut cards to the appropriate section of `Future Upgrades`

You make the final call on every cut. If you disagree with a suggested cut, say so and the AI will propose an alternative.

### Step 5 — Output the Build-Candidates File

After Phase 6, the AI will produce a completed `build-candidates.md` file using the template. This file contains:
- The full 99-card list organized by type
- The cut log with reasoning
- Future upgrade priorities (gaps not filled + cards cut due to count)
- Session notes

**This is not a final decklist.** It is a working draft. When you are satisfied with it, rename it to `decklist.md` following your repository's naming convention.

---

## Tips

**On inventory format:** The AI can work with plain lists, Moxfield exports, Archidekt exports, or even rough descriptions ("I have most of the Innistrad zombie cards"). A specific list produces better results, but don't let format be a barrier to starting.

**On bracket:** When in doubt, declare the bracket you *want* to play at, not the one you think your cards can reach. The protocol will flag gaps honestly.

**On gaps:** If your inventory can't fill a role, the gap is documented in `Future Upgrades`. This is useful — it gives you a prioritized shopping list for when you want to iterate on the deck later. Think of it as the build workflow feeding the upgrade workflow.

**On session length:** Complex decks (high synergy density, heavy interaction requirements) will take longer per phase. You can end a session at any phase boundary and resume later — the `build-candidates.md` output preserves everything completed to that point.

**On rebuilding:** If after Phase 6 the deck doesn't feel right, you can restart from Phase 4 (synergy and flex) without redoing the engine and interaction work. The early phases establish a foundation that rarely needs to change within a session.

---

## Workflow Relationship Diagram

```
Build-From-Inventory Workflow
│
├── Phase 0: Setup (commander, theme, bracket, inventory)
├── Phase 1: Identity & Core Cards
├── Phase 2: Engine (ramp, draw, recursion)
├── Phase 3: Interaction (removal, protection, hate)
├── Phase 4: Synergy & Flex
├── Phase 5: Mana Base
└── Phase 6: Review & Cuts
            │
            ├── build-candidates.md (output)
            │       │
            │       ├── [player promotes] → decklist.md
            │       └── [player generates] → deck-readme.md
            │
            └── Future Upgrades section
                        │
                        └── [feeds into] → Upgrade Workflow
```

---

## Promoting to deck-readme.md

Once you are satisfied with `build-candidates.md`, use it as the source to generate `deck-readme.md` for the deck vault. The two files serve different purposes — build-candidates is the full engineering record, deck-readme is the living document you maintain going forward.

### Promotion Checklist

When creating `deck-readme.md` from a completed build session, carry over or populate the following:

| deck-readme.md Field | Source |
|----------------------|--------|
| Commander | Phase 0 session setup |
| Color Identity | Phase 0 session setup |
| Bracket | Phase 0 — confirmed bracket |
| Origin | Set to `Custom Build` for all inventory builds |
| Status | Set to `S2 Built` if deck is physically assembled, `S1 Partial` if gaps remain |
| Theme & Strategy | Phase 1 deck identity / game plan (condense to 2–3 sentences) |
| Win Conditions | Phase 1 win conditions |
| Bracket Notes | Phase 0 bracket + any Game Changers flagged during the build |
| Upgrade Philosophy | Summarize from the Future Upgrades section — what does the deck need most? |
| Open Questions | Carry over any unresolved Phase 6 decisions or gap cards still being evaluated |
| Session Log | First entry: build session date + "Initial build from inventory" |

### Fields to Fill Fresh

These fields have no source in build-candidates and must be filled manually:

- **Moxfield URL** — add once the list is entered in Moxfield
- **Moxfield Folder** — assign to appropriate vault folder
- **Physical State** — reflect actual card availability after assembly

---

## Frequently Asked Questions

**Q: Can I use this workflow for non-Commander formats?**  
Yes. The protocol defaults to Commander but works for Oathbreaker and other singleton formats. Specify the format in your session prompt.

**Q: What if I don't know what bracket my cards support?**  
Declare a target bracket and proceed. The protocol will flag any inventory cards that exceed the bracket ceiling. You can decide whether to exclude them or revisit the bracket declaration.

**Q: Can I mix this with the upgrade workflow in the same session?**  
Not in the same session pass. Complete the build session and produce a `build-candidates.md` first. Then run an upgrade session against that output if you want to optimize it.

**Q: What if I want to allow a small number of purchases?**  
The build protocol is inventory-strict. But after the build is complete, your `Future Upgrades` section will contain a prioritized list of targeted purchases. Run an upgrade session against the completed build-candidates file with a defined budget to get specific buy recommendations.
