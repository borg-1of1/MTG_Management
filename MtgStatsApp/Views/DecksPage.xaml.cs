using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using MtgStatsApp.Services;

namespace MtgStatsApp.Views
{
    public partial class DecksPage : Page
    {
        private Deck? _selectedDeck = null;

        public DecksPage()
        {
            InitializeComponent();
            LoadDecks();
        }

        private void LoadDecks()
        {
            try
            {
                var decks = DbService.GetDecks().ToList();
                LstDecks.ItemsSource = decks;
            }
            catch (Exception ex)
            {
                ShowInfo($"Error loading decks: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void OnDeckSelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (LstDecks.SelectedItem is Deck deck)
            {
                _selectedDeck = deck;
                TxtFormHeader.Text = $"Edit Deck: {deck.DeckName}";
                TxtDeckName.Text = deck.DeckName;
                TxtMoxfieldUrl.Text = deck.MoxfieldUrl;
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
            LstDecks.SelectedItem = null;
            ClearForm();
        }

        private void ClearForm()
        {
            _selectedDeck = null;
            TxtFormHeader.Text = "Create New Deck";
            TxtDeckName.Text = string.Empty;
            TxtMoxfieldUrl.Text = string.Empty;
            TxtNotes.Text = string.Empty;
            BtnDelete.Visibility = Visibility.Collapsed;
            InfoBarDeck.IsOpen = false;
        }

        private void OnSaveClick(object sender, RoutedEventArgs e)
        {
            string name = TxtDeckName.Text.Trim();
            string url = TxtMoxfieldUrl.Text.Trim();
            string notes = TxtNotes.Text.Trim();

            if (string.IsNullOrEmpty(name))
            {
                ShowInfo("Deck name is required.", Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            // Enforce Real Name Only constraint
            if (name.Contains("[") || name.Contains("]"))
            {
                ShowInfo("Do not include status tags (like [S2] or [Active]) in the database. Use real name only.", Wpf.Ui.Controls.InfoBarSeverity.Error);
                return;
            }

            try
            {
                var deck = _selectedDeck ?? new Deck();
                deck.DeckName = name;
                deck.MoxfieldUrl = string.IsNullOrEmpty(url) ? null : url;
                deck.Notes = string.IsNullOrEmpty(notes) ? null : notes;

                DbService.SaveDeck(deck);
                ShowInfo("Deck saved successfully!", Wpf.Ui.Controls.InfoBarSeverity.Success);
                
                ClearForm();
                LoadDecks();
            }
            catch (Exception ex)
            {
                ShowInfo($"Error saving deck: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void OnDeleteClick(object sender, RoutedEventArgs e)
        {
            if (_selectedDeck == null) return;

            var result = MessageBox.Show(
                $"Are you sure you want to delete '{_selectedDeck.DeckName}'?\nThis will also cascade-delete all logged games for this deck!",
                "Confirm Delete",
                MessageBoxButton.YesNo,
                MessageBoxImage.Warning
            );

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    DbService.DeleteDeck(_selectedDeck.DeckId);
                    ShowInfo("Deck deleted successfully.", Wpf.Ui.Controls.InfoBarSeverity.Success);
                    
                    ClearForm();
                    LoadDecks();
                }
                catch (Exception ex)
                {
                    ShowInfo($"Error deleting deck: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
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
