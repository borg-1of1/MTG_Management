# Mechanics Notes — The Wise Mothman (Mutant Menace)

This file is the card oracle reference for this deck. It defines exact mechanical
interactions between key cards to ensure consistent AI evaluation. Load this file
alongside the decklist when running sessions that involve complex interaction questions.

Last Updated: 2026-06-06

---

## Core Engine

### The Wise Mothman
- Flying
- Whenever The Wise Mothman enters the battlefield or attacks, each player gets a rad counter
- Whenever one or more nonland cards are milled, put a +1/+1 counter on each of up to X
  target creatures, where X is the number of nonland cards milled this way

### Rad Counter (Rule 723)
- At the beginning of the precombat main phase of a player with one or more rad counters,
  that player mills cards equal to the number of rad counters they have
- For each nonland card milled this way, that player loses 1 life and removes a rad counter
- **Key interaction:** Rad counters self-remove as they trigger — the engine naturally decelerates
  unless additional rad counters are added via proliferate

### Mothman Egg (functions as Mesmeric Orb)
- Whenever a permanent becomes untapped, that permanent's controller mills a card
- **Key interaction:** This triggers on ALL permanents untapping — including opponents' lands
  at the start of their untap step, making it a continuous mill engine for all players

### Mindcrank
- Whenever an opponent loses life, that player mills that many cards
- **Key interaction with Rad and Syr Konrad in multiplayer:**
  - Rad causes life loss → Mindcrank mills that player
  - Milled creatures trigger Syr Konrad: "each opponent" loses 1 life
  - Each opponent losing life triggers Mindcrank separately — milling each of them
  - More milled nonland cards trigger Mothman to distribute more counters
  - More milled creatures trigger Konrad again against each opponent
- **Multiplayer scope is what can make this engine self-sustaining.** In a four-player game,
  one creature entering a graveyard generates three Konrad triggers (one per opponent),
  each triggering Mindcrank on a different player. The engine feeds itself as long as
  creatures keep hitting graveyards across all players.
- **This is not infinite by definition** — it terminates when libraries are exhausted or
  opponents are eliminated. Milled creature cards transition from library to graveyard,
  which is what triggers Syr Konrad — the graveyard is the destination, not the source.
  However in a multiplayer game it can close out the table in one or two trigger cycles
  once it reaches critical mass.
- **Bracket 3 assessment:** Confirmed legal. Neither Mindcrank nor Syr Konrad is on the
  Game Changers list. The combo is indeterminate — the outcome depends on variables
  outside your control (creatures in graveyards across all players, available interaction,
  board state) rather than producing a guaranteed result. This is a synergy, not a true
  combo. However the multiplayer scaling means this engine should be disclosed under
  Rule Zero at bracket-mixed tables.
  See Resolved Questions in mutant-menace-overview.md.

---

## Counter Multipliers

### Stacking Rules
When multiple multipliers are in play simultaneously, they apply in timestamp order
(the order they entered the battlefield). This matters for calculating final counter totals.

### Hardened Scales
- If one or more +1/+1 counters would be put on a creature you control, that many plus
  one +1/+1 counters are put on it instead
- **Effect:** +1 to every counter placement on your creatures

### Winding Constrictor
- If one or more counters would be put on an artifact or creature you control, that many
  plus one of each kind are put on it instead
- If you would get one or more counters, you get that many plus one of each kind instead
- **Effect:** +1 to every counter placement (broader than Hardened Scales — includes artifacts
  and counters on you, not just creatures)

### Corpsejack Menace
- If one or more +1/+1 counters would be put on a creature you control, twice that many
  are put on it instead
- **Effect:** Doubles all +1/+1 counter placements on your creatures

### Branching Evolution
- If one or more +1/+1 counters would be put on a creature you control, twice that many
  are put on it instead
- **Effect:** Doubles all +1/+1 counter placements on your creatures (identical to Corpsejack)
- **Note:** Corpsejack + Branching Evolution stack multiplicatively with each other

### Tekuthal, Inquiry Dominus
- If you would proliferate, proliferate twice instead
- **Effect:** Every proliferate trigger doubles — each proliferate event becomes two

---

## Protection Package

### Ripples of Potential
- Proliferate, then choose any number of creatures you control that have counters.
  Those creatures phase out until your next turn
- **Key use:** In response to a board wipe — creatures phase out and return with counters intact

### Mutational Advantage
- You gain hexproof until end of turn
- Choose any number of permanents you control with counters — they gain indestructible
  until end of turn
- Proliferate
- **Key use:** Protects the board from targeted removal and board wipes while also proliferating

### Inspiring Call
- Draw a card for each creature you control with a +1/+1 counter on it
- Those creatures gain indestructible until end of turn
- **Key use:** Doubles as draw engine and board protection — highly efficient in a counter-heavy board

---

## High-Impact Creatures

### Deepglow Skate
- When Deepglow Skate enters the battlefield, double the number of each kind of counter
  on each permanent you control
- **Key use:** Functions as a one-turn "win now" button — doubles all counters on all permanents
  simultaneously, often moving creatures into lethal swing territory

### Fathom Mage
- Whenever one or more +1/+1 counters are put on Fathom Mage, draw that many cards
- **Key interaction with Mothman:** Every time Mothman triggers from a milled nonland card,
  if Fathom Mage is a target, you draw cards equal to counters placed

### Syr Konrad, the Grim
- Whenever another creature dies, or a creature card leaves a graveyard, or a creature
  card is put into a graveyard from anywhere, each opponent loses 1 life
- **Key interaction with Mindcrank and Rad:** Opponents losing life from Konrad triggers
  Mindcrank to mill more cards, which can trigger Konrad again if creatures are milled.
  This is the deck's primary non-combat damage engine.

### Insidious Roots
- Whenever one or more creature cards leave your graveyard, create a 0/1 green Plant token
  for each card that left
- Those tokens get +1/+1 for each land you control
- **Key interaction with Reanimate/Shigeki:** Each recursion event generates tokens scaled
  to your land count — late game these become significant threats

---

## Interaction Notes

**Rad + Winding Constrictor:** Winding Constrictor adds +1 to rad counters placed on
you via Mothman's "each player gets a rad counter" trigger. This accelerates your own
radiation but also increases the mill/life loss you take.

**Deepglow Skate + Tekuthal:** If Tekuthal is in play when Deepglow Skate enters,
the Skate trigger doubles all counters — including any proliferate counters already
on permanents. They do not directly interact (Skate is an ETB, not a proliferate).

**Mesmeric Orb (Mothman Egg) timing:** The untap trigger happens during the untap step,
before priority is passed. This means milling from Mesmeric Orb happens before any
player can respond at the start of each turn.
