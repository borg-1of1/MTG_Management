using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using MtgStatsApp.Services;

namespace MtgStatsApp.Views
{
    public partial class LogGamePage : Page
    {
        private List<Deck> _decks = new();
        private List<HordeDeck> _hordeDecks = new();

        public LogGamePage()
        {
            InitializeComponent();
            
            // Set date to today
            DpDate.SelectedDate = DateTime.Today;

            // Load selectors
            LoadDecksAndHordeDecks();

            // Load sticky defaults
            LoadStickyDefaults();

            // Setup wipe recovery check state
            UpdateWipeRecoveryState();

            // Hook Ctrl+S preview key handler
            PreviewKeyDown += Page_KeyDown;
        }

        private void LoadDecksAndHordeDecks()
        {
            try
            {
                _decks = DbService.GetDecks().ToList();
                CbDecks.ItemsSource = _decks;

                _hordeDecks = DbService.GetHordeDecks().ToList();
                CbHordeDecks.ItemsSource = _hordeDecks;
            }
            catch (Exception ex)
            {
                ShowInfo($"Error loading reference decks: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void LoadStickyDefaults()
        {
            var settings = SettingsService.Load();

            // Set sliders & inputs from settings
            SlHordePlayers.Value = Math.Clamp(settings.LastHordePlayers, 1, 4);
            TxtSurvivorLife.Text = settings.LastSurvivorLife.ToString();

            // Set ComboBox values by matching Tags
            SelectComboItemByTag(CbDeckSizePct, settings.LastDeckSizePct.ToString());
            SelectComboItemByTag(CbTokenMultiplier, settings.LastTokenMultiplier.ToString());
            SelectComboItemByTag(CbMilestonePct, settings.LastMilestonePct.ToString());

            // Set draws per turn combo (matches content string)
            SelectComboItemByContent(CbDrawsPerTurn, settings.LastDrawsPerTurn.ToString());

            // Set horde deck selector
            if (settings.LastHordeDeckId > 0 && _hordeDecks.Any(d => d.HordeDeckId == settings.LastHordeDeckId))
            {
                CbHordeDecks.SelectedValue = settings.LastHordeDeckId;
            }
        }

        private void SaveStickyDefaults()
        {
            var settings = SettingsService.Load();
            
            settings.LastHordePlayers = (int)SlHordePlayers.Value;
            if (int.TryParse(TxtSurvivorLife.Text, out int life))
            {
                settings.LastSurvivorLife = life;
            }

            if (CbDeckSizePct.SelectedItem is ComboBoxItem deckSizeItem && int.TryParse(deckSizeItem.Tag?.ToString(), out int size))
            {
                settings.LastDeckSizePct = size;
            }

            if (CbTokenMultiplier.SelectedItem is ComboBoxItem tokenItem && int.TryParse(tokenItem.Tag?.ToString(), out int mult))
            {
                settings.LastTokenMultiplier = mult;
            }

            if (CbMilestonePct.SelectedItem is ComboBoxItem milestoneItem && int.TryParse(milestoneItem.Tag?.ToString(), out int milestone))
            {
                settings.LastMilestonePct = milestone;
            }

            if (CbDrawsPerTurn.SelectedItem is ComboBoxItem drawsItem && int.TryParse(drawsItem.Content?.ToString(), out int draws))
            {
                settings.LastDrawsPerTurn = draws;
            }

            if (CbHordeDecks.SelectedValue is int hordeDeckId)
            {
                settings.LastHordeDeckId = hordeDeckId;
            }

            SettingsService.Save(settings);
        }

        private void SelectComboItemByTag(ComboBox cb, string tagValue)
        {
            foreach (ComboBoxItem item in cb.Items)
            {
                if (item.Tag?.ToString() == tagValue)
                {
                    cb.SelectedItem = item;
                    break;
                }
            }
        }

        private void SelectComboItemByContent(ComboBox cb, string contentValue)
        {
            foreach (ComboBoxItem item in cb.Items)
            {
                if (item.Content?.ToString() == contentValue)
                {
                    cb.SelectedItem = item;
                    break;
                }
            }
        }

        private void OnGameTypeChanged(object sender, RoutedEventArgs e)
        {
            if (SwGameType == null || CardLiveConfig == null || CardHordeConfig == null) return;

            bool isHorde = SwGameType.IsChecked == true;
            CardLiveConfig.Visibility = isHorde ? Visibility.Collapsed : Visibility.Visible;
            CardHordeConfig.Visibility = isHorde ? Visibility.Visible : Visibility.Collapsed;
        }

        private void OnSaltPriorChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (TxtSaltPriorVal != null) TxtSaltPriorVal.Text = ((int)e.NewValue).ToString();
        }

        private void OnSaltObservedChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (TxtSaltObservedVal != null) TxtSaltObservedVal.Text = ((int)e.NewValue).ToString();
        }

        private void OnHordePlayersChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (TxtHordePlayersVal != null) TxtHordePlayersVal.Text = ((int)e.NewValue).ToString();
            
            // Adjust survivor life recommendation if not customized (typically 20 life per player)
            if (TxtSurvivorLife != null && string.IsNullOrEmpty(TxtSurvivorLife.Text.Trim()) || TxtSurvivorLife.Text == "20" || TxtSurvivorLife.Text == "40" || TxtSurvivorLife.Text == "60" || TxtSurvivorLife.Text == "80")
            {
                TxtSurvivorLife.Text = ((int)e.NewValue * 20).ToString();
            }
        }

