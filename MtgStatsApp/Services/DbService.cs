using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using Microsoft.Data.Sqlite;
using Dapper;

namespace MtgStatsApp.Services
{
    public class Deck
    {
        public int DeckId { get; set; }
        public string DeckName { get; set; } = string.Empty;
        public string? MoxfieldUrl { get; set; }
        public string? Notes { get; set; }
    }

    public class HordeDeck
    {
        public int HordeDeckId { get; set; }
        public string DeckName { get; set; } = string.Empty;
        public int IsOfficial { get; set; } = 0; // 0 = community, 1 = official
        public string? SourceUrl { get; set; }
        public string? Notes { get; set; }
    }

    public class Game
    {
        public int GameId { get; set; }
        public string Date { get; set; } = string.Empty;
        public int DeckId { get; set; }
        public string Source { get; set; } = string.Empty; // 'live' or 'horde'
        public int? LandsDrawnOpening { get; set; }
        public int? MulliganCount { get; set; }
        public int? CommanderCastTurn { get; set; }
        public int? SaltPrior { get; set; }
        public int? SaltObserved { get; set; }
        public int? CommanderRecastCount { get; set; }
        public int? MyWipeCount { get; set; }
        public int? OpponentWipeCount { get; set; }
        public int? RecoveredFromWipe { get; set; } // 0 or 1, or null
        public int? TurnCount { get; set; }
        public string? Notes { get; set; }
    }

    public class HordeGame
    {
        public int GameId { get; set; }
        public int? HordePlayers { get; set; }
        public int? SurvivorLife { get; set; }
        public int? DeckSizePct { get; set; }
        public int? DrawsPerTurn { get; set; }
        public int? TokenMultiplier { get; set; }
        public int? MilestonePct { get; set; }
        public int? HordeDeckId { get; set; }
        public string? Result { get; set; } // 'win' or 'loss'
    }

    public class GameHistoryItem
    {
        public int GameId { get; set; }
        public string Date { get; set; } = string.Empty;
        public int DeckId { get; set; }
        public string DeckName { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public int? LandsDrawnOpening { get; set; }
        public int? MulliganCount { get; set; }
        public int? CommanderCastTurn { get; set; }
        public int? SaltPrior { get; set; }
        public int? SaltObserved { get; set; }
        public int? CommanderRecastCount { get; set; }
        public int? MyWipeCount { get; set; }
        public int? OpponentWipeCount { get; set; }
        public int? RecoveredFromWipe { get; set; }
        public int? TurnCount { get; set; }
        public string? Notes { get; set; }

        // Horde specific columns
        public int? HordePlayers { get; set; }
        public int? SurvivorLife { get; set; }
        public int? DeckSizePct { get; set; }
        public int? DrawsPerTurn { get; set; }
        public int? TokenMultiplier { get; set; }
        public int? MilestonePct { get; set; }
        public int? HordeDeckId { get; set; }
        public string? HordeDeckName { get; set; }
        public string? Result { get; set; }
        
        // Co-op commanders
        public string? CoOpCommanders { get; set; }
    }

    public static class DbService
    {
        private static string _connectionString = string.Empty;
        private static string _dbPath = string.Empty;

        public static string DatabasePath => _dbPath;

        public static void Initialize(string dbPath)
        {
            _dbPath = dbPath;
            var builder = new SqliteConnectionStringBuilder
            {
                DataSource = dbPath
            };
            _connectionString = builder.ConnectionString;

            // Initialize connection and enable foreign keys, then check/create schema
            using (var connection = GetConnection())
            {
                connection.Open();
                
                // Check if the 'decks' table exists. If not, seed the database schema.
                var tableCheck = connection.QueryFirstOrDefault<string>(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='decks';"
                );

                if (string.IsNullOrEmpty(tableCheck))
                {
                    CreateSchema(connection);
                }
            }
        }

        public static SqliteConnection GetConnection()
        {
            if (string.IsNullOrEmpty(_connectionString))
            {
                throw new InvalidOperationException("Database has not been initialized. Please set the database path.");
            }

            var connection = new SqliteConnection(_connectionString);
            
            // Set PRAGMA foreign_keys = ON immediately on opening (before any command runs)
            connection.StateChange += (sender, e) =>
            {
                if (e.CurrentState == ConnectionState.Open)
                {
                    using (var command = connection.CreateCommand())
                    {
                        command.CommandText = "PRAGMA foreign_keys = ON;";
                        command.ExecuteNonQuery();
                    }
                }
            };

            return connection;
        }

