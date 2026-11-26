import unittest

import wallpaper_app
from wallpaper_app.main import main


class SmokeTest(unittest.TestCase):
    def test_package_imports(self) -> None:
        self.assertEqual(wallpaper_app.__version__, "0.1.0")

    def test_main_returns_success(self) -> None:
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
