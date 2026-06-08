# Commander Bracket Constraints

This document is the authoritative reference for bracket rules within this workflow. All AI sessions and upgrade evaluations must check candidate cards against the target bracket defined in the deck's `overview.md`.

> **Authoritative Source:** [WotC Commander Brackets (Beta)](https://magic.wizards.com/en/news/announcements/introducing-commander-brackets-beta) — last confirmed against the [October 21, 2025 Beta Update](https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-october-21-2025). The Game Changers list is maintained as a `[REF] Game Changers` list in Moxfield (LIBRARY/Tools), manually synced to the official WotC list when updates are published. That list is the operational source of truth for GC status and ownership during any session.

---

## The Four Constraint Axes

Every bracket is defined by where it sits on these four axes. These are the lens through which every upgrade candidate is evaluated.

| Axis | What It Measures |
|---|---|
| **Game Changers** | How many cards from the official Game Changers list are present |
| **Two-Card Infinite Combos** | Whether intentional infinite combos exist, and how early they can fire |
| **Extra Turns** | Presence and chainability of extra turn effects |
| **Mass Land Denial (MLD)** | Cards that destroy or deny all/most lands |

---

## Bracket Definitions

### Bracket 1 — Exhibition (Ultra Casual)

**Intent:** Theme and flavor over power. Nobody is in a hurry. Games are social experiences first.

| Axis | Rule |
|---|---|
| Game Changers | **Zero** — none permitted |
| Two-Card Infinite Combos | **None** — no intentional combos |
| Extra Turns | **None** |
| Mass Land Denial | **None** |
| Tutors | Sparse — not a focus of the deck |

**Expected game length:** 9+ turns before first elimination.

**Build notes:** Every card choice should serve the theme or a creative/flavor goal. Efficiency is actively deprioritized. A good test: would a new player feel overwhelmed or shut out by this deck?

---

### Bracket 2 — Core (Focused Casual)

**Intent:** Consistent, thematic, interactive play. Winning matters but is not the primary driver. Decks are built around a clear idea and execute it straightforwardly.

> **October 2025 Update:** Bracket 2 is no longer tied to preconstructed decks. It is defined by play experience and intent, not card pool origin. The precon framing was removed because precon power levels vary too widely and player expectations around them diverge significantly.

| Axis | Rule |
|---|---|
| Game Changers | **Zero** — none permitted |
| Two-Card Infinite Combos | **None** — no intentional combos |
| Extra Turns | Low quantity only; must not chain or loop |
| Mass Land Denial | **None** |
| Tutors | Sparse — present but not a core strategy |

**Expected game length:** 8+ turns before first elimination.

**Build notes:** Win conditions should be incremental and disruptible. Gameplay should feel low-pressure with room for social interaction. Optimization is acceptable as long as it serves the theme rather than replacing it.

---

### Bracket 3 — Upgraded (Powered Casual) ⭐ Primary Play Space

**Intent:** Noticeably stronger than a casual table, but still socially focused. Synergies are deliberate and optimized. Games are faster and more decisive, but not oppressive.

| Axis | Rule |
|---|---|
| Game Changers | **Up to 3** from the official list |
| Two-Card Infinite Combos | **No early-game combos** — late-game combos (requiring significant setup) are acceptable |
| Extra Turns | Low quantity only; must not chain or loop |
| Mass Land Denial | **None** |
| Tutors | No explicit restriction, but intent matters — tutoring for a combo piece on turn 3 pushes toward Bracket 4 |

**Expected game length:** Games are faster than Bracket 2; first elimination may occur around turns 6–8.

**Build notes for this workflow:**

- The 3 Game Changer slots are a **budget**, not a target. Use them only where they provide clear value for the deck's strategy.
- "No early-game two-card infinite combo" means no combo that can fire before the mid-game without significant resource investment. If a combo can win before turn 5 with minimal setup, it belongs in Bracket 4.
- Mana efficiency (Sol Ring, Arcane Signet, etc.) is fine — fast mana that enables broken turn 1–2 plays (Mana Vault into a combo piece) is the line.

---

### Bracket 4 — Optimized (High Power)

**Intent:** Maximizing the deck's power and consistency within the Commander ban list. No social constraints. Winning efficiently is the primary goal.

| Axis | Rule |
|---|---|
| Game Changers | **Unrestricted** |
| Two-Card Infinite Combos | **Unrestricted** |
| Extra Turns | **Unrestricted** |
| Mass Land Denial | **Unrestricted** |
| Tutors | **Unrestricted** |

**Expected game length:** Games can end by turns 5–7 or earlier.

**Build notes:** All decisions are evaluated purely on power and consistency. The meta matters — builds should anticipate interaction from other high-power decks. No card is off-limits by bracket rule (only the Commander ban list applies).

---

### Bracket 5 — cEDH (Competitive)

**Intent:** Fully competitive, metagame-aware play. Identical card restrictions to Bracket 4, but distinguished by **mindset and metagame focus**. Every decision is made with the competitive meta in mind.

| Axis | Rule |
|---|---|
| Game Changers | **Unrestricted** |
| Two-Card Infinite Combos | **Unrestricted** |
| Extra Turns | **Unrestricted** |
| Mass Land Denial | **Unrestricted** |
| Tutors | **Unrestricted** |

**Expected game length:** Wins as early as turns 2–4 are possible and expected.

**Build notes:** The distinction between Bracket 4 and Bracket 5 is intent and metagame adherence, not card restrictions. A Bracket 5 deck is built specifically to compete in the cEDH metagame, with card choices validated against what the current competitive field is running. Bracket 4 is high power without that metagame lens.

---

## Game Changers List

The full Game Changers list is maintained as `[REF] Game Changers` in Moxfield under LIBRARY/Tools. That list is manually synced to the official WotC list when updates are published and serves as the single operational source of truth. Do not maintain a copy here — any card evaluation requiring GC status should reference the Moxfield list directly.

> **When was the Moxfield list last synced?** Check the comment/changelog on that Moxfield deck entry.

---

## Interaction Classification

Before applying the bracket evaluation checklist, interactions must be classified correctly. Using imprecise language leads to incorrect bracket assessments. Apply these definitions consistently.

### Deterministic Combo

Two or more cards that produce a guaranteed infinite or game-ending result with no dependency on board state, opponent actions, or library contents. The outcome is certain once the pieces are assembled. Example: a two-card loop that generates infinite mana regardless of what opponents control or what remains in any library.

Deterministic combos are the primary concern of the two-card infinite combo axis. Their bracket classification depends on how early they can fire and how much setup they require.

### Indeterminate Synergy

Two or more cards that interact powerfully but whose outcome depends on variables outside your control — creatures in graveyards, opponents' life totals, available interaction, library contents, board state. The engine may close out a game but is not guaranteed to do so and can be disrupted or exhausted.

An indeterminate synergy is not a combo. It does not trigger the two-card infinite combo axis. Bracket classification is based on the cards' individual GC status and the deck's overall power profile, not the synergy itself.

### Multiplayer Self-Sustaining Synergies

An indeterminate synergy can become practically self-sustaining in multiplayer due to the scope of "each opponent" or "each player" triggers. In a four-player game, a single trigger event against one opponent can generate cascading triggers against all other opponents, feeding the engine across multiple players simultaneously. This does not make the synergy deterministic — it still terminates when libraries are exhausted or opponents are eliminated, and it depends on board state — but the multiplayer scaling meaningfully increases the engine's practical power compared to a two-player context.

**Bracket classification is unchanged** — a multiplayer self-sustaining indeterminate synergy is still evaluated as an indeterminate synergy, not as a combo. However it **warrants Rule Zero disclosure** at any bracket-mixed table. Players who agreed to a Bracket 3 game may not have anticipated an engine that can close out the table in one or two trigger cycles once it reaches critical mass.

> **Example from this workflow:** Syr Konrad, the Grim + Mindcrank. Confirmed Bracket 3 legal — neither card is on the Game Changers list, and the interaction is indeterminate. However in a four-player game, milled creatures generate Konrad triggers against all opponents, each triggering Mindcrank on a different player. The engine is self-sustaining in multiplayer at critical mass. Disclose under Rule Zero at bracket-mixed tables. See `decks/mutant-menace/mutant-menace-mechanics-notes.md` for the full interaction ruling. This example illustrates the classification and disclosure rules. Do not use it as a template for classifying other interactions — apply the definitions above to each interaction independently.

---

## Bracket Evaluation Checklist

When evaluating an upgrade candidate, work through this checklist in order:

1. **What is the deck's bracket target?** (Check `overview.md`)
2. **Is the card on the Game Changers list?**
   - If yes: does adding it keep the deck within its GC budget for the bracket target?
3. **Does the card enable or accelerate an interaction between cards?**
   - First classify the interaction: is it a **deterministic combo** or an **indeterminate synergy**? (See Interaction Classification above)
   - If deterministic: does the combo fire early-game? → Flag for bracket violation if yes
   - If indeterminate: is it self-sustaining in multiplayer due to "each opponent" or "each player" scope? → Flag for Rule Zero disclosure if yes; bracket classification is unchanged
4. **Does the card produce or chain extra turns?**
   - If yes: does it loop or chain? → Flag for bracket violation
5. **Does the card produce mass land denial?**
   - If yes: automatic exclusion for Brackets 1–3
6. **Does the card's intent match the bracket target?**
   - A card can technically fit the rules while pushing the deck's feel into the next bracket. Use judgment.

---

## Personal Play Philosophy

- **Primary play spaces:** Bracket 2 and Bracket 3
- **Bracket 2** is the target for decks meant to play at a kitchen table or with less experienced players. Fun and theme take priority over efficiency.
- **Bracket 3** is the target for optimized personal builds. Synergy and power are deliberate, but the game should still feel interactive and fair.
- **Brackets 4 and 5** are build targets for high-power or competitive contexts. These are built to win efficiently and are evaluated purely on power and consistency.
- **Bracket 1** builds are creative or theme-driven projects. They are not evaluated for efficiency.
- **Rule Zero always applies.** This document encodes the bracket rules as a default. Any deviation agreed upon at the table takes precedence for that session.
