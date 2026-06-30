using System;
using System.IO;
using System.Text.Json;

namespace MtgStatsApp.Services
{
    public class AppSettings
    {
        public string DatabasePath { get; set; } = string.Empty;
        
        // Storing the last used settings for horde game logs for the "under 10 seconds" quick-logging requirement
        public int LastHordePlayers { get; set; } = 1;
        public int LastSurvivorLife { get; set; } = 20;
        public int LastDeckSizePct { get; set; } = 100;
        public int LastDrawsPerTurn { get; set; } = 1;
        public int LastTokenMultiplier { get; set; } = 1;
        public int LastMilestonePct { get; set; } = 0;
        public int LastHordeDeckId { get; set; } = 0;
    }

    public static class SettingsService
    {
        private static readonly string SettingsFolder = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "MtgStatsApp"
        );
        
        private static readonly string SettingsFile = Path.Combine(SettingsFolder, "settings.json");

        public static AppSettings Load()
        {
            try
            {
                if (!Directory.Exists(SettingsFolder))
                {
                    Directory.CreateDirectory(SettingsFolder);
                }

                if (File.Exists(SettingsFile))
                {
                    string json = File.ReadAllText(SettingsFile);
                    return JsonSerializer.Deserialize<AppSettings>(json) ?? new AppSettings();
                }
            }
            catch { }

            return new AppSettings();
        }

        public static void Save(AppSettings settings)
        {
            try
            {
                if (!Directory.Exists(SettingsFolder))
                {
                    Directory.CreateDirectory(SettingsFolder);
                }

                string json = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(SettingsFile, json);
            }
            catch { }
        }
    }
}
