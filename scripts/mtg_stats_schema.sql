-- MTG Deck Stats Tracking — v1 Schema
-- Source of truth: single SQLite file. Portable, scriptable, no vendor lock.
--
-- Design notes (see session discussion for full rationale):
--   - `source` distinguishes Horde (solo, fixed/non-adaptive aggro gauntlet,
--     high iteration, no board-state response) from Live (multiplayer,
--     low iteration, the only place interaction/political data is real).
--   - `salt_prior` and `salt_observed` are split intentionally:
--       prior  = standing reputation of the deck/commander at table, as of
--                this game (captured per-row so later changes to a deck's
--                reputation don't retroactively reinterpret old games)
--       observed = what actually happened THIS game, Live only.
--     The gap between prior and observed is itself the useful signal —
--     e.g. a non-salty deck getting focused anyway flags a one-off cause
--     worth investigating outside this table.
--   - `commander_cast_turn` is NULL (not 0/99) when the commander was never
--     cast, so AVG()/aggregate queries naturally exclude those games
--     instead of skewing the result.
--   - `result` deliberately omitted from v1 — flagged as not yet meaningful
--     across both sources (Horde win/loss is well-defined; Live multiplayer
--     win/loss less so) and tied to an open follow-up about capturing which
--     Horde opponent/deck was faced. Revisit later as its own addition.
--   - `notes` is an intentional escape hatch, expected to stay mostly empty.
--     If it's filled in every game, that's a signal a new column wants to
--     exist instead of free text.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS games (
    game_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date                 TEXT NOT NULL,                  -- ISO 8601, e.g. '2026-06-28'
    deck                 TEXT NOT NULL,                  -- matches deck name used elsewhere in repo
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

    notes                  TEXT

    -- Future, deliberately NOT added yet (see open threads):
    --   result columns — meaning differs by source, revisit separately
    --   horde_opponent_deck / horde_details — pending follow-up discussion
    --   interaction/removal timing — likely a separate child table keyed
    --     on game_id, since it's naturally many-rows-per-game, not one
);

-- Helpful indexes for the query patterns already discussed
CREATE INDEX IF NOT EXISTS idx_games_deck   ON games(deck);
CREATE INDEX IF NOT EXISTS idx_games_source ON games(source);
CREATE INDEX IF NOT EXISTS idx_games_date   ON games(date);
