import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from wallpaper_app.wallpaper.manager import WallpaperManager


class WallpaperManagerTest(unittest.TestCase):
    def test_sets_light_and_dark_wallpapers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "wallpaper image.jpg"
            image_path.write_bytes(b"image")

            with patch("wallpaper_app.wallpaper.manager.subprocess.run") as run:
                WallpaperManager().set_wallpaper(image_path)

            uri = image_path.resolve().as_uri()
            self.assertEqual(run.call_count, 2)
            run.assert_any_call(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.background",
                    "picture-uri",
                    uri,
                ],
                check=True,
            )
            run.assert_any_call(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.background",
                    "picture-uri-dark",
                    uri,
                ],
                check=True,
            )

    def test_missing_file_is_rejected(self) -> None:
        with self.assertRaises(FileNotFoundError):
            WallpaperManager().set_wallpaper("/tmp/does-not-exist-wallpaper.jpg")


if __name__ == "__main__":
    unittest.main()