        private static void CreateSchema(SqliteConnection connection)
        {
            string schemaSql = @"
CREATE TABLE decks (
    deck_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name    TEXT    NOT NULL,
    moxfield_url TEXT,
    notes        TEXT
);

CREATE TABLE horde_decks (
    horde_deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name     TEXT    NOT NULL,
    is_official   INTEGER NOT NULL DEFAULT 0 CHECK (is_official IN (0, 1)),
    source_url    TEXT,
    notes         TEXT
);

CREATE TABLE games (
    game_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date                  TEXT    NOT NULL,
    deck_id               INTEGER NOT NULL REFERENCES decks (deck_id),
    source                TEXT    NOT NULL CHECK (source IN ('live', 'horde')),
    lands_drawn_opening   INTEGER,
    mulligan_count        INTEGER,
    commander_cast_turn   INTEGER,
    salt_prior            INTEGER,
    salt_observed         INTEGER,
    commander_recast_count INTEGER,
    my_wipe_count          INTEGER,
    opponent_wipe_count    INTEGER,
    recovered_from_wipe    INTEGER CHECK (recovered_from_wipe IN (0, 1)),
    turn_count             INTEGER,
    notes                  TEXT
);

CREATE INDEX idx_games_deck_id ON games (deck_id);
CREATE INDEX idx_games_date    ON games (date);
CREATE INDEX idx_games_source  ON games (source);

CREATE TABLE live_games (
    game_id INTEGER PRIMARY KEY REFERENCES games (game_id) ON DELETE CASCADE
);

CREATE TABLE horde_games (
    game_id          INTEGER PRIMARY KEY REFERENCES games (game_id) ON DELETE CASCADE,
    horde_players    INTEGER,
    survivor_life    INTEGER,
    deck_size_pct    INTEGER,
    draws_per_turn   INTEGER,
    token_multiplier INTEGER CHECK (token_multiplier BETWEEN 1 AND 4),
    milestone_pct    INTEGER,
    horde_deck_id    INTEGER REFERENCES horde_decks (horde_deck_id),
    result           TEXT CHECK (result IN ('win', 'loss'))
);

CREATE INDEX idx_horde_games_horde_deck_id ON horde_games (horde_deck_id);

CREATE TABLE horde_co_op_decks (
    co_op_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id        INTEGER NOT NULL REFERENCES games (game_id) ON DELETE CASCADE,
    co_op_commander TEXT
);

CREATE INDEX idx_horde_co_op_decks_game_id ON horde_co_op_decks (game_id);
";
            connection.Execute(schemaSql);
        }

        // Decks CRUD
        public static IEnumerable<Deck> GetDecks()
        {
            using (var connection = GetConnection())
            {
                return connection.Query<Deck>("SELECT * FROM decks ORDER BY deck_name;");
            }
        }

        public static void SaveDeck(Deck deck)
        {
            using (var connection = GetConnection())
            {
                if (deck.DeckId == 0)
                {
                    string sql = "INSERT INTO decks (deck_name, moxfield_url, notes) VALUES (@DeckName, @MoxfieldUrl, @Notes);";
                    connection.Execute(sql, deck);
                }
                else
                {
                    string sql = "UPDATE decks SET deck_name = @DeckName, moxfield_url = @MoxfieldUrl, notes = @Notes WHERE deck_id = @DeckId;";
                    connection.Execute(sql, deck);
                }
            }
        }

        public static void DeleteDeck(int deckId)
        {
            using (var connection = GetConnection())
            {
                connection.Execute("DELETE FROM decks WHERE deck_id = @deckId;", new { deckId });
            }
        }

        // Horde Decks CRUD
        public static IEnumerable<HordeDeck> GetHordeDecks()
        {
            using (var connection = GetConnection())
            {
                return connection.Query<HordeDeck>("SELECT * FROM horde_decks ORDER BY deck_name;");
            }
        }

        public static void SaveHordeDeck(HordeDeck deck)
        {
            using (var connection = GetConnection())
            {
                if (deck.HordeDeckId == 0)
                {
                    string sql = "INSERT INTO horde_decks (deck_name, is_official, source_url, notes) VALUES (@DeckName, @IsOfficial, @SourceUrl, @Notes);";
                    connection.Execute(sql, deck);
                }
                else
                {
                    string sql = "UPDATE horde_decks SET deck_name = @DeckName, is_official = @IsOfficial, source_url = @SourceUrl, notes = @Notes WHERE horde_deck_id = @HordeDeckId;";
                    connection.Execute(sql, deck);
                }
            }
        }

