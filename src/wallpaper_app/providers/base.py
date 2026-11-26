"""Provider contracts and shared metadata."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ProviderError(RuntimeError):
    """Raised when a provider cannot return valid image metadata."""


@dataclass(frozen=True)
class ImageMetadata:
    """Provider-independent metadata for one remote image."""

    provider: str
    remote_id: str
    source_url: str
    download_url: str
    author_url: str | None = None
    author_name: str | None = None
    description: str | None = None
    width: int | None = None
    height: int | None = None
    file_type: str | None = None
    category: str | None = None
    purity: str | None = None


class Provider(ABC):
    """Interface implemented by wallpaper image providers."""

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 10) -> list[ImageMetadata]:
        """Search for images."""

    @abstractmethod
    def get_random(self) -> ImageMetadata:
        """Return one random image."""

    @abstractmethod
    def get_image(self, remote_id: str) -> ImageMetadata:
        """Return one image by its provider-specific ID."""
