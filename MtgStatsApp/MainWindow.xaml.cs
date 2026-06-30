using System;
using System.IO;
using System.Windows;
using Wpf.Ui.Controls;
using MtgStatsApp.Services;
using MtgStatsApp.Views;

namespace MtgStatsApp
{
    public partial class MainWindow : FluentWindow
    {
        public MainWindow()
        {
            InitializeComponent();
            
            // Link the navigation view to the content frame for automatic page rendering
            RootNavigation.Frame = ContentFrame;

            // Initialize app theme state
            Wpf.Ui.Appearance.SystemThemeWatcher.Watch(this);

            CheckDatabaseConnection();
        }

        private void CheckDatabaseConnection()
        {
            var settings = SettingsService.Load();
            if (string.IsNullOrEmpty(settings.DatabasePath) || !File.Exists(settings.DatabasePath))
            {
                // Lock navigation until database is connected
                LockNavigation(true);
                RootNavigation.Navigate(typeof(DbSettingsPage));
            }
            else
            {
                try
                {
                    DbService.Initialize(settings.DatabasePath);
                    LockNavigation(false);
                    RootNavigation.Navigate(typeof(DashboardPage));
                }
                catch (Exception)
                {
                    LockNavigation(true);
                    RootNavigation.Navigate(typeof(DbSettingsPage));
                }
            }
        }

        public void OnDatabaseConnected()
        {
            LockNavigation(false);
            RootNavigation.Navigate(typeof(DashboardPage));
        }

        private void LockNavigation(bool isLocked)
        {
            // Enable or disable main menu items based on lock state
            foreach (var item in RootNavigation.MenuItems)
            {
                if (item is NavigationViewItem navItem)
                {
                    navItem.IsEnabled = !isLocked;
                }
            }
        }
    }
}