        public static void DeleteHordeDeck(int hordeDeckId)
        {
            using (var connection = GetConnection())
            {
                connection.Execute("DELETE FROM horde_decks WHERE horde_deck_id = @hordeDeckId;", new { hordeDeckId });
            }
        }

        // Log Game Transaction
        public static void LogGame(Game game, HordeGame? hordeGame, List<string> coOpCommanders)
        {
            using (var connection = GetConnection())
            {
                connection.Open();
                using (var transaction = connection.BeginTransaction())
                {
                    try
                    {
                        // 1. Insert into games header
                        string insertGameSql = @"
INSERT INTO games (
    date, deck_id, source, lands_drawn_opening, mulligan_count, commander_cast_turn, 
    salt_prior, salt_observed, commander_recast_count, my_wipe_count, 
    opponent_wipe_count, recovered_from_wipe, turn_count, notes
) VALUES (
    @Date, @DeckId, @Source, @LandsDrawnOpening, @MulliganCount, @CommanderCastTurn, 
    @SaltPrior, @SaltObserved, @CommanderRecastCount, @MyWipeCount, 
    @OpponentWipeCount, @RecoveredFromWipe, @TurnCount, @Notes
);
SELECT last_insert_rowid();";

                        int gameId = connection.QuerySingle<int>(insertGameSql, game, transaction);

                        if (game.Source == "live")
                        {
                            // 2. Insert into live_games
                            connection.Execute("INSERT INTO live_games (game_id) VALUES (@gameId);", new { gameId }, transaction);
                        }
                        else if (game.Source == "horde" && hordeGame != null)
                        {
                            // 2. Insert into horde_games
                            hordeGame.GameId = gameId;
                            string insertHordeSql = @"
INSERT INTO horde_games (
    game_id, horde_players, survivor_life, deck_size_pct, draws_per_turn, token_multiplier, milestone_pct, horde_deck_id, result
) VALUES (
    @GameId, @HordePlayers, @SurvivorLife, @DeckSizePct, @DrawsPerTurn, @TokenMultiplier, @MilestonePct, @HordeDeckId, @Result
);";
                            connection.Execute(insertHordeSql, hordeGame, transaction);

                            // 3. Insert into horde_co_op_decks
                            if (coOpCommanders != null && coOpCommanders.Count > 0)
                            {
                                foreach (var commander in coOpCommanders)
                                {
                                    if (!string.IsNullOrWhiteSpace(commander))
                                    {
                                        connection.Execute(
                                            "INSERT INTO horde_co_op_decks (game_id, co_op_commander) VALUES (@gameId, @commander);",
                                            new { gameId, commander = commander.Trim() },
                                            transaction
                                        );
                                    }
                                }
                            }
                        }

                        transaction.Commit();
                    }
                    catch
                    {
                        transaction.Rollback();
                        throw;
                    }
                }
            }
        }

        // Fetch Games History
        public static IEnumerable<GameHistoryItem> GetGamesHistory()
        {
            using (var connection = GetConnection())
            {
                string sql = @"
SELECT 
    g.*,
    d.deck_name AS DeckName,
    hg.horde_players AS HordePlayers,
    hg.survivor_life AS SurvivorLife,
    hg.deck_size_pct AS DeckSizePct,
    hg.draws_per_turn AS DrawsPerTurn,
    hg.token_multiplier AS TokenMultiplier,
    hg.milestone_pct AS MilestonePct,
    hg.horde_deck_id AS HordeDeckId,
    hd.deck_name AS HordeDeckName,
    hg.result AS Result,
    (SELECT group_concat(co_op_commander, ', ') FROM horde_co_op_decks WHERE game_id = g.game_id) AS CoOpCommanders
FROM games g
JOIN decks d ON g.deck_id = d.deck_id
LEFT JOIN horde_games hg ON g.game_id = hg.game_id
LEFT JOIN horde_decks hd ON hg.horde_deck_id = hd.horde_deck_id
ORDER BY g.date DESC, g.game_id DESC;";

                return connection.Query<GameHistoryItem>(sql);
            }
        }

        // Delete Game
        public static void DeleteGame(int gameId)
        {
            using (var connection = GetConnection())
            {
                // Deleting from games will cascade-delete live_games, horde_games, and horde_co_op_decks due to REFERENCES ... ON DELETE CASCADE
                connection.Execute("DELETE FROM games WHERE game_id = @gameId;", new { gameId });
            }
        }
    }
}
