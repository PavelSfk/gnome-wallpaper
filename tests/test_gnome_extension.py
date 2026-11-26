import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1] / "gnome-extension" / "wallpaper-app@pavel"


class GnomeExtensionTest(unittest.TestCase):
    def test_metadata_targets_gnome_46(self) -> None:
        metadata = json.loads((ROOT / "metadata.json").read_text())

        self.assertEqual(metadata["uuid"], "wallpaper-app@pavel")
        self.assertIn("46", metadata["shell-version"])

    def test_extension_uses_menu_and_select_cli_contract(self) -> None:
        extension = (ROOT / "extension.js").read_text()

        self.assertIn("_runCli(['menu']", extension)
        self.assertIn("_runCli(['select', String(candidate.id)]", extension)
        self.assertIn("'-m', 'wallpaper_app.main'", extension)
        self.assertIn("launcher.setenv('XDG_DATA_HOME', USER_DATA_HOME, true)", extension)
        self.assertIn("wallpaper-current", extension)
        self.assertIn("icon_size: 96", extension)
        self.assertIn("this._indicator.reactive = true", extension)
        self.assertIn("this._indicator.can_focus = true", extension)
        self.assertIn("button-release-event", extension)
        self.assertIn("this._indicator.menu.open()", extension)
        self.assertIn("this.dir.get_child('stylesheet.css')", extension)
        self.assertNotIn("this.get_stylesheet()", extension)


if __name__ == "__main__":
    unittest.main()