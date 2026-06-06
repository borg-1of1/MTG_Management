# MTG Management
## Structure
This outlines the Obsidian Vault structure I am using for my deck management system.  This may found in other documents, but this is the authoritative source as this is at the root level and was developed after those documents.  Those documents will be updated either to remove any structural reference or to reflect this reference.

### repo structure
MTG_Management/
├── decks/
│   ├── deck-name/
│   │   ├── overview.md         # Commander, theme, Bracket rating
│   │   ├── decklist.md         # Current list
│   │   ├── upgrade-log.md      # What changed and why
│   │   └── upgrade-candidates.md  # Researched options, tiered
├── cards/
│   └── [optional per-card notes for heavily-used pieces]
├── inventory/
│   ├── moxfield-export.csv     # Raw export
│   └── inventory-notes.md      # Quirks, proxies, condition flags
├── protocols/
│   ├── master_deckbuilding_logic.md
│   ├── input_contract.md  # defines _Global_Inventory, Current_decklist_ format
│   └── bracket3-constraints.md # Your guardrails codified
└── scripts/
    └── inventory-check.py      # CSV cross-reference automation

