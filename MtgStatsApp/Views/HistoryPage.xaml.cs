using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using MtgStatsApp.Services;

namespace MtgStatsApp.Views
{
    public partial class HistoryPage : Page
    {
        private GameHistoryItem? _selectedGame = null;

        public HistoryPage()
        {
            InitializeComponent();
            LoadGames();
        }

        private void LoadGames()
        {
            try
            {
                var games = DbService.GetGamesHistory().ToList();
                DgGames.ItemsSource = games;
            }
            catch (Exception ex)
            {
                ShowInfo($"Error loading game history: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void OnGameSelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (DgGames.SelectedItem is GameHistoryItem game)
            {
                _selectedGame = game;
                PanelPlaceholder.Visibility = Visibility.Collapsed;
                GridDetails.Visibility = Visibility.Visible;

                // Bind Details Header
                string formattedSource = game.Source.Equals("horde", StringComparison.OrdinalIgnoreCase) ? "Horde" : "Live";
                TxtDetailTitle.Text = game.DeckName;
                TxtDetailSubtitle.Text = $"{formattedSource} Match — {game.Date}";

                // Bind Core Stats
                TxtDetailMulligans.Text = game.MulliganCount?.ToString() ?? "0";
                TxtDetailLands.Text = game.LandsDrawnOpening?.ToString() ?? "N/A";

                // Bind Secondary Stats
                TxtDetailCmdCast.Text = game.CommanderCastTurn?.ToString() ?? "N/A";
                TxtDetailCmdRecasts.Text = game.CommanderRecastCount?.ToString() ?? "0";
                TxtDetailWipes.Text = $"{game.MyWipeCount ?? 0} / {game.OpponentWipeCount ?? 0}";
                TxtDetailSalt.Text = $"{game.SaltPrior} / {game.SaltObserved}";

                // Recovered from wipe visibility
                if (game.OpponentWipeCount > 0)
                {
                    GridDetailWipeRecover.Visibility = Visibility.Visible;
                    TxtDetailWipeRecover.Text = game.RecoveredFromWipe == 1 ? "Yes" : "No";
                }
                else
                {
                    GridDetailWipeRecover.Visibility = Visibility.Collapsed;
                }

                // Bind Horde Specific Panel
                if (game.Source.Equals("horde", StringComparison.OrdinalIgnoreCase))
                {
                    PanelHordeDetails.Visibility = Visibility.Visible;
                    TxtDetailHordeDeck.Text = game.HordeDeckName ?? "Unknown Deck";
                    TxtDetailPlayersLife.Text = $"{game.HordePlayers} Players / {game.SurvivorLife} Life";
                    TxtDetailSetup.Text = $"{game.DeckSizePct}% Size / {game.DrawsPerTurn} Draw / {game.TokenMultiplier}x";
                    TxtDetailMilestone.Text = $"{game.MilestonePct}%";

                    // Bind Co-op partner names
                    if (!string.IsNullOrEmpty(game.CoOpCommanders))
                    {
                        PanelDetailCoOp.Visibility = Visibility.Visible;
                        TxtDetailCoOp.Text = game.CoOpCommanders;
                    }
                    else
                    {
                        PanelDetailCoOp.Visibility = Visibility.Collapsed;
                    }
                }
                else
                {
                    PanelHordeDetails.Visibility = Visibility.Collapsed;
                }

                // Notes Bind
                if (!string.IsNullOrWhiteSpace(game.Notes))
                {
                    TxtDetailNotes.Text = game.Notes;
                    TxtDetailNotes.Foreground = (System.Windows.Media.Brush)Application.Current.FindResource("TextFillColorPrimaryBrush");
                }
                else
                {
                    TxtDetailNotes.Text = "No notes recorded.";
                    TxtDetailNotes.Foreground = (System.Windows.Media.Brush)Application.Current.FindResource("TextFillColorSecondaryBrush");
                }
            }
            else
            {
                _selectedGame = null;
                PanelPlaceholder.Visibility = Visibility.Visible;
                GridDetails.Visibility = Visibility.Collapsed;
            }
        }

        private void OnDeleteGameClick(object sender, RoutedEventArgs e)
        {
            if (_selectedGame == null) return;

            var result = MessageBox.Show(
                $"Are you sure you want to delete this game record?\nDeck: {_selectedGame.DeckName}\nDate: {_selectedGame.Date}",
                "Confirm Delete Record",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning
            );

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    DbService.DeleteGame(_selectedGame.GameId);
                    ShowInfo("Game record deleted successfully.", Wpf.Ui.Controls.InfoBarSeverity.Success);
                    
                    DgGames.SelectedItem = null;
                    LoadGames();
                }
                catch (Exception ex)
                {
                    ShowInfo($"Error deleting game: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
                }
            }
        }

        private void ShowInfo(string message, Wpf.Ui.Controls.InfoBarSeverity severity)
        {
            InfoBarHistory.Message = message;
            InfoBarHistory.Severity = severity;
            InfoBarHistory.IsOpen = true;
        }
    }
}
