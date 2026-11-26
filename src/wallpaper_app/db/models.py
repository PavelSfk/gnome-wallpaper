"""Database models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageRecord:
    """Metadata stored for a downloaded image."""

    provider: str
    remote_id: str
    source_url: str
    author_url: str | None = None
    author_name: str | None = None
    description: str | None = None
    width: int | None = None
    height: int | None = None
    file_type: str | None = None
    category: str | None = None
    purity: str | None = None
    local_path: str | None = None
    id: int | None = None
    downloaded_at: str | None = None
    first_used_at: str | None = None
    last_used_at: str | None = None
    use_count: int = 0
    favorite: bool = False
