# Build-From-Inventory Session Prompt

## Purpose

Use this prompt to initiate a deck-building session from scratch using cards you already own. This is not an upgrade session — no existing decklist is required. The output will be a `build-candidates.md` file ready for review and promotion to a final decklist.

---

## How to Use This Prompt

Copy the template below, fill in all sections you have answers to, and submit. The AI will ask clarifying questions for anything missing before beginning Phase 0.

You do not need to complete every field before starting — but **Bracket** and **Inventory** are required before any card selection begins.

---

## Session Prompt Template

```
## MTG Deck Build Session

### Entry Mode
<!-- Choose one: Commander-Led | Theme-Led | Commander + Theme -->
[Your entry mode]

### Commander (if known)
[Commander name, or "TBD — see theme below"]

### Theme / Archetype
[Describe the intended strategy. Examples: aristocrats, group hug, voltron, token swarm, 
spellslinger, stax, big mana, reanimator, counters, chaos, tribal (specify tribe)]

### Bracket Target
<!-- Required. Options: Bracket 1 | Bracket 2 | Bracket 3 | Bracket 4 | Bracket 5 -->
[Your bracket]

### Format
<!-- Default: Commander. Specify if different. -->
[Commander / Oathbreaker / Other]

### Inventory
<!-- Paste your card list, spreadsheet export, or describe your collection.
     The more specific, the better. At minimum, list cards you know you want considered. -->
[Your inventory here]

### Additional Context
<!-- Optional. Examples: 
     - "I want this to be a budget build"
     - "I have a strong creature base but few instants/sorceries"
     - "I want this playable in both casual and competitive pods"
     - "I already know I want [card X] and [card Y] in the deck" -->
[Any additional notes]
```

---

## What Happens Next

Once the prompt is submitted, the AI will:

1. **Confirm the entry mode** and ask any required clarifying questions (bracket, commander selection if theme-led, etc.)
2. **Acknowledge Phase 0 inputs** — summarize what was provided and what was assumed
3. **Proceed phase by phase**, presenting candidates at each phase for your review before advancing
4. **Produce a `build-candidates.md` file** at the end of Phase 6

You can interrupt at any phase boundary to adjust, cut candidates, or redirect.

---

## Example Prompts

### Commander-Led Example

```
## MTG Deck Build Session

### Entry Mode
Commander-Led

### Commander
Prossh, Skyraider of Kher

### Theme / Archetype
Aristocrats / sacrifice value. Use Prossh's tokens as fodder. Win through 
Food Chain combo if the bracket supports it, otherwise drain and impact tremors effects.

### Bracket Target
Bracket 3

### Format
Commander

### Inventory
[inventory list]

### Additional Context
I have a deep collection of black sacrifice payoffs. Light on green ramp.
```

### Theme-Led Example

```
## MTG Deck Build Session

### Entry Mode
Theme-Led

### Commander
TBD

### Theme / Archetype
Zombie tribal. I want to grind value through recursion and ETB effects,
win through overwhelming board presence or Rooftop Storm combo lines.

### Bracket Target
Bracket 2

### Format
Commander

### Inventory
[inventory list]

### Additional Context
I have Gravecrawler, Phyrexian Altar, and most of the classic zombie payoffs.
Open to mono-black or Dimir commanders.
```

---

## Loading Instructions

Before beginning a session, load the following files in addition to this prompt:

| File | Purpose |
|------|---------|
| `protocols/build-from-inventory-logic.md` | Core build rules and phase structure |
| `protocols/bracket-constraints.md` | Legality guardrails by bracket |
| `protocols/master-deckbuilding-logic.md` | Shared foundational principles |
| `protocols/input-contract.md` | Input validation rules |

Provide your inventory in the format your collection tool exports, or paste a plain list. The AI will work with whatever format is provided.
