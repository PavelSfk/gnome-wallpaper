import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from wallpaper_app.db.database import Database
from wallpaper_app.db.models import ImageRecord
from wallpaper_app.history.manager import HistoryManager


class HistoryManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.database = Database(self.root / "wallpaper.db")
        self.wallpaper_manager = Mock()
        self.history = HistoryManager(self.database, self.wallpaper_manager)
        self.images = [
            ImageRecord(
                provider="test",
                remote_id=f"photo-{index}",
                source_url=f"https://example.test/{index}",
                local_path=str(self.root / f"{index}.jpg"),
            )
            for index in range(3)
        ]
        self.ids = [self.database.insert_image(image) for image in self.images]

    def tearDown(self) -> None:
        self.database.close()
        self.temp_dir.cleanup()

    def test_next_previous_and_empty_selection(self) -> None:
        self.assertEqual(self.history.get_next().id, self.ids[0])
        self.assertEqual(self.history.get_next(self.ids[0]).id, self.ids[1])
        self.assertEqual(self.history.get_next(self.ids[2]).id, self.ids[0])
        self.assertEqual(self.history.get_previous().id, self.ids[2])
        self.assertEqual(self.history.get_previous(self.ids[0]).id, self.ids[2])
        self.assertIsNotNone(self.history.get_random())

    def test_set_wallpaper_records_usage_after_success(self) -> None:
        image = self.database.get_by_id(self.ids[0])
        used = self.history.set_wallpaper(image)

        self.wallpaper_manager.set_wallpaper.assert_called_once_with(image.local_path)
        self.assertEqual(used.use_count, 1)
        self.assertEqual(self.history.get_unused(), [
            self.database.get_by_id(self.ids[1]),
            self.database.get_by_id(self.ids[2]),
        ])
        self.assertEqual(self.history.get_history()[0].id, self.ids[0])

    def test_failed_wallpaper_does_not_record_usage(self) -> None:
        self.wallpaper_manager.set_wallpaper.side_effect = RuntimeError("gsettings failed")
        image = self.database.get_by_id(self.ids[0])

        with self.assertRaises(RuntimeError):
            self.history.set_wallpaper(image)

        self.assertEqual(self.database.get_by_id(self.ids[0]).use_count, 0)

    def test_menu_candidates_are_limited_and_current_is_latest_used(self) -> None:
        self.assertEqual([image.id for image in self.history.get_menu_candidates(2)], self.ids[2::-1][:2])
        self.assertIsNone(self.history.get_current())
        self.history.set_wallpaper(self.database.get_by_id(self.ids[1]))
        self.assertEqual(self.history.get_current().id, self.ids[1])


if __name__ == "__main__":
    unittest.main()
