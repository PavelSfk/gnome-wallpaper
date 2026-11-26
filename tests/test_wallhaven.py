import unittest
from unittest.mock import Mock

from wallpaper_app.providers.base import ProviderError
from wallpaper_app.providers.wallhaven import WallhavenProvider


WALLPAPER = {
    "id": "abc123",
    "url": "https://wallhaven.cc/w/abc123",
    "path": "https://w.wallhaven.cc/full/ab/wallhaven-abc123.jpg",
    "dimension_x": 1920,
    "dimension_y": 1080,
    "file_type": "image/jpeg",
    "category": "general",
    "purity": "sfw",
    "thumbs": {},
}


class WallhavenProviderTest(unittest.TestCase):
    def test_search_maps_response_and_sends_wallhaven_params(self) -> None:
        response = Mock()
        response.json.return_value = {"data": [WALLPAPER]}
        session = Mock()
        session.get.return_value = response
        provider = WallhavenProvider("mountains", session=session)

        result = provider.search(page=2)

        self.assertEqual(result[0].provider, "wallhaven")
        self.assertEqual(result[0].remote_id, "abc123")
        self.assertEqual(result[0].source_url, WALLPAPER["url"])
        self.assertEqual(result[0].download_url, WALLPAPER["path"])
        self.assertEqual(result[0].width, 1920)
        session.get.assert_called_once_with(
            "https://wallhaven.cc/api/v1/search",
            params={
                "q": "mountains",
                "categories": "100",
                "purity": "100",
                "atleast": "1920x1080",
                "sorting": "random",
                "page": 2,
            },
            timeout=10,
        )

    def test_search_accepts_query_override_and_random_uses_default_query(self) -> None:
        response = Mock()
        response.json.side_effect = [{"data": [WALLPAPER]}, {"data": [WALLPAPER]}]
        session = Mock()
        session.get.return_value = response
        provider = WallhavenProvider("nature", session=session)

        provider.search("+mountains +nature -people")
        provider.get_random()

        self.assertEqual(session.get.call_args_list[0].kwargs["params"]["q"], "+mountains +nature -people")
        self.assertEqual(session.get.call_args_list[1].kwargs["params"]["q"], "nature")

    def test_invalid_payload_and_empty_query_raise(self) -> None:
        with self.assertRaises(ValueError):
            WallhavenProvider("")

        response = Mock()
        response.json.return_value = {"data": [{"id": "missing"}]}
        session = Mock()
        session.get.return_value = response
        provider = WallhavenProvider(session=session)

        with self.assertRaises(ProviderError):
            provider.search()


if __name__ == "__main__":
    unittest.main()