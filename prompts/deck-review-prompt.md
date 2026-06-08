# Deck Review Prompt

**Task:** Conduct a full diagnostic review of the current deck state. This prompt evaluates the deck as it stands today — it does not execute upgrades. If the review surfaces candidates for improvement, those feed into an upgrade session using the standard phase path defined in `master-deckbuilding-logic.md`.

> **Relationship to the upgrade path:** Review and upgrade are distinct operations. Review produces an assessment and a set of recommendations. The user decides whether to open an upgrade session based on the review output. Upgrade sessions almost always end with a review pass via `comparison-logic.md` — review sessions may or may not lead to an upgrade session.

---

## Step 1 — Session Initialization

Complete the following before any diagnostic work begins. State each confirmation explicitly.

**Bracket target:** Read from `overview.md`. State it:
> "Bracket target confirmed: [X]."

**Changelog constraints:** Read `changelog.md`. All confirmed OUT and Rejected entries are binding for this session — do not suggest cards that were previously cut or rejected. If no changelog exists, note this and proceed without changelog constraints.

**GC budget:** Read current GC slot usage from the Bracket Notes section of `overview.md`. State it:
> "GC slots used: [X] of [maximum for bracket target]. [X] slot(s) remaining."

**Mechanics notes:** If `mechanics-notes.md` is present for this deck, load it. Use it as the authoritative source for interaction rulings. Do not reconstruct interaction rulings from memory — if a ruling is not in `mechanics-notes.md` and is not unambiguous from the card text, flag it as requiring confirmation rather than asserting it.

**Review context:** Determine which review context applies and state it explicitly before proceeding.

- **Post-Upgrade Review:** The deck has recently completed one or more upgrade phases and the review is validating that work. The diagnostic is backward-looking — did the upgrades achieve their intent and does the deck cohere as a whole?
- **Periodic Review:** The deck has been in service for some time. The diagnostic is forward-looking — is the deck still performing as intended, have new cards been released that change the calculus, and has anything drifted from the original design intent?

If the context is not clear from the loaded files, ask before proceeding.

---

## Step 2 — Current State Diagnostic

Evaluate the deck against the four mechanical priorities in order. For each category, provide a current state assessment and a gap rating.

**Gap rating scale:**
- **Stable** — this category is well-covered and needs no attention
- **Monitor** — minor gap or potential improvement, not urgent
- **Address** — meaningful gap that should be resolved in the next upgrade session
- **Critical** — significant gap that is likely impacting game performance

---

### Mana Consistency

Evaluate the land base and ramp package against the deck's CMC profile and color pip requirements.

- Is the average CMC appropriate for the deck's strategy and bracket target?
- Does the land base support reliable access to the required color pips on curve?
- Is the ramp package sufficient in quantity and CMC to support the game plan?
- Are there tapped lands, slow lands, or inefficient ramp pieces that could be upgraded?

State: average CMC, land count, ramp count, and any specific concerns identified.
Gap rating: [Stable / Monitor / Address / Critical]

---

### Interaction

Evaluate the deck's ability to answer threats, protect its pieces, and disrupt opponents.

- Does the deck have sufficient interaction for its bracket target? Bracket 3 decks should have meaningful interaction — the game should feel interactive and fair.
- Is the interaction instant-speed where possible?
- Does the deck have protection for its key pieces (board wipes, targeted removal)?
- Are there gaps in what the interaction package can answer (artifacts, enchantments, graveyards)?

State: interaction piece count, speed profile (instant vs sorcery), protection pieces, and any specific gaps identified.
Gap rating: [Stable / Monitor / Address / Critical]

---

### Card Draw and Card Advantage

Evaluate the deck's ability to sustain card advantage over the course of a game.

- Does the deck have sufficient draw engines to recover from interaction and maintain card parity?
- Is the draw conditional (requires creatures, counters, combat) or unconditional?
- Does the deck have ways to refuel after a board wipe?

State: draw piece count, draw engine types, and any specific concerns identified.
Gap rating: [Stable / Monitor / Address / Critical]

---

### Win Conditions

Evaluate the deck's win conditions against its strategy and bracket target.

