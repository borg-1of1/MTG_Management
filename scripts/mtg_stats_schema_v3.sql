-- MTG Stats Schema v3
-- Replaces v2 in full. Safe to apply against an empty .db (no migration needed).
--
-- Structure overview:
--   decks              — reference table for the user's own decks
--   horde_decks        — reference table for Horde format decks (official + community)
--   games              — header table, one row per game regardless of format
--                        source = 'live' | 'horde' enforced by CHECK constraint
--                        shared metrics (opening hand, salt, interaction, turn count) live here
--   live_games         — child table, one-to-one with games where source = 'live'
--                        currently a FK anchor; Live-specific columns added here as needed
--   horde_games        — child table, one-to-one with games where source = 'horde'
--                        all Horde-specific config knobs and result live here
--   horde_co_op_decks  — child table, many-per-game, Horde co-op partner deck tracking
--
-- IMPORTANT: PRAGMA foreign_keys = ON is a per-connection setting in SQLite.
-- It is NOT persistent in the database file. Every tool/script/connection that
-- writes to this database must set this pragma explicitly before any writes,
-- or FK enforcement and cascade-deletes will silently not fire.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Reference Tables
-- ---------------------------------------------------------------------------

CREATE TABLE decks (
    deck_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name    TEXT    NOT NULL,
    -- Real name only — do NOT include Moxfield status prefixes (e.g. [Active], [Retired])
    moxfield_url TEXT,
    notes        TEXT
);

CREATE TABLE horde_decks (
    horde_deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name     TEXT    NOT NULL,
    is_official   INTEGER NOT NULL DEFAULT 0 CHECK (is_official IN (0, 1)),
    -- 0 = community/custom, 1 = official against-the-horde.com deck
    source_url    TEXT,
    notes         TEXT
);

-- ---------------------------------------------------------------------------
-- Games Header Table
-- ---------------------------------------------------------------------------

CREATE TABLE games (
    game_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date                  TEXT    NOT NULL,
    -- ISO 8601 date: YYYY-MM-DD
    deck_id               INTEGER NOT NULL REFERENCES decks (deck_id),
    source                TEXT    NOT NULL CHECK (source IN ('live', 'horde')),

    -- Opening hand metrics
    lands_drawn_opening   INTEGER,
    mulligan_count        INTEGER,
    commander_cast_turn   INTEGER,

    -- Salt metrics
    salt_prior            INTEGER,
    -- Perceived salt level of the table/opponents before the game
    salt_observed         INTEGER,
    -- Actual salt level observed during the game

    -- Interaction metrics (shared across Live and Horde)
    commander_recast_count INTEGER,
    -- Your commander only; count of recasts as proxy for removal pressure received
    my_wipe_count          INTEGER,
    -- Board wipes you cast
    opponent_wipe_count    INTEGER,
    -- Board wipes opponents cast that affected you
    recovered_from_wipe    INTEGER CHECK (recovered_from_wipe IN (0, 1)),
    -- 0/1 boolean; NULL when opponent_wipe_count = 0 (not a logging error)

    -- Turn count (applies to both Live and Horde)
    turn_count             INTEGER,
    -- Live: bracket calibration signal (Bracket 3 should threaten win ~turn 6, Oct 2025 definition)
    -- Horde: benchmarking signal across configs or deck tweaks

    notes                  TEXT
    -- Free text: qualitative context, Horde Optional Rules toggles (rarely used), etc.
);

CREATE INDEX idx_games_deck_id ON games (deck_id);
CREATE INDEX idx_games_date    ON games (date);
CREATE INDEX idx_games_source  ON games (source);

-- ---------------------------------------------------------------------------
-- Live Games Child Table
-- ---------------------------------------------------------------------------

CREATE TABLE live_games (
    -- One-to-one with games where source = 'live'.
    -- game_id is both PK and FK — enforces the one-to-one relationship.
    -- Currently a structural anchor; Live-specific columns added here as needed
    -- without touching the games header table.
    game_id INTEGER PRIMARY KEY REFERENCES games (game_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------------
-- Horde Games Child Table
-- ---------------------------------------------------------------------------

CREATE TABLE horde_games (
    -- One-to-one with games where source = 'horde'.
    -- game_id is both PK and FK — enforces the one-to-one relationship.
    game_id          INTEGER PRIMARY KEY REFERENCES games (game_id) ON DELETE CASCADE,

    -- Co-op configuration
    horde_players    INTEGER,
    -- Number of players (including the user) facing the Horde

    -- Horde config knobs — the user's deliberate benchmarking variables.
    -- These are varied intentionally game-to-game to find performance inflection points
    -- (e.g., what survivor_life gives a 50% win rate against a given Horde deck).
    -- Do NOT hide behind a profile table — the variation IS the data.
    survivor_life    INTEGER,
    deck_size_pct    INTEGER,
    -- Starting deck size as a percentage of full deck
    draws_per_turn   INTEGER,
    token_multiplier INTEGER CHECK (token_multiplier BETWEEN 1 AND 4),
    milestone_pct    INTEGER,

    -- Horde deck identity
    horde_deck_id    INTEGER REFERENCES horde_decks (horde_deck_id),

    -- Result — meaningful for Horde (fixed non-political adversary, unambiguous win/loss)
    -- NULL on Live rows is enforced at the application/UI layer, not the DB layer
    -- (SQLite cannot cleanly enforce conditional nullability across tables without
    -- significant structural cost — accepted deliberate gap).
    result           TEXT CHECK (result IN ('win', 'loss'))
);

CREATE INDEX idx_horde_games_horde_deck_id ON horde_games (horde_deck_id);

-- ---------------------------------------------------------------------------
-- Horde Co-op Decks Child Table
-- ---------------------------------------------------------------------------

CREATE TABLE horde_co_op_decks (
    -- Many-per-game. Zero rows = solo Horde game.
    -- Anchored on game_id from the games header table (not horde_games) —
    -- game_id is the universal entry point for all game-related data.
    co_op_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id        INTEGER NOT NULL REFERENCES games (game_id) ON DELETE CASCADE,
    co_op_commander TEXT
    -- Free text — no canonical registry for other players' decks.
    -- Goal is pattern-spotting, not clean joins.
);

CREATE INDEX idx_horde_co_op_decks_game_id ON horde_co_op_decks (game_id);

-- ---------------------------------------------------------------------------
-- Migration Notes (for future reference — NOT needed for current empty .db)
-- ---------------------------------------------------------------------------
-- If this schema is ever applied against a .db that already has v2 data:
-- 1. Create decks/horde_decks/games from this file (already populated in v2).
-- 2. INSERT INTO live_games (game_id) SELECT game_id FROM games WHERE source = 'live'.
-- 3. INSERT INTO horde_games (game_id, horde_players, survivor_life, deck_size_pct,
--    draws_per_turn, token_multiplier, milestone_pct, horde_deck_id, result)
--    SELECT game_id, horde_players, survivor_life, deck_size_pct, draws_per_turn,
--    token_multiplier, milestone_pct, horde_deck_id, result
--    FROM games WHERE source = 'horde'.
-- 4. Drop Horde-specific columns from games (requires table rebuild in SQLite).
