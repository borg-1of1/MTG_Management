# Web Guide Synthesis

**Task:** Audit available sources and extract upgrade recommendations for the current deck, cross-referenced against `_Global_Inventory` and filtered through `bracket-constraints.md`.

> **This prompt drives Phase 3 of the upgrade path defined in `master-deckbuilding-logic.md`.** The phase gate rule applies — do not advance to Phase 4 without explicit user confirmation.

---

## Step 1 — Scenario Detection

Before extracting any recommendations, determine which input scenario applies. State the scenario explicitly before proceeding.

**Scenario A — Dedicated sources available**
One or more guides, articles, or videos exist that specifically cover this commander or deck archetype. These may be from sources such as EDHREC commander pages with written guides, The Command Zone, Card Kingdom, community content creators, or similar. Load and proceed to the Per-Source Extraction section.

**Scenario B — No dedicated sources available**
No commander-specific guides exist or none have been provided. This is common for custom builds, obscure commanders, or newly released commanders without an established community guide footprint. Proceed to the EDHREC Consensus section.

If both dedicated sources and EDHREC data are available, run Scenario A first, then use EDHREC data to fill gaps or surface cards the guides missed. Note when EDHREC data is supplementing rather than replacing guide analysis.

---

## Scenario A — Per-Source Extraction

For each dedicated source, provide the following block:

**Source Title:** (e.g., "Card Kingdom Mutant Menace Upgrade Guide")
**Primary Strategy Identified:** What does this author want the deck to do? How does their recommended strategy align with or diverge from the deck's current strategy as defined in `overview.md`?
**Must-Haves:** The top 5 cards this guide considers essential. Cross-reference against `_Global_Inventory` — highlight any owned cards in **BOLD CAPS**.
**Unique Tech:** Any card this guide recommends that other sources missed. Flag if it appears in inventory.
**Cuts:** The 3 cards from `_Current_Decklist` this guide most strongly recommends removing.

Repeat this block for every source provided before moving to the Cross-Source Synthesis step.

---

## Scenario B — EDHREC Consensus

When no dedicated sources are available, use EDHREC data as the primary input. EDHREC provides two distinct signals that must be treated separately:

**Inclusion Rate:** The percentage of decks running this commander that include a given card. High inclusion reflects broad community consensus. It does not indicate fit for this specific deck, bracket target, or theme.

**Synergy Score:** A measure of how much more often a card appears in decks with this commander compared to all Commander decks. High synergy indicates the card works specifically well with this commander's mechanics, independent of whether it is a generic staple.

These are different signals. A card with high synergy but low inclusion may be an underplayed card worth flagging. A card with high inclusion but low synergy is likely a generic staple — it may or may not earn its slot depending on theme and bracket fit.

### EDHREC Candidate Evaluation Stack

Apply this priority order when evaluating every EDHREC candidate. Work through the stack in order — a card that fails at any step is filtered out or flagged before the next step is applied.

1. **Bracket constraint check** — does the card violate the bracket target? If yes, auto-exclude. State the reason explicitly. Do not pass bracket-violating cards further down the stack regardless of synergy score or inclusion rate.
2. **Inventory cross-reference** — does the card appear in `_Global_Inventory`? An owned card advances with a **[Inventory — $0]** label. A card not in inventory advances with a **[Purchase — ~$X]** label.
3. **Theme filter** — apply the upgrade philosophy from `overview.md`. A card that fits the deck's theme and pulls its weight mechanically is preferred over a purely efficient replacement that breaks theme. Cards that are high-inclusion but off-theme must clear a higher bar to earn a recommendation. State the theme assessment explicitly.
4. **Synergy over inclusion** — where two candidates are otherwise equal after Steps 1–3, prefer the higher synergy score over the higher inclusion rate. The synergy score reflects fit with this commander; the inclusion rate reflects what the average deck runs, which may not be this deck.

### EDHREC Output Format

Present EDHREC recommendations in two groups:

**Recommended — Owned:** Cards that passed the full evaluation stack and are in inventory. Sorted by synergy score, highest first.

**Recommended — Purchase:** Cards that passed the full evaluation stack but require purchase. Sorted by synergy score, highest first. Include estimated cost.

**Filtered Out:** Cards that were excluded and why. Group by exclusion reason: bracket violation, GC budget exceeded, off-theme without sufficient mechanical justification.

---

## Cross-Source Synthesis (Scenario A)

After all per-source blocks are complete, produce a synthesis across all sources.

### Conflict Resolution

When sources disagree on a card — one recommends including it, another recommends cutting it, or sources disagree on priority — apply this resolution order:

1. **Inventory bias:** If the card is in `_Global_Inventory`, apply an include bias. An owned card that is contested between sources should be retained unless a bracket violation or strong mechanical argument rules it out.
2. **Bracket constraint:** If the card violates the bracket target as defined in `bracket-constraints.md`, auto-exclude regardless of source consensus. State the bracket reason explicitly.
3. **Mechanical priority:** If no inventory or bracket factor is decisive, default to the recommendation that improves the higher-priority mechanical category. Mana Consistency outweighs Interaction, which outweighs Card Draw, which outweighs Win Conditions. A card that improves Mana Consistency beats a conflicted Win Condition recommendation.

For each conflict resolved, state which rule resolved it and why.

### Bracket Classification Check

Source guides frequently misclassify bracket level or make no bracket assessment at all. Do not inherit a guide's bracket assessment. Apply `bracket-constraints.md` independently to every recommended card:

- Run each recommendation through the Bracket Evaluation Checklist in `bracket-constraints.md`
- Flag any card the guide recommends that would violate the deck's bracket target
- Flag any card the guide recommends that is on the Game Changers list, with current GC budget status
- If a guide recommends a card as bracket-safe and your evaluation disagrees, state the conflict explicitly and apply your assessment

### Synthesis Output Format

**Consensus Recommendations — Owned:** Cards recommended by two or more sources that are in inventory. **BOLD CAPS.**
**Consensus Recommendations — Purchase:** Cards recommended by two or more sources that require purchase. Include estimated cost.
**Single-Source Recommendations — Owned:** Cards recommended by only one source but in inventory and worth flagging.
**Cuts Consensus:** Cards recommended for removal by two or more sources.
**Conflicts Resolved:** Any cross-source disagreements and how they were resolved.
**Bracket Flags:** Any cards flagged during the bracket classification check.

---

## Universal Rules (Both Scenarios)

These apply regardless of scenario.

**Bracket Override:** No source recommendation, synergy score, or inclusion rate overrides a bracket constraint violation. If a card violates the bracket target, it is excluded. Period.

**Inventory Preference:** At equivalent power level and theme fit, an owned card always beats a purchase recommendation. Never recommend purchasing a card when an inventory alternative exists that serves the same mechanical role.

**Theme Preservation:** Where `overview.md` specifies a theme preservation preference, apply it as an active filter throughout synthesis. Flag when a recommendation conflicts with theme preservation and let the user decide — do not silently exclude theme-conflicting cards, but do note the conflict explicitly.

**No Inherited Bracket Assessments:** Apply `bracket-constraints.md` independently. A guide calling something "casual-friendly" or "safe for any table" is not a bracket assessment. Evaluate the card on its mechanics, GC status, and combo potential.