        private void OnOpponentWipesChanged(object sender, TextChangedEventArgs e)
        {
            UpdateWipeRecoveryState();
        }

        private void UpdateWipeRecoveryState()
        {
            if (ChkRecoveredFromWipe == null || TxtOpponentWipeCount == null) return;

            if (int.TryParse(TxtOpponentWipeCount.Text.Trim(), out int wipes) && wipes > 0)
            {
                ChkRecoveredFromWipe.IsEnabled = true;
            }
            else
            {
                ChkRecoveredFromWipe.IsChecked = false;
                ChkRecoveredFromWipe.IsEnabled = false;
            }
        }

        private void NumberValidation(object sender, TextCompositionEventArgs e)
        {
            // Allow only numbers
            e.Handled = !e.Text.All(char.IsDigit);
        }

        private void OnFormInputChanged(object sender, SelectionChangedEventArgs e)
        {
            InfoBarLog.IsOpen = false;
        }

        private void Page_KeyDown(object sender, KeyEventArgs e)
        {
            // Ctrl+S trigger
            if (e.Key == Key.S && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
            {
                e.Handled = true;
                BtnSaveGame.Focus(); // Shift focus to validate inputs
                SaveGame();
            }
        }

        private void OnSaveGameClick(object sender, RoutedEventArgs e)
        {
            SaveGame();
        }

        private void SaveGame()
        {
            // 1. Core validations
            if (DpDate.SelectedDate == null)
            {
                ShowInfo("Please select a game date.", Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            if (CbDecks.SelectedValue == null)
            {
                ShowInfo("Please select your deck.", Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            bool isHorde = SwGameType.IsChecked == true;

            if (isHorde && CbHordeDecks.SelectedValue == null)
            {
                ShowInfo("Please select a Horde Adversary deck.", Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            try
            {
                // 2. Build Game Header
                var game = new Game
                {
                    Date = DpDate.SelectedDate.Value.ToString("yyyy-MM-dd"),
                    DeckId = (int)CbDecks.SelectedValue,
                    Source = isHorde ? "horde" : "live",
                    LandsDrawnOpening = ParseNullableInt((CbLandsDrawn.SelectedItem as ComboBoxItem)?.Content?.ToString()),
                    MulliganCount = ParseNullableInt((CbMulligans.SelectedItem as ComboBoxItem)?.Content?.ToString()),
                    CommanderCastTurn = ParseNullableInt(TxtCommanderCastTurn.Text),
                    SaltPrior = (int)SlSaltPrior.Value,
                    SaltObserved = (int)SlSaltObserved.Value,
                    CommanderRecastCount = ParseNullableInt(TxtCommanderRecastCount.Text) ?? 0,
                    MyWipeCount = ParseNullableInt(TxtMyWipeCount.Text) ?? 0,
                    OpponentWipeCount = ParseNullableInt(TxtOpponentWipeCount.Text) ?? 0,
                    TurnCount = ParseNullableInt(TxtTurnCount.Text),
                    Notes = string.IsNullOrEmpty(TxtNotes.Text.Trim()) ? null : TxtNotes.Text.Trim()
                };

                // recovered_from_wipe: 1 (true) / 0 (false) / null (when opponent wipe count is 0)
                if (game.OpponentWipeCount > 0)
                {
                    game.RecoveredFromWipe = ChkRecoveredFromWipe.IsChecked == true ? 1 : 0;
                }
                else
                {
                    game.RecoveredFromWipe = null;
                }

                HordeGame? hordeGame = null;
                List<string> coOpCommanders = new();

                if (isHorde)
                {
                    // 3. Build Horde Child data
                    hordeGame = new HordeGame
                    {
                        HordeDeckId = (int)CbHordeDecks.SelectedValue,
                        HordePlayers = (int)SlHordePlayers.Value,
                        SurvivorLife = ParseNullableInt(TxtSurvivorLife.Text) ?? (int)SlHordePlayers.Value * 20,
                        DrawsPerTurn = ParseNullableInt((CbDrawsPerTurn.SelectedItem as ComboBoxItem)?.Content?.ToString()) ?? 1,
                        TokenMultiplier = int.Parse((CbTokenMultiplier.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? "1"),
                        DeckSizePct = int.Parse((CbDeckSizePct.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? "100"),
                        MilestonePct = int.Parse((CbMilestonePct.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? "0"),
                        Result = (CbHordeResult.SelectedItem as ComboBoxItem)?.Tag?.ToString() ?? "win"
                    };

                    // Process Co-op Commanders
                    string coOpInput = TxtCoOpCommanders.Text.Trim();
                    if (!string.IsNullOrEmpty(coOpInput))
                    {
                        coOpCommanders = coOpInput.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries)
                                                  .Select(s => s.Trim())
                                                  .Where(s => !string.IsNullOrEmpty(s))
                                                  .ToList();
                    }

                    // Save Horde sticky defaults
                    SaveStickyDefaults();
                }

                // 4. Save to Database in transaction
                DbService.LogGame(game, hordeGame, coOpCommanders);

                // 5. Show Success
                ShowInfo($"Game logged successfully on {game.Date}!", Wpf.Ui.Controls.InfoBarSeverity.Success);

                // 6. Reset Form (retaining date & sticky defaults)
                ResetFormExceptSticky();
            }
            catch (Exception ex)
            {
                ShowInfo($"Failed to log game: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void ResetFormExceptSticky()
        {
            // Reset core textboxes
            TxtCommanderCastTurn.Text = string.Empty;
            TxtCommanderRecastCount.Text = string.Empty;
            TxtTurnCount.Text = string.Empty;
            TxtMyWipeCount.Text = string.Empty;
            TxtOpponentWipeCount.Text = string.Empty;
            TxtNotes.Text = string.Empty;

            // Reset mulligan/lands combos
            CbMulligans.SelectedIndex = 0;
            CbLandsDrawn.SelectedIndex = 3;

            // Reset sliders
            SlSaltPrior.Value = 3;
            SlSaltObserved.Value = 3;

            // Reset wipe checkbox
            ChkRecoveredFromWipe.IsChecked = false;
            ChkRecoveredFromWipe.IsEnabled = false;

            // Horde specific co-op commanders reset
            TxtCoOpCommanders.Text = string.Empty;

            // Refresh datasets (in case new decks were added since opening)
            LoadDecksAndHordeDecks();
            LoadStickyDefaults();
        }

        private int? ParseNullableInt(string? text)
        {
            if (string.IsNullOrEmpty(text?.Trim())) return null;
            return int.TryParse(text, out int val) ? val : null;
        }

        private void ShowInfo(string message, Wpf.Ui.Controls.InfoBarSeverity severity)
        {
            InfoBarLog.Message = message;
            InfoBarLog.Severity = severity;
            InfoBarLog.IsOpen = true;
        }
    }
}
