import unittest
from pathlib import Path

from wallpaper_app.config.settings import load_settings


class SettingsTest(unittest.TestCase):
    def test_uses_xdg_directories(self) -> None:
        settings = load_settings(
            {
                "XDG_CONFIG_HOME": "/tmp/test-config",
                "XDG_DATA_HOME": "/tmp/test-data",
                "WALLHAVEN_QUERY": "mountains",
            }
        )

        self.assertEqual(settings.config_dir, Path("/tmp/test-config/wallpaper-app"))
        self.assertEqual(settings.data_dir, Path("/tmp/test-data/wallpaper-app"))
        self.assertEqual(settings.images_dir, Path("/tmp/test-data/wallpaper-app/images"))
        self.assertEqual(
            settings.database_path,
            Path("/tmp/test-data/wallpaper-app/wallpaper.db"),
        )
        self.assertEqual(settings.wallhaven_query, "mountains")

    def test_wallhaven_query_defaults_to_nature(self) -> None:
        settings = load_settings({})

        self.assertEqual(settings.wallhaven_query, "nature")


if __name__ == "__main__":
    unittest.main()
