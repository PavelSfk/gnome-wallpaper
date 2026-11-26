import tempfile
import unittest
from pathlib import Path

from wallpaper_app.db.database import Database
from wallpaper_app.db.models import ImageRecord


class DatabaseTest(unittest.TestCase):
    def test_insert_lookup_local_images_and_usage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "wallpaper.db")
            image = ImageRecord(
                provider="unsplash",
                remote_id="photo-1",
                source_url="https://example.test/photo-1.jpg",
                author_url="https://example.test/author",
                author_name="Test Author",
                description="A test image",
                width=1920,
                height=1080,
                file_type="image/jpeg",
                category="general",
                purity="sfw",
                local_path="images/1.jpg",
            )

            image_id = database.insert_image(image)
            duplicate_id = database.insert_image(image)
            stored = database.get_by_provider_remote_id("unsplash", "photo-1")

            self.assertEqual(image_id, duplicate_id)
            self.assertIsNotNone(stored)
            self.assertEqual(stored.local_path, "images/1.jpg")
            self.assertEqual(stored.width, 1920)
            self.assertEqual(database.get_local_images(), [stored])

            database.update_usage(image_id, "2026-08-20T10:00:00+00:00")
            database.update_usage(image_id, "2026-08-20T11:00:00+00:00")
            used = database.get_by_provider_remote_id("unsplash", "photo-1")

            self.assertEqual(used.first_used_at, "2026-08-20T10:00:00+00:00")
            self.assertEqual(used.last_used_at, "2026-08-20T11:00:00+00:00")
            self.assertEqual(used.use_count, 2)
            database.close()

    def test_images_without_local_path_are_not_local(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "wallpaper.db")
            database.insert_image(
                ImageRecord(
                    provider="unsplash",
                    remote_id="photo-2",
                    source_url="https://example.test/photo-2.jpg",
                )
            )

            self.assertEqual(database.get_local_images(), [])
            database.close()


if __name__ == "__main__":
    unittest.main()
