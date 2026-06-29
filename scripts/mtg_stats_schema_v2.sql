-- MTG Deck Stats Tracking — v2 Schema
-- Source of truth: single SQLite file. Portable, scriptable, no vendor lock.
--
-- This supersedes v1 in full. No data existed in the live .db at the time of
-- this rewrite, so `deck` (free text) was replaced outright by `deck_id`
-- (FK) rather than migrated — there was nothing to preserve. If this file
-- is ever run against a .db that already has rows, STOP: that assumption
-- no longer holds, and a real backfill migration is needed instead of a
-- drop/rebuild. See the bottom of this file for that scenario.
--
-- Design notes (see session discussion for full rationale):
--   - `source` distinguishes Horde (fixed/non-adaptive aggro gauntlet, no
--     board-state response, can be solo or multiplayer) from Live
--     (multiplayer, low iteration, the only place interaction/political
--     data is real).
--   - `salt_prior` and `salt_observed` are split intentionally:
--       prior    = standing reputation of the deck/commander at table, as
--                  of this game (captured per-row so later changes to a
--                  deck's reputation don't retroactively reinterpret old
--                  games)
--       observed = what actually happened THIS game, Live only.
--     The gap between prior and observed is itself the useful signal —
--     e.g. a non-salty deck getting focused anyway flags a one-off cause
--     worth investigating outside this table.
--   - `commander_cast_turn` is NULL (not 0/99) when the commander was never
--     cast, so AVG()/aggregate queries naturally exclude those games
--     instead of skewing the result.
--   - `deck_id` replaces the v1 free-text `deck` column. Moxfield has no
--     API, so this is still hand-maintained, not automated — the FK's job
--     is to stop a typo from silently forking a deck's stats across two
--     names, not to sync with Moxfield. `decks.deck_name` stores the
--     deck's real name with any Moxfield status prefix stripped.
--   - Horde-specific columns (player count, life, deck size, draw rate,
--     token multiplier, milestone %, horde_deck_id, result) are nullable
--     and only meaningful when source = 'horde'. They live directly on
--     `games`, NOT behind a profile-table indirection, because they are
--     the user's active benchmarking/tuning variables (e.g. "find the life
--     total where this deck's win rate crosses 50%"), not incidental setup
--     to abstract away.
--   - The against-the-horde.com "Optional Rules" toggles (evenly distribute
--     tokens / horde has life points / alt draw mode / tokens to zones /
--     random starting permanent / milestones as secondary deck) are
--     deliberately NOT modeled as structured columns. They are almost
--     never touched in practice — a boolean nobody sets isn't pulling
--     weight. If one is ever toggled, note it in `notes` instead.
--   - `result` is well-defined for Horde (fixed, non-political adversary —
--     "did the table beat the Horde" is unambiguous regardless of player
--     count) but deliberately NOT used for Live multiplayer, where
--     win/loss has no single clean meaning. This is an application-level
--     convention, not DB-enforced: SQLite CHECK constraints can't cleanly
--     enforce "non-null only when source='horde'" without more structural
--     overhead than this earns. Treat `result` populated on a 'live' row
--     as a logging error to catch in review.
--   - `notes` is an intentional escape hatch, expected to stay mostly empty.
--     If it's filled in every game, that's a signal a new column wants to
--     exist instead of free text.

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- Reference table: your own decks.
-- One-time manual entry per deck, before that deck's first logged game.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decks (
    deck_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name    TEXT NOT NULL UNIQUE,   -- real deck name, Moxfield status prefix stripped
    moxfield_url TEXT,                   -- manual reference only, not a live/synced link
    notes        TEXT
);

-- ----------------------------------------------------------------------------
-- Reference table: Horde decks — both the 7 official against-the-horde.com
-- decks and any player-built ones actually played. Same hand-maintained,
-- one-time-entry treatment as `decks`.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS horde_decks (
    horde_deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name     TEXT NOT NULL UNIQUE,
    is_official   INTEGER NOT NULL CHECK (is_official IN (0, 1)),  -- 1 = official default, 0 = player-built
    source_url    TEXT,    -- nullable; most useful for player-built decks so they can be found again
    notes         TEXT
);

