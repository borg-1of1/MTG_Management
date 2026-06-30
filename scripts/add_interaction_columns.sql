-- Migration: Add interaction and turn tracking columns to games
-- Safe to run against an empty .db -- no data migration needed.
-- All columns nullable: NULL = not logged, consistent with existing schema conventions.
-- recovered_from_wipe should be NULL when opponent_wipe_count = 0 (not a logging error).

ALTER TABLE games ADD COLUMN commander_recast_count INTEGER;
ALTER TABLE games ADD COLUMN my_wipe_count          INTEGER;
ALTER TABLE games ADD COLUMN opponent_wipe_count     INTEGER;
ALTER TABLE games ADD COLUMN recovered_from_wipe     INTEGER; -- 0 = false, 1 = true, NULL = no opponent wipes occurred
ALTER TABLE games ADD COLUMN turn_count              INTEGER;
