"""Unsplash API provider."""

from collections.abc import Sequence
from typing import Any

import requests

from wallpaper_app.providers.base import ImageMetadata, Provider, ProviderError


class UnsplashProvider(Provider):
    """Client for the official Unsplash API."""

    def __init__(
        self,
        access_key: str | None,
        session: requests.Session | None = None,
        base_url: str = "https://api.unsplash.com",
    ) -> None:
        if not access_key:
            raise ValueError("UNSPLASH_ACCESS_KEY is required")
        self.access_key = access_key
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")

    def search(self, query: str, page: int = 1, per_page: int = 10) -> list[ImageMetadata]:
        payload = self._get(
            "/search/photos",
            params={"query": query, "page": page, "per_page": per_page},
        )
        results = payload.get("results")
        if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
            raise ProviderError("Unsplash response has no valid results")
        return [self._parse_image(item) for item in results]

    def get_random(self) -> ImageMetadata:
        return self._parse_image(self._get("/photos/random"))

    def get_image(self, remote_id: str) -> ImageMetadata:
        return self._parse_image(self._get(f"/photos/{remote_id}"))

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        request_params = {"client_id": self.access_key, **(params or {})}
        try:
            response = self.session.get(
                f"{self.base_url}{path}", params=request_params, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            raise ProviderError(f"Unsplash request failed: {path}") from error

    @staticmethod
    def _parse_image(payload: Any) -> ImageMetadata:
        if not isinstance(payload, dict):
            raise ProviderError("Unsplash image response is not an object")
        urls = payload.get("urls")
        user = payload.get("user")
        if not isinstance(urls, dict) or not isinstance(user, dict):
            raise ProviderError("Unsplash image response is missing required fields")
        remote_id = payload.get("id")
        source_url = payload.get("links", {}).get("html")
        download_url = urls.get("full") or urls.get("raw")
        if not all(isinstance(value, str) and value for value in (remote_id, source_url, download_url)):
            raise ProviderError("Unsplash image response has invalid identifiers or URLs")

        return ImageMetadata(
            provider="unsplash",
            remote_id=remote_id,
            source_url=source_url,
            download_url=download_url,
            author_url=user.get("links", {}).get("html"),
            author_name=user.get("name"),
            description=payload.get("description") or payload.get("alt_description"),
        )
