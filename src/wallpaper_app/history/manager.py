"""Wallpaper history and local image selection."""

import random

from wallpaper_app.db.database import Database
from wallpaper_app.db.models import ImageRecord
from wallpaper_app.wallpaper.manager import WallpaperManager


class HistoryManager:
    """Coordinate wallpaper changes with persistent usage history."""

    def __init__(self, database: Database, wallpaper_manager: WallpaperManager) -> None:
        self.database = database
        self.wallpaper_manager = wallpaper_manager

    def set_wallpaper(self, image: ImageRecord) -> ImageRecord:
        """Set an image and record usage only after GNOME succeeds."""
        if image.id is None or image.local_path is None:
            raise ValueError("A local image with an ID is required")
        self.wallpaper_manager.set_wallpaper(image.local_path)
        self.database.update_usage(image.id)
        return self.database.get_by_id(image.id) or image

    def get_history(self) -> list[ImageRecord]:
        return self.database.get_history()

    def get_unused(self) -> list[ImageRecord]:
        return self.database.get_unused()

    def get_random(self) -> ImageRecord | None:
        return _choose(self.database.get_local_images())

    def get_next(self, current_id: int | None = None) -> ImageRecord | None:
        return _step(self.database.get_local_images(), current_id, 1)

    def get_previous(self, current_id: int | None = None) -> ImageRecord | None:
        return _step(self.database.get_local_images(), current_id, -1)

    def get_menu_candidates(self, limit: int = 4) -> list[ImageRecord]:
        """Return the newest local candidates for the GNOME popover."""
        return self.database.get_recent_local_images(limit)

    def get_current(self) -> ImageRecord | None:
        history = self.database.get_history()
        return history[0] if history else None


def _choose(images: list[ImageRecord]) -> ImageRecord | None:
    return random.choice(images) if images else None


def _step(
    images: list[ImageRecord], current_id: int | None, direction: int
) -> ImageRecord | None:
    if not images:
        return None
    if current_id is None:
        return images[0] if direction > 0 else images[-1]
    current_index = next(
        (index for index, image in enumerate(images) if image.id == current_id),
        None,
    )
    if current_index is None:
        return images[0] if direction > 0 else images[-1]
    return images[(current_index + direction) % len(images)]