-- ----------------------------------------------------------------------------
-- Main table.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS games (
    game_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date                 TEXT NOT NULL,                  -- ISO 8601, e.g. '2026-06-28'
    deck_id              INTEGER NOT NULL REFERENCES decks(deck_id),
    source               TEXT NOT NULL CHECK (source IN ('horde', 'live')),

    -- Lands stage
    lands_drawn_opening   INTEGER,                       -- lands in opening hand (post-mulligan-decision hand)

    -- Pregame stage
    mulligan_count        INTEGER NOT NULL DEFAULT 0,    -- number of mulligans taken

    -- Commander-on-curve stage
    commander_cast_turn   INTEGER,                       -- NULL = never cast this game

    -- Salt / table-targeting (Live-relevant; prior may still be recorded for Horde for consistency, observed will just be NULL there)
    salt_prior             INTEGER NOT NULL DEFAULT 0 CHECK (salt_prior IN (0, 1)),
    salt_observed          INTEGER CHECK (salt_observed IN (0, 1)),  -- NULL when not applicable (e.g. Horde)

    -- Horde-specific configuration and outcome (NULL when source = 'live')
    horde_players         INTEGER CHECK (horde_players >= 1),
    survivor_life         INTEGER CHECK (survivor_life IN (20, 40, 60, 80)),
    deck_size_pct         INTEGER CHECK (deck_size_pct IN (50, 75, 100, 200)),
    draws_per_turn        INTEGER CHECK (draws_per_turn IN (1, 2, 3)),
    token_multiplier      INTEGER CHECK (token_multiplier IN (1, 2, 3, 4)),
    milestone_pct         INTEGER CHECK (milestone_pct IN (25, 50, 75, 100)),
    horde_deck_id         INTEGER REFERENCES horde_decks(horde_deck_id),
    result                TEXT CHECK (result IN ('win', 'loss')),  -- Horde-only by convention, see notes above

    notes                  TEXT

    -- Future, deliberately NOT added yet (see open threads):
    --   interaction/removal timing — likely a separate child table keyed
    --     on game_id, since it's naturally many-rows-per-game, not one
    --     (same shape as horde_co_op_decks below)
);

-- ----------------------------------------------------------------------------
-- Child table: co-op partner decks for multiplayer Horde games.
-- Zero rows for solo games. One row per *other* deck at the table.
-- Free text by design — these aren't your decks, no canonical registry
-- exists or is needed; the goal is pattern-spotting (e.g. "every loss has
-- an Eldrazi commander present"), not a clean join.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS horde_co_op_decks (
    co_op_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id         INTEGER NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    co_op_commander TEXT NOT NULL   -- e.g. "Atraxa", or a partner's custom deck name if they have one
);

-- ----------------------------------------------------------------------------
-- Indexes for the query patterns already discussed.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_games_deck_id        ON games(deck_id);
CREATE INDEX IF NOT EXISTS idx_games_source         ON games(source);
CREATE INDEX IF NOT EXISTS idx_games_date           ON games(date);
CREATE INDEX IF NOT EXISTS idx_games_horde_deck_id  ON games(horde_deck_id);
CREATE INDEX IF NOT EXISTS idx_games_result         ON games(result);
CREATE INDEX IF NOT EXISTS idx_horde_co_op_game_id  ON horde_co_op_decks(game_id);

-- ----------------------------------------------------------------------------
-- IF THIS IS EVER RUN AGAINST A .db THAT ALREADY HAS GAMES ROWS:
-- Do not run this file as-is — it will fail (deck_id NOT NULL with no
-- default, no source for it) or silently lose the old `deck` column's
-- data if adapted carelessly. Instead:
--   1. INSERT INTO decks (deck_name) SELECT DISTINCT deck FROM games;
--   2. ALTER TABLE games ADD COLUMN deck_id INTEGER REFERENCES decks(deck_id);
--   3. UPDATE games SET deck_id = (SELECT deck_id FROM decks WHERE decks.deck_name = games.deck);
--   4. Verify every row got a non-NULL deck_id before proceeding.
--   5. Rebuild the table to drop the old `deck` column and its index
--      (idx_games_deck) — SQLite 3.35+ supports DROP COLUMN directly;
--      confirm version first.
-- This was not needed this time since the live .db was empty.
-- ----------------------------------------------------------------------------
