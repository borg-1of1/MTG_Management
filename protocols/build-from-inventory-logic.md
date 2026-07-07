# Build-From-Inventory Logic Protocol

## Purpose

This protocol governs all deck-building sessions that start from scratch using cards the player already owns. It is a companion to `master-deckbuilding-logic.md` and operates under the same foundational principles, extended for the unique constraints of building rather than upgrading.

---

## Core Principles

1. **Inventory is the only source of truth.** No card may appear in the main deck list unless it is confirmed present in the player's inventory. This is not a wish list — it is an engineering problem.
2. **Bracket is a hard constraint, not a guideline.** It must be established before Phase 1 begins. Every card selected must be legal within the declared bracket.
3. **Build wide, then cut.** Phases 1–5 are additive. The deck will exceed 99 cards. Phase 6 exists to reduce it. Never artificially limit candidate selection during build phases.
4. **Gaps are documented, not ignored.** When no inventory card adequately fills a required role, the slot is noted as a gap and flagged in the `Future Upgrades` section of the output. A gap does not block build progress.
5. **Suboptimal is acceptable during the build.** The goal of the initial build is a functional, playable deck from owned cards. Optimization is the job of the upgrade workflow.
6. **Phases are sequential and non-recursive during a session.** Complete each phase before advancing. If a later phase reveals a problem, note it and continue — do not restart earlier phases mid-session.

---

## Phase 0 — Session Setup

**Goal:** Establish all constraints before any card selection begins.

The AI must confirm the following before proceeding to Phase 1. If any item is missing from the initial prompt, the AI asks for it before continuing.

### Required Inputs

| Input | Description |
|-------|-------------|
| **Commander** | The chosen legendary creature or planeswalker (if commander-led) |
| **Theme / Archetype** | The intended strategy (e.g., aristocrats, voltron, tokens, stax) |
| **Bracket** | Target bracket (1–5). Must be declared. No default assumed. |
| **Inventory** | The card pool available to draw from. Format flexible (list, spreadsheet export, etc.) |
| **Format** | Commander (default), Oathbreaker, or other. Assume Commander unless stated. |

### Entry Modes

The build may begin in one of three ways. The AI identifies the mode from the prompt and asks clarifying questions accordingly.

- **Commander-led:** Player names a commander and optionally a theme. AI confirms color identity, bracket, and asks for inventory.
- **Theme-led:** Player names a strategy or archetype without a commander. AI proposes 2–3 commander options that fit the theme and the inventory, player selects one, then proceeds.
- **Commander + Theme:** Player names both. AI confirms they are compatible, then proceeds.

### Bracket Gate

If the bracket is not specified in the opening prompt, the AI asks before any other question. Bracket determines:
- Which cards are legal (per `bracket-constraints.md`)
- The expected power ceiling for win conditions and interaction
- How aggressively the AI should evaluate tutors, fast mana, and combo pieces

---

## Phase Gate Rule

The AI must not advance to the next phase automatically. At the end of each phase, present the phase output and wait for explicit user confirmation before continuing:

> "Phase [X] complete. Ready to move to Phase [X+1] — [phase name] — when you are."

Do not proceed until the user confirms. This applies even if the next phase is clearly defined and ready to execute. Each phase boundary is a deliberate checkpoint — it allows the user to review candidates, remove or add cards before advancing, redirect the build, or end the session and resume later. Advancing without confirmation is not permitted regardless of how straightforward the next phase appears.

**This rule applies to all six phases, including the transition from Phase 0 to Phase 1.** Phase 0 is complete only when the user explicitly confirms the session setup summary is correct and gives the go-ahead to begin building.

---

## Phase 1 — Identity & Role Mapping

**Goal:** Define what the deck does and pull the non-negotiable cards.

1. Articulate the deck's primary game plan in one sentence.
2. Identify win conditions (1–3). Pull any inventory cards that directly enable them.
3. Identify the 3–5 cards that most define the archetype's identity — the cards the deck cannot function without. Pull from inventory.
4. Flag any identity-critical cards missing from inventory as **Priority Gaps**.
5. Document all Phase 1 candidates with their role noted.

