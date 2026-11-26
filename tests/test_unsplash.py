import unittest
from unittest.mock import Mock

from wallpaper_app.providers.base import ProviderError
from wallpaper_app.providers.unsplash import UnsplashProvider


IMAGE_PAYLOAD = {
    "id": "photo-1",
    "description": "A mountain",
    "alt_description": "mountain landscape",
    "urls": {"full": "https://images.example/photo-1.jpg"},
    "links": {"html": "https://unsplash.com/photos/photo-1"},
    "user": {
        "name": "Test Author",
        "links": {"html": "https://unsplash.com/@author"},
    },
}


class UnsplashProviderTest(unittest.TestCase):
    def make_provider(self, payload: object) -> tuple[UnsplashProvider, Mock]:
        response = Mock()
        response.json.return_value = payload
        session = Mock()
        session.get.return_value = response
        return UnsplashProvider("test-key", session=session), response

    def test_get_image_maps_metadata_and_request(self) -> None:
        provider, response = self.make_provider(IMAGE_PAYLOAD)

        image = provider.get_image("photo-1")

        self.assertEqual(image.provider, "unsplash")
        self.assertEqual(image.remote_id, "photo-1")
        self.assertEqual(image.author_name, "Test Author")
        self.assertEqual(image.description, "A mountain")
        response.raise_for_status.assert_called_once_with()
        provider.session.get.assert_called_once_with(
            "https://api.unsplash.com/photos/photo-1",
            params={"client_id": "test-key"},
            timeout=10,
        )

    def test_search_and_random_parse_responses(self) -> None:
        search_response = Mock()
        search_response.json.return_value = {"results": [IMAGE_PAYLOAD]}
        random_response = Mock()
        random_response.json.return_value = IMAGE_PAYLOAD
        session = Mock()
        session.get.side_effect = [search_response, random_response]
        provider = UnsplashProvider("test-key", session=session)

        search_result = provider.search("mountains", page=2, per_page=5)
        random_result = provider.get_random()

        self.assertEqual(search_result[0].remote_id, "photo-1")
        self.assertEqual(random_result.remote_id, "photo-1")
        self.assertEqual(session.get.call_count, 2)

    def test_missing_key_and_invalid_payload_raise(self) -> None:
        with self.assertRaises(ValueError):
            UnsplashProvider(None)

        provider, _ = self.make_provider({"id": "missing-fields"})
        with self.assertRaises(ProviderError):
            provider.get_random()


if __name__ == "__main__":
    unittest.main()
