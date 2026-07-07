using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using MtgStatsApp.Services;

namespace MtgStatsApp.Views
{
    public partial class DbSettingsPage : Page
    {
        private string _selectedPath = string.Empty;

        public DbSettingsPage()
        {
            InitializeComponent();
            LoadCurrentSettings();
        }

        private void LoadCurrentSettings()
        {
            var settings = SettingsService.Load();
            if (!string.IsNullOrEmpty(settings.DatabasePath))
            {
                TxtDbPath.Text = settings.DatabasePath;
                _selectedPath = settings.DatabasePath;
                TestConnection(silent: true);
            }
        }

        private void OnBrowseClick(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Filter = "SQLite Database Files (*.db;*.sqlite)|*.db;*.sqlite|All Files (*.*)|*.*",
                Title = "Select MTG Stats Database File"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                _selectedPath = openFileDialog.FileName;
                TxtDbPath.Text = _selectedPath;
                TestConnection(silent: false);
            }
        }

        private void OnCreateNewClick(object sender, RoutedEventArgs e)
        {
            var saveFileDialog = new SaveFileDialog
            {
                Filter = "SQLite Database Files (*.db)|*.db",
                Title = "Create New MTG Stats Database File",
                FileName = "mtg_stats.db"
            };

            if (saveFileDialog.ShowDialog() == true)
            {
                _selectedPath = saveFileDialog.FileName;
                TxtDbPath.Text = _selectedPath;
                
                try
                {
                    // Initialize creates the tables if the file is new/empty
                    DbService.Initialize(_selectedPath);
                    ShowInfo("Database created successfully!", Wpf.Ui.Controls.InfoBarSeverity.Success);
                }
                catch (Exception ex)
                {
                    ShowInfo($"Failed to create database: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
                }
            }
        }

        private bool TestConnection(bool silent)
        {
            if (string.IsNullOrEmpty(_selectedPath))
            {
                if (!silent) ShowInfo("Please select or create a database file first.", Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return false;
            }

            try
            {
                DbService.Initialize(_selectedPath);
                if (!silent) ShowInfo("Connected to database successfully!", Wpf.Ui.Controls.InfoBarSeverity.Success);
                return true;
            }
            catch (Exception ex)
            {
                if (!silent) ShowInfo($"Database error: {ex.Message}", Wpf.Ui.Controls.InfoBarSeverity.Error);
                return false;
            }
        }

        private void OnConnectClick(object sender, RoutedEventArgs e)
        {
            if (TestConnection(silent: false))
            {
                // Save database path to settings
                var settings = SettingsService.Load();
                settings.DatabasePath = _selectedPath;
                SettingsService.Save(settings);

                // Transition MainWindow to Dashboard
                var mainWindow = Application.Current.MainWindow as MainWindow;
                if (mainWindow != null)
                {
                    mainWindow.OnDatabaseConnected();
                }
            }
        }

        private void ShowInfo(string message, Wpf.Ui.Controls.InfoBarSeverity severity)
        {
            InfoBarConnection.Message = message;
            InfoBarConnection.Severity = severity;
            InfoBarConnection.IsOpen = true;
        }
    }
}