---

## Phase 2 — Engine Building

**Goal:** Establish the support structure — ramp, draw, and recursion.

Work through each engine category in order:

### Ramp
- Target: enough mana acceleration to support the deck's curve and gameplan
- Prefer mana rocks and land ramp consistent with the color identity and bracket
- Pull all viable inventory candidates; note any gaps

### Card Draw & Advantage
- Target: consistent card flow to sustain the game plan through multiple turns
- Prefer repeatable draw over one-shots where inventory allows
- Pull all viable inventory candidates; note any gaps

### Recursion (if archetype-relevant)
- Pull graveyard recursion, flashback, or persistent threat enablers as applicable
- Skip or minimize if archetype does not benefit

---

## Phase 3 — Interaction

**Goal:** Build the deck's ability to answer threats and protect its own game plan.

### Removal
- Single-target removal (creature, artifact, enchantment, planeswalker as applicable)
- Board wipes appropriate to bracket level
- Pull from inventory; note gaps

### Protection
- Commander protection (hexproof, indestructible, counterspells, boots/greaves equivalents)
- Combo/win-con protection where applicable
- Pull from inventory; note gaps

### Hate Pieces (bracket-appropriate)
- Graveyard hate, artifact hate, enchantment hate as appropriate to expected meta
- Do not over-include; keep proportional to the archetype's needs

---

## Phase 4 — Synergy & Flex Slots

**Goal:** Fill remaining slots with cards that reinforce the archetype's identity and maximize internal synergy.

1. Review all Phase 1–3 candidates and identify synergy clusters.
2. Pull additional inventory cards that interact favorably with confirmed includes.
3. Fill flex slots with role-players that support the game plan even if not essential.
4. At this point the deck should feel like itself — Phase 4 is where theme becomes tangible.

---

## Phase 5 — Mana Base

**Goal:** Build a land base that supports the color requirements produced by Phases 1–4.

1. Count the color pips across all confirmed non-land candidates.
2. Determine the land count target (typically 35–38; adjust for average CMC and ramp density).
3. Pull dual lands, utility lands, and basics from inventory.
4. Prioritize: lands that enter untapped > lands with dual color identity > basics.
5. Note any significant gaps in dual coverage.
6. Do not include lands that do not support the color identity.

---

## Phase 6 — Review & Cuts

**Goal:** Reduce the candidate pool to exactly 99 cards (plus commander).

### Cut Priority Order
When making cuts, evaluate in this order:
1. **Weakest role overlap** — if two cards serve the same role, cut the less synergistic one
2. **Highest CMC for lowest impact** — expensive cards that don't win the game or are not synergy payoffs
3. **Off-theme cards** — cards pulled in earlier phases that don't reinforce Phase 4's synergy picture
4. **Conditional cards** — cards that require specific board states to function

### Documentation
- Record why each cut was made (one line is sufficient)
- Move cut cards that are thematically correct but lost to count reduction into the `Future Upgrades` section — they are upgrade candidates, not rejects

---

## Output Standards

All build sessions produce a `build-candidates.md` file (see template). The file is:
- **Not a final decklist** until the player manually promotes it
- **Version-stamped** with the session date and declared bracket
- **Structured** with clearly labeled sections for each phase's output and a dedicated `Future Upgrades` section

---

## Interaction with Other Protocols

| Protocol | Relationship |
|----------|-------------|
| `master-deckbuilding-logic.md` | Parent protocol. All shared principles apply. |
| `bracket-constraints.md` | Governs legality checks throughout all phases. Always active. |
| `input-contract.md` | Governs how inventory and session inputs are formatted and validated. |

---

## Session Continuity

If a session is interrupted before Phase 6, the current phase and all confirmed candidates are preserved in the `build-candidates.md` output. On resume, the AI:
1. Confirms the last completed phase
2. Reviews confirmed candidates to date
3. Continues from the next phase without revisiting prior decisions unless the player requests it
