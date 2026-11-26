"""Download provider images to local storage."""

import hashlib
from pathlib import Path
from urllib.parse import urlparse

import requests

from wallpaper_app.db.database import Database
from wallpaper_app.db.models import ImageRecord
from wallpaper_app.providers.base import ImageMetadata


class DownloadError(RuntimeError):
    """Raised when an image cannot be downloaded or stored."""


class Downloader:
    """Download images and register their metadata in SQLite."""

    def __init__(
        self,
        database: Database,
        images_dir: Path | str,
        session: requests.Session | None = None,
    ) -> None:
        self.database = database
        self.images_dir = Path(images_dir)
        self.session = session or requests.Session()

    def download(self, metadata: ImageMetadata) -> ImageRecord:
        """Download an image once and return its database record."""
        existing = self.database.get_by_provider_remote_id(
            metadata.provider, metadata.remote_id
        )
        if existing is not None and existing.local_path:
            return existing

        self.images_dir.mkdir(parents=True, exist_ok=True)
        destination = self.images_dir / _filename(metadata)
        try:
            response = self.session.get(metadata.download_url, stream=True, timeout=10)
            response.raise_for_status()
            with destination.open("wb") as image_file:
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        image_file.write(chunk)
        except (OSError, requests.RequestException) as error:
            destination.unlink(missing_ok=True)
            raise DownloadError(f"Could not download image {metadata.remote_id}") from error

        record = ImageRecord(
            provider=metadata.provider,
            remote_id=metadata.remote_id,
            source_url=metadata.source_url,
            author_url=metadata.author_url,
            author_name=metadata.author_name,
            description=metadata.description,
            width=metadata.width,
            height=metadata.height,
            file_type=metadata.file_type,
            category=metadata.category,
            purity=metadata.purity,
            local_path=str(destination),
        )
        record_id = self.database.insert_image(record)
        return self.database.get_by_provider_remote_id(
            metadata.provider, metadata.remote_id
        ) or ImageRecord(**{**record.__dict__, "id": record_id})


def _filename(metadata: ImageMetadata) -> str:
    digest = hashlib.sha256(
        f"{metadata.provider}:{metadata.remote_id}".encode("utf-8")
    ).hexdigest()[:24]
    suffix = Path(urlparse(metadata.download_url).path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".img"
    return f"{digest}{suffix}"
