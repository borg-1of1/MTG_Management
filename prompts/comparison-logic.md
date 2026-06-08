# Comparison Logic

**Task:** Conduct a pre-sync audit of the current deck state compared to the starting version for this session. This prompt is run at the end of a session before committing changes to Moxfield, or at the start of a session to confirm the deck state matches expectations.

> **This prompt supports any phase of the upgrade path defined in `master-deckbuilding-logic.md`.** It does not drive a phase on its own — it produces the audit output and Final Swap List that close out a phase or session.

---

## Analysis Checklist

Run each of the following checks against the session's proposed swaps before producing output.

### Mana Curve

Calculate the average CMC of the starting decklist and the proposed new decklist. State both values explicitly.

- If average CMC decreased or held flat: note this as a positive outcome.
- If average CMC increased: apply the Escalation Rule from `master-deckbuilding-logic.md` immediately. Do not proceed to the output section until this flag is acknowledged:

> **FLAG: Average CMC increased without ramp compensation. Confirm before proceeding.**

This flag must appear as a named, visible block — not as a line item inside The Risks section. If ramp was added to compensate for the CMC increase, note both the increase and the compensation explicitly and confirm whether the compensation is sufficient.

### Color Pips

Review the colored mana requirements of all cards being added. Compare against the current land base.

- Are the correct land proportions in place to reliably hit the required color pips on curve?
- If any swap introduces new pip requirements not previously present, flag it explicitly.
- If the land base needs adjustment to support the new pip requirements, note it as a recommended follow-up action.

### Inventory Utilization

List every card being added in this session that is sourced from `_Global_Inventory`. Label each with **[Inventory — $0]**. List every card being added that requires purchase separately, labeled with **[Purchase — ~$X]**.

### Bracket Status

Confirm the deck remains within its bracket target after all proposed swaps are applied.

- State current GC slot count after swaps: [X] of [maximum for bracket target]
- Note any flags raised during the session — bracket edge cases, Rule Zero disclosures, or escalation flags

---

## Output Format

### The Good

Summarize the strengths of the updated deck version. Focus on what improved mechanically relative to the four priority categories: Mana Consistency, Interaction, Card Draw, Win Conditions.

### The Risks

Summarize any concerns with the updated version. This includes curve increases with partial or no ramp compensation, cuts to interaction that leave the deck more exposed, or any bracket edge cases identified during the session. Do not bury escalation flags here — those must appear as named flags above before this section is reached.

### Bracket and GC Status

State the bracket target, current GC slot usage, and any flags or disclosures from this session.

### Final Swap List

Produce a clean list of all changes from this session formatted for direct copy into `changelog.md`. Use the entry format defined in `templates/changelog.md` — do not reproduce the template structure here, reference it. Populate every field. Do not leave template placeholders in the output. The Final Swap List should be ready to paste directly into `changelog.md` with no further editing required.
