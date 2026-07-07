using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using Dapper;
using MtgStatsApp.Services;

namespace MtgStatsApp.Views
{
    public partial class DashboardPage : Page
    {
        public DashboardPage()
        {
            InitializeComponent();
            LoadStats();
        }

        private void LoadStats()
        {
            try
            {
                using (var connection = DbService.GetConnection())
                {
                    // 1. Core game counts
                    int totalGames = connection.ExecuteScalar<int>("SELECT COUNT(*) FROM games;");
                    int liveGames = connection.ExecuteScalar<int>("SELECT COUNT(*) FROM games WHERE source = 'live';");
                    int hordeGames = connection.ExecuteScalar<int>("SELECT COUNT(*) FROM games WHERE source = 'horde';");

                    TxtTotalGames.Text = totalGames.ToString();
                    TxtLiveGames.Text = liveGames.ToString();
                    TxtHordeGames.Text = hordeGames.ToString();

                    // Show empty state if no games logged
                    if (totalGames == 0)
                    {
                        CardEmptyState.Visibility = Visibility.Visible;
                        return;
                    }
                    else
                    {
                        CardEmptyState.Visibility = Visibility.Collapsed;
                    }

                    // 2. Horde Win Rate
                    if (hordeGames > 0)
                    {
                        int hordeWins = connection.ExecuteScalar<int>("SELECT COUNT(*) FROM horde_games WHERE result = 'win';");
                        double winRate = (double)hordeWins / hordeGames * 100;
                        TxtHordeWinRate.Text = $"{winRate:F0}%";
                    }
                    else
                    {
                        TxtHordeWinRate.Text = "N/A";
                    }

                    // 3. Gameplay Metrology Averages
                    double? avgTurns = connection.ExecuteScalar<double?>("SELECT AVG(turn_count) FROM games WHERE turn_count IS NOT NULL;");
                    TxtAvgTurns.Text = avgTurns.HasValue ? $"{avgTurns.Value:F1} turns" : "N/A";

                    double? avgSalt = connection.ExecuteScalar<double?>("SELECT AVG(salt_observed) FROM games WHERE salt_observed IS NOT NULL;");
                    TxtAvgSalt.Text = avgSalt.HasValue ? $"{avgSalt.Value:F1} / 10" : "N/A";

                    double? avgWipesFaced = connection.ExecuteScalar<double?>("SELECT AVG(opponent_wipe_count) FROM games WHERE opponent_wipe_count IS NOT NULL;");
                    TxtAvgWipesFaced.Text = avgWipesFaced.HasValue ? $"{avgWipesFaced.Value:F1}" : "N/A";

                    // Wipe recovery rate
                    int gamesWithWipes = connection.ExecuteScalar<int>("SELECT COUNT(*) FROM games WHERE opponent_wipe_count > 0;");
                    if (gamesWithWipes > 0)
                    {
                        int gamesRecovered = connection.ExecuteScalar<int>("SELECT COUNT(*) FROM games WHERE recovered_from_wipe = 1 AND opponent_wipe_count > 0;");
                        double recoveryRate = (double)gamesRecovered / gamesWithWipes * 100;
                        TxtWipeRecoveryRate.Text = $"{recoveryRate:F0}%";
                    }
                    else
                    {
                        TxtWipeRecoveryRate.Text = "N/A";
                    }

                    // 4. Top Played Decks List
                    var topDecks = connection.Query<TopDeckItem>(@"
                        SELECT d.deck_name AS DeckName, COUNT(*) AS PlayCount 
                        FROM games g 
                        JOIN decks d ON g.deck_id = d.deck_id 
                        GROUP BY g.deck_id 
                        ORDER BY PlayCount DESC 
                        LIMIT 5;"
                    ).ToList();

                    LstTopDecks.ItemsSource = topDecks;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading stats: {ex.Message}", "Database Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private class TopDeckItem
        {
            public string DeckName { get; set; } = string.Empty;
            public int PlayCount { get; set; }
        }
    }
}
