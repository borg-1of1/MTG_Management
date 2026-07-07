using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using MtgStatsApp.Services;

namespace MtgStatsApp.Views
{
    public partial class HordeDecksPage : Page
    {
        private HordeDeck? _selectedDeck = null;

        public HordeDecksPage()
        {
            InitializeComponent();
            LoadHordeDecks();
        }

        private void LoadHordeDecks()
        {
            try
            {
                var decks = DbService.GetHordeDecks().ToList();
                LstHordeDecks.ItemsSource = decks;
            }
            catch (Exception ex)
            {
                ShowInfo($"Error loading Horde decks: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void OnHordeDeckSelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (LstHordeDecks.SelectedItem is HordeDeck deck)
            {
                _selectedDeck = deck;
                TxtFormHeader.Text = $"Edit Horde Deck: {deck.DeckName}";
                TxtDeckName.Text = deck.DeckName;
                ChkIsOfficial.IsChecked = deck.IsOfficial == 1;
                TxtSourceUrl.Text = deck.SourceUrl;
                TxtNotes.Text = deck.Notes;
                BtnDelete.Visibility = Visibility.Visible;
            }
            else
            {
                ClearForm();
            }
        }

        private void OnClearClick(object sender, RoutedEventArgs e)
        {
            LstHordeDecks.SelectedItem = null;
            ClearForm();
        }

        private void ClearForm()
        {
            _selectedDeck = null;
            TxtFormHeader.Text = "Create New Horde Deck";
            TxtDeckName.Text = string.Empty;
            ChkIsOfficial.IsChecked = false;
            TxtSourceUrl.Text = string.Empty;
            TxtNotes.Text = string.Empty;
            BtnDelete.Visibility = Visibility.Collapsed;
            InfoBarDeck.IsOpen = false;
        }

        private void OnSaveClick(object sender, RoutedEventArgs e)
        {
            string name = TxtDeckName.Text.Trim();
            string url = TxtSourceUrl.Text.Trim();
            string notes = TxtNotes.Text.Trim();
            bool isOfficial = ChkIsOfficial.IsChecked == true;

            if (string.IsNullOrEmpty(name))
            {
                ShowInfo("Deck name is required.", Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            try
            {
                var deck = _selectedDeck ?? new HordeDeck();
                deck.DeckName = name;
                deck.IsOfficial = isOfficial ? 1 : 0;
                deck.SourceUrl = string.IsNullOrEmpty(url) ? null : url;
                deck.Notes = string.IsNullOrEmpty(notes) ? null : notes;

                DbService.SaveHordeDeck(deck);
                ShowInfo("Horde deck saved successfully!", Wpf.Ui.Controls.InfoBarSeverity.Success);
                
                ClearForm();
                LoadHordeDecks();
            }
            catch (Exception ex)
            {
                ShowInfo($"Error saving Horde deck: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void OnDeleteClick(object sender, RoutedEventArgs e)
        {
            if (_selectedDeck == null) return;

            var result = MessageBox.Show(
                $"Are you sure you want to delete '{_selectedDeck.DeckName}'?\nThis will cascade-delete all logged games against this Horde deck!",
                "Confirm Delete",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning
            );

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    DbService.DeleteHordeDeck(_selectedDeck.HordeDeckId);
                    ShowInfo("Horde deck deleted successfully.", Wpf.Ui.Controls.InfoBarSeverity.Success);
                    
                    ClearForm();
                    LoadHordeDecks();
                }
                catch (Exception ex)
                {
                    ShowInfo($"Error deleting Horde deck: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
                }
            }
        }

        private void ShowInfo(string message, Wpf.Ui.Controls.InfoBarSeverity severity)
        {
            InfoBarDeck.Message = message;
            InfoBarDeck.Severity = severity;
            InfoBarDeck.IsOpen = true;
        }
    }
}
