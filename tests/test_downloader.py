import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from wallpaper_app.db.database import Database
from wallpaper_app.download.downloader import Downloader
from wallpaper_app.providers.base import ImageMetadata


class DownloaderTest(unittest.TestCase):
    def test_downloads_file_and_skips_duplicate(self) -> None:
        response = Mock()
        response.iter_content.return_value = [b"image", b"-bytes"]
        session = Mock()
        session.get.return_value = response

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = Database(root / "wallpaper.db")
            downloader = Downloader(database, root / "images", session=session)
            metadata = ImageMetadata(
                provider="wallhaven",
                remote_id="photo/unsafe-name",
                source_url="https://wallhaven.cc/w/photo",
                download_url="https://images.example/photo.jpg?raw=1",
                author_name="Test Author",
            )

            first = downloader.download(metadata)
            second = downloader.download(metadata)

            self.assertEqual(first.id, second.id)
            self.assertEqual(Path(first.local_path).read_bytes(), b"image-bytes")
            self.assertEqual(len(database.get_local_images()), 1)
            session.get.assert_called_once_with(
                metadata.download_url, stream=True, timeout=10
            )
            self.assertNotIn("unsafe-name", Path(first.local_path).name)
            database.close()

    def test_failed_download_removes_partial_file(self) -> None:
        response = Mock()
        response.raise_for_status.side_effect = RuntimeError("bad response")
        session = Mock()
        session.get.return_value = response

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = Database(root / "wallpaper.db")
            downloader = Downloader(database, root / "images", session=session)
            metadata = ImageMetadata(
                provider="wallhaven",
                remote_id="photo-1",
                source_url="https://wallhaven.cc/w/photo-1",
                download_url="https://images.example/photo-1.jpg",
            )

            with self.assertRaises(RuntimeError):
                downloader.download(metadata)

            self.assertEqual(list((root / "images").glob("*")), [])
            database.close()


if __name__ == "__main__":
    unittest.main()
