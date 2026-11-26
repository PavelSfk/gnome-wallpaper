"""Wallhaven API provider."""

from collections.abc import Mapping
from typing import Any

import requests

from wallpaper_app.providers.base import ImageMetadata, Provider, ProviderError


class WallhavenProvider(Provider):
    """Client for the public Wallhaven search API."""

    def __init__(
        self,
        query: str = "nature",
        session: requests.Session | None = None,
        base_url: str = "https://wallhaven.cc/api/v1",
        categories: str = "100",
        purity: str = "100",
        atleast: str = "1920x1080",
        sorting: str = "random",
    ) -> None:
        if not query:
            raise ValueError("Wallhaven query must not be empty")
        self.query = query
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")
        self.categories = categories
        self.purity = purity
        self.atleast = atleast
        self.sorting = sorting

    def search(self, query: str | None = None, page: int = 1, per_page: int = 10) -> list[ImageMetadata]:
        payload = self._get(
            "/search",
            params={
                "q": query or self.query,
                "categories": self.categories,
                "purity": self.purity,
                "atleast": self.atleast,
                "sorting": self.sorting,
                "page": page,
            },
        )
        data = payload.get("data")
        if not isinstance(data, list):
            raise ProviderError("Wallhaven response has no valid data list")
        return [self._parse_image(item) for item in data]

    def get_random(self) -> ImageMetadata:
        results = self.search()
        if not results:
            raise ProviderError("Wallhaven returned no wallpapers")
        return results[0]

    def get_image(self, remote_id: str) -> ImageMetadata:
        raise ProviderError(
            f"Wallhaven image lookup by ID is not supported by the search integration: {remote_id}"
        )

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        try:
            response = self.session.get(f"{self.base_url}{path}", params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            raise ProviderError(f"Wallhaven request failed: {path}") from error
        if not isinstance(payload, dict):
            raise ProviderError("Wallhaven response is not an object")
        return payload

    @staticmethod
    def _parse_image(payload: Any) -> ImageMetadata:
        if not isinstance(payload, Mapping):
            raise ProviderError("Wallhaven candidate is not an object")
        required = ("id", "url", "path", "dimension_x", "dimension_y", "file_type", "category", "purity")
        if any(field not in payload for field in required):
            raise ProviderError("Wallhaven candidate is missing required fields")
        if not all(isinstance(payload[field], str) and payload[field] for field in ("id", "url", "path", "file_type", "category", "purity")):
            raise ProviderError("Wallhaven candidate has invalid text fields")
        if not all(isinstance(payload[field], int) for field in ("dimension_x", "dimension_y")):
            raise ProviderError("Wallhaven candidate has invalid dimensions")
        return ImageMetadata(
            provider="wallhaven",
            remote_id=payload["id"],
            source_url=payload["url"],
            download_url=payload["path"],
            width=payload["dimension_x"],
            height=payload["dimension_y"],
            file_type=payload["file_type"],
            category=payload["category"],
            purity=payload["purity"],
        )