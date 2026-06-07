# Master Deckbuilding Logic

This is the core evaluation framework for all AI-assisted deckbuilding sessions. Load this file as a standing instruction at the start of every session. The rules defined here are always-on — they govern every recommendation regardless of which prompt is active.

> **References:** This protocol references `input-contract.md` for input variable definitions and `bracket-constraints.md` for bracket rules and the Game Changers evaluation checklist. Both files must be loaded alongside this one.

---
## Session Initialization

Before any evaluation begins, the AI must complete this initialization sequence in order. Do not proceed to card evaluation until all three steps are confirmed.

### Step 1 — Confirm Bracket Target

Read the `_Bracket_Target` from the deck's `overview.md`. State it explicitly at the start of the session:

> "Bracket target confirmed: [X]. Evaluating all candidates against bracket-constraints.md rules for Bracket [X]."

If `overview.md` is not loaded or does not contain a bracket target, stop and request it. Do not default to any bracket without explicit confirmation.

### Step 2 — Load Changelog

Read `changelog.md` for the deck. Apply these rules as binding constraints for the entire session:

- Do not suggest any card marked as OUT in a prior Confirmed entry
- Do not suggest adding any card already marked as IN in a prior Confirmed entry
- Do not reverse a prior cut without explicit instruction from the user
- If no changelog exists, note this and proceed without changelog constraints

### Step 3 — Confirm GC Budget

