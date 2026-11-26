import io
import json
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from unittest.mock import Mock

from wallpaper_app.db.models import ImageRecord
from wallpaper_app.main import Services, build_parser, main
from wallpaper_app.providers.base import ImageMetadata


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.image = ImageRecord(
            id=1,
            provider="test",
            remote_id="photo-1",
            source_url="https://example.test/photo-1",
            local_path="/tmp/photo-1.jpg",
            use_count=1,
        )
        self.provider = Mock()
        self.downloader = Mock()
        self.history = Mock()
        self.database = Mock()
        self.database.get_existing_ids.return_value = set()
        self.candidate = ImageMetadata(
            provider="wallhaven",
            remote_id="candidate-1",
            source_url="https://wallhaven.cc/w/candidate-1",
            download_url="https://w.wallhaven.cc/full/candidate-1.jpg",
        )
        self.candidates = [
            ImageMetadata(
                provider="wallhaven",
                remote_id=f"candidate-{index}",
                source_url=f"https://wallhaven.cc/w/candidate-{index}",
                download_url=f"https://w.wallhaven.cc/full/candidate-{index}.jpg",
            )
            for index in range(4)
        ]
        self.services = Services(
            provider=self.provider,
            downloader=self.downloader,
            history=self.history,
            database=self.database,
        )

    def test_parser_accepts_all_commands(self) -> None:
        commands = [
            "download",
            "today",
            "next",
            "previous",
            "random",
            "history",
            "current",
            "daily",
        ]

        for command in commands:
            self.assertEqual(build_parser().parse_args([command]).command, command)

    def test_download_command_only_downloads(self) -> None:
        self.provider.search.return_value = self.candidates
        self.downloader.download.return_value = self.image
        output = io.StringIO()

        with redirect_stdout(output):
            result = main(["download"], self.services)

        self.assertEqual(result, 0)
        self.provider.search.assert_called_once_with(page=1)
        self.downloader.download.assert_called_once()
        self.history.set_wallpaper.assert_not_called()
        self.assertIn("remote_id=photo-1", output.getvalue())

    def test_random_command_sets_selected_image(self) -> None:
        self.history.get_history.return_value = [self.image]
        self.history.get_random.return_value = self.image
        self.history.set_wallpaper.return_value = self.image

        result = main(["random"], self.services)

        self.assertEqual(result, 0)
        self.history.get_random.assert_called_once_with()
        self.history.set_wallpaper.assert_called_once_with(self.image)

    def test_history_and_current_without_data(self) -> None:
        self.history.get_history.return_value = []
        output = io.StringIO()

        with redirect_stdout(output):
            history_result = main(["history"], self.services)
            current_result = main(["current"], self.services)

        self.assertEqual(history_result, 0)
        self.assertEqual(current_result, 1)
        self.assertIn("No wallpaper history.", output.getvalue())

    def test_menu_returns_four_candidates_and_current_marker(self) -> None:
        self.history.get_menu_candidates.return_value = [self.image]
        self.history.get_current.return_value = self.image
        output = io.StringIO()

        with redirect_stdout(output):
            result = main(["menu"], self.services)

        self.assertEqual(result, 0)
        self.assertTrue(json.loads(output.getvalue())[0]["current"])

    def test_select_sets_image_by_id(self) -> None:
        self.database.get_by_id.return_value = self.image
        self.history.set_wallpaper.return_value = self.image

        result = main(["select", "1"], self.services)

        self.assertEqual(result, 0)
        self.database.get_by_id.assert_called_once_with(1)
        self.history.set_wallpaper.assert_called_once_with(self.image)

    def test_daily_skips_provider_when_wallpaper_was_used_today(self) -> None:
        today = datetime.now(timezone.utc).date().isoformat()
        today_image = ImageRecord(**{**self.image.__dict__, "last_used_at": f"{today}T10:00:00+00:00"})
        self.history.get_history.return_value = [today_image]

        result = main(["daily"], self.services)

        self.assertEqual(result, 0)
        self.provider.search.assert_not_called()
        self.downloader.download.assert_not_called()
        self.history.set_wallpaper.assert_not_called()

    def test_daily_downloads_and_sets_when_history_is_old(self) -> None:
        old_image = ImageRecord(**{**self.image.__dict__, "last_used_at": "2000-01-01T00:00:00+00:00"})
        self.history.get_history.return_value = [old_image]
        self.provider.search.return_value = self.candidates
        self.downloader.download.side_effect = [
            ImageRecord(**{**self.image.__dict__, "id": index})
            for index in range(1, 5)
        ]
        self.history.set_wallpaper.return_value = self.image

        result = main(["daily"], self.services)

        self.assertEqual(result, 0)
        self.provider.search.assert_called_once_with(page=1)
        self.assertEqual(self.downloader.download.call_count, 4)
        self.history.set_wallpaper.assert_called_once_with(self.image)


if __name__ == "__main__":
    unittest.main()
