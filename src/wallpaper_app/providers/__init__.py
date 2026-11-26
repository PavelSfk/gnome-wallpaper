"""Wallpaper providers."""

from wallpaper_app.providers.base import ImageMetadata, Provider, ProviderError
from wallpaper_app.providers.wallhaven import WallhavenProvider

__all__ = ["ImageMetadata", "Provider", "ProviderError", "WallhavenProvider"]