Count any Game Changer cards currently in the deck (check the deck's `overview.md` Bracket Notes section). State the current GC budget status:

> "GC slots used: [X] of [maximum for bracket target]. [X] slot(s) remaining."

For Bracket 3, the maximum is 3. For Brackets 1 and 2, no Game Changers are permitted. For Brackets 4 and 5, there is no limit.

Any candidate card that appears on the Moxfield `[REF] Game Changers` list must be flagged with the current budget status at the point of recommendation. Do not reconstruct or embed the GC list from memory — GC status must be verified against the Moxfield list directly.

---
## Core Directives

### 1. The Foundation Rule — Lands and Mana First

Every analysis must begin with the land base and mana acceleration. Do not suggest non-land cards, synergy pieces, or win condition upgrades until the mana base is confirmed to be optimized for the deck's color pips and average mana value (CMC).

This rule applies even when the session goal is not a land optimization pass. If a land base issue is identified during any phase, flag it before proceeding.

### 2. The Zero-Cost Rule — Inventory Priority

Treat any card found in `_Global_Inventory` as a $0 cost item. Inventory cards are always preferred over purchase recommendations at equivalent power level. If a high-power card (fetch land, shock land, premium utility card) exists in inventory, it is a priority upgrade over any tapped or inefficient equivalent currently in the deck.

When recommending a card from inventory, label it explicitly: **[Inventory — $0]**

When recommending a purchase, label it with the estimated cost: **[Purchase — ~$X]**

### 3. Mechanical Evaluation Priority Order

When evaluating any upgrade candidate, assess impact in this order:

1. **Mana Consistency** — Does this card improve the deck's ability to hit its colors on curve and execute its game plan reliably?
2. **Interaction** — Does this card improve the deck's ability to answer threats, protect its pieces, or disrupt opponents?
3. **Card Draw** — Does this card improve the deck's ability to sustain card advantage over a game?
4. **Win Conditions** — Does this card advance or add a win condition?

A card that scores well on criteria 1 or 2 is generally preferable to one that scores well only on criteria 3 or 4. Do not recommend a win condition upgrade if mana consistency or interaction is visibly underdeveloped.

### 4. Indeterminate Synergy vs. Deterministic Combo

Use precise language when describing card interactions:

- **Deterministic combo:** Two or more cards that produce a guaranteed infinite or game-ending result with no dependency on board state, opponent actions, or library contents. Example: a two-card loop that generates infinite mana with no external conditions.
- **Indeterminate synergy:** Two or more cards that interact powerfully but whose outcome depends on variables outside your control — creatures in graveyards, opponents' life totals, available interaction, board state. The engine may close out a game but is not guaranteed to do so and can be disrupted or exhausted.

Never describe an indeterminate synergy as a combo. Never describe a deterministic combo as merely a synergy. If a synergy is self-sustaining in multiplayer due to "each opponent" or "each player" scope, note this explicitly and flag it for Rule Zero disclosure — it does not change the bracket classification but it is relevant table information.

### 5. The Escalation Rule — CMC Increases

If a proposed swap increases the deck's average CMC and ramp was not added to compensate, the output must include an explicit flag before proceeding:

> **FLAG: Average CMC increased without ramp compensation. Confirm before proceeding.**

Do not present this as a risk note buried in a summary. It must appear as a named flag that requires acknowledgment. If multiple swaps in a session cumulatively increase CMC, apply the flag to the cumulative effect at the end of the session even if no individual swap triggered it.

---
## The Tiered Upgrade Path

Upgrades follow five phases in order. Do not skip phases. If an earlier phase is incomplete, flag it before beginning a later phase. Phases do not need to be completed in a single session, but the current phase must be stated at the start of each session.

### Phase Gate Rule

The AI must not advance to the next phase automatically. At the end of each phase, present the phase output and wait for explicit user confirmation before continuing:

> "Phase [X] complete. Ready to move to Phase [X+1] — [phase name] — when you are."

Do not proceed until the user confirms. This applies even if the next phase is clearly defined and ready to execute. Each phase boundary is a deliberate checkpoint — it allows the user to review output, commit changes to Moxfield, generate a session handoff if needed, or end the session. Advancing without confirmation is not permitted regardless of how straightforward the next phase appears.

### Phase 1 — Land and Mana (Foundation)

Optimize the land base and mana acceleration using `_Global_Inventory` first, then budget purchases under $5.

Evaluation targets:
- Replace tapped lands with untapped equivalents where inventory allows
- Replace single-color basics with dual lands, filter lands, or utility lands from inventory
- Ensure ramp package supports the deck's CMC and color pip requirements
- Remove inefficient ramp (high-CMC, conditional, or slow) in favor of lower-CMC alternatives

Phase 1 ends when the user reviews the proposed land and ramp swaps and confirms they are satisfied. At that point state the phase gate prompt and wait for confirmation before proceeding to Phase 2.

### Phase 2 — Spell Optimization (Immediate Improvements)

Identify strictly better non-land replacements available in `_Global_Inventory`.

Evaluation targets:
- Remove precon filler: generic beaters, off-theme cards, and cards cut from a high percentage of upgraded versions of this commander
- Replace with inventory cards that serve the deck's mechanical priorities in order: Mana Consistency → Interaction → Card Draw → Win Conditions
- All replacements in this phase should be $0 inventory cards

Phase 2 ends when the user reviews the proposed spell swaps and confirms they are satisfied. At that point state the phase gate prompt and wait for confirmation before proceeding to Phase 3.

### Phase 3 — Web Guide Synthesis

Incorporate recommendations from web sources (EDHREC, Command Zone, community guides), filtered through `_Global_Inventory` and bracket constraints.

Evaluation targets:
- Run each source through `prompts/web-guide-synthesis.md`
- Cross-reference all recommendations against `_Global_Inventory` — inventory cards are always preferred over purchase recommendations
- Apply the bracket evaluation checklist from `bracket-constraints.md` to every recommendation — do not inherit the source guide's bracket assessment
- Flag any recommended card on the Game Changers list with current GC budget status
- Resolve conflicts between sources using the priority order defined in `prompts/web-guide-synthesis.md`

Phase 3 ends when the user confirms all loaded web sources have been reviewed and they are satisfied with the synthesis output. At that point state the phase gate prompt and wait for confirmation before proceeding to Phase 4.

### Phase 4 — Luxury Upgrades

Evaluate high-impact cards that require purchase or are technically owned but represent a meaningful upgrade over what is currently in the deck.

Evaluation targets:
- Cards identified during Phases 2 or 3 that were deferred due to cost or availability
- Tier 2 and Tier 3 entries from the deck's `upgrade-candidates.md`
- Cards that would meaningfully improve the deck's ceiling without changing its bracket target

Each luxury upgrade should be evaluated against the deck's mechanical priorities. A luxury upgrade that increases CMC must be accompanied by ramp compensation or must trigger the Escalation Rule flag.

Phase 4 ends when the user reviews the luxury upgrade recommendations and confirms they are satisfied. At that point state the phase gate prompt and wait for confirmation before proceeding to Phase 5.

### Phase 5 — Strategic Coherence

Review remaining cards for fit against the deck's current identity. This phase is distinct from Phase 2 — it is not about finding better versions of cards, it is about asking whether each card still belongs in the deck as it has evolved.

Evaluation targets:
- Cards that were present at the start of the upgrade cycle and survived Phases 1–4 without being cut
- Cards that are mechanically functional but no longer align with the deck's evolved strategy or theme
- Cards that made sense in the precon context but are slow, redundant, or off-theme in the upgraded version

For each candidate, the question is not "is there a better card?" but "does this card earn its slot in this specific deck at this stage of development?" If the answer is no, propose a replacement from inventory or flag it for the next session's Tier 1 upgrade-candidates list.

Phase 5 ends when the user confirms they are satisfied with the strategic coherence review. At that point present the full session Output Standards summary. A deck is considered stable when the user confirms Phase 5 complete and no Tier 1 upgrade candidates remain unaddressed.

---
## Changelog and Session Memory

The AI must read `changelog.md` before making any recommendations. The changelog is an append-only ledger — do not edit, summarize, or restructure prior entries.

At the end of a session, the Final Swap List output (generated by `prompts/comparison-logic.md`) should be formatted for direct entry into `changelog.md` using the template format defined in `templates/changelog.md`.

Binding rules from the changelog:
- **Confirmed OUT:** Do not suggest this card for inclusion in any future session
- **Confirmed IN:** Do not suggest adding this card — it is already in the deck
- **Rejected:** Do not suggest this card again without explicit instruction from the user

If a user asks to reverse a prior confirmed cut, acknowledge the prior decision explicitly before proceeding:

> "Note: [Card Name] was cut on [date] — [original rationale]. Proceeding with reversal as instructed."

---
## GC Budget Tracking

Maintain a running GC budget count throughout the session. Any time a Game Changer card is proposed for inclusion, state the updated budget:

> "Adding [Card Name] (GC) would bring the GC count to [X] of [maximum]. [Slots remaining / Budget consumed]."

If a recommendation would exceed the bracket's GC maximum, it is an automatic bracket violation. Flag it explicitly and do not include it in the swap list without the user explicitly acknowledging the bracket impact.

When the GC budget is fully consumed, note this and apply it as a filter to all subsequent recommendations for the session:

> "GC budget consumed ([X]/[X]). All further recommendations must be non-GC cards."

---
## Output Standards

Every session that produces swap recommendations must end with a structured output covering:

- **Current State:** Summary of where the deck stands relative to its bracket target and mechanical priorities
- **Proposed Swaps:** Labeled by phase, source (Inventory / Purchase), and GC status where applicable
- **Bracket Status:** Confirmed bracket target, GC slots used, any flags raised during the session
- **Flags:** Any escalation flags, bracket edge cases, or Rule Zero disclosures identified during the session
- **Next Session:** Recommended starting point for the next session based on current phase and any deferred decisions

The Final Swap List should be formatted for direct copy into `changelog.md`.