- Are the win conditions consistent with the deck's primary game plan as described in `overview.md`?
- Does the deck have redundancy in its win conditions, or is it dependent on a single line?
- Are any win conditions slow, off-theme, or no longer pulling their weight given the current card pool?
- For periodic reviews: have new cards been released that execute the win condition more efficiently or thematically?

State: primary, secondary, and tertiary win conditions, their current reliability assessment, and any concerns identified.
Gap rating: [Stable / Monitor / Address / Critical]

---

## Step 3 — Bracket and Theme Assessment

### Bracket Compliance

Run the bracket evaluation checklist from `bracket-constraints.md` against the current decklist as a whole.

- Confirm current GC slot usage is within the budget for the bracket target
- Identify any cards in the current list that warrant interaction classification review (deterministic combo vs indeterminate synergy)
- Flag any multiplayer self-sustaining synergies that warrant Rule Zero disclosure at bracket-mixed tables
- Note any cards that push the deck's feel toward the next bracket even if technically compliant

State the overall bracket assessment: compliant, compliant with disclosures, or flag for review.

### Theme Coherence (Periodic Review Only)

If this is a periodic review, assess whether the deck's current card selection still reflects its stated theme and upgrade philosophy from `overview.md`.

- Are there cards that have drifted from the theme since the last upgrade cycle?
- Are there cards that were retained for flavor but are no longer pulling their mechanical weight?
- Have new cards been released that would serve both the theme and the strategy better than current inclusions?

---

## Step 4 — Suggestions

Based on the diagnostic, produce a prioritized list of suggested improvements. Apply all constraints before producing suggestions:

- Changelog constraints are binding — do not suggest previously cut or rejected cards
- All suggestions must pass the bracket evaluation checklist
- Inventory cards are preferred over purchase recommendations at equivalent impact
- Theme filter applies — flag when a suggestion conflicts with theme preservation and let the user decide

### Suggested Changes — Owned (Inventory)

Cards available in `_Global_Inventory` that address gaps identified in the diagnostic. Sorted by priority: Address gaps first, then Monitor gaps. Label each: **[Inventory — $0]**

For each suggestion state:
- Card in
- Card out
- Which diagnostic gap it addresses
- Bracket safe confirmation

### Suggested Changes — Purchase

Cards not in inventory that address gaps identified in the diagnostic. Only include if no inventory alternative exists that serves the same role. Label each: **[Purchase — ~$X]**

For each suggestion state:
- Card in
- Card out
- Which diagnostic gap it addresses
- Estimated cost
- Bracket safe confirmation

### Cards to Monitor

Cards currently in the deck that are not suggested for immediate replacement but warrant watching — either because better alternatives may emerge, because they are underperforming but no clear replacement exists yet, or because new card releases could displace them.

---

## Step 5 — Output

### Current State Summary

A concise summary of where the deck stands today. Include the gap rating for each of the four mechanical priorities and the overall bracket assessment. This section should be readable as a standalone status report.

### Suggested Changes

The full suggestion list from Step 4, formatted and ready for review. If suggestions are accepted, they feed into an upgrade session — do not execute them here.

### Bracket Status

- Bracket target: [X]
- GC slots used: [X] of [maximum]
- Bracket assessment: [Compliant / Compliant with disclosures / Flag for review]
- Rule Zero disclosures: [Any multiplayer self-sustaining synergies identified]

### Flags

Any escalation flags, bracket edge cases, or concerns identified during the review that require explicit acknowledgment before an upgrade session begins.

### Recommendation

State one of the following based on the diagnostic:

- **No upgrade needed** — all categories Stable or Monitor, no Critical or Address gaps. Deck is performing as intended. Schedule next periodic review after significant new card releases or after 3–6 months of play.
- **Upgrade recommended** — one or more Address gaps identified. Begin an upgrade session targeting the highest-priority gap. Load `master-deckbuilding-logic.md` and enter at the appropriate phase.
- **Upgrade required** — one or more Critical gaps identified. The deck has a meaningful performance issue that should be resolved before the next play session if possible.

If an upgrade is recommended or required, state the suggested entry point in the upgrade path:
> "Recommend opening an upgrade session at Phase [X] — [phase name] targeting [specific gap]."
