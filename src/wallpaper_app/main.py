"""Command-line entry point."""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Sequence

from wallpaper_app.config.settings import Settings, load_settings
from wallpaper_app.db.database import Database
from wallpaper_app.db.models import ImageRecord
from wallpaper_app.download.downloader import Downloader
from wallpaper_app.history.manager import HistoryManager
from wallpaper_app.providers.wallhaven import WallhavenProvider
from wallpaper_app.wallpaper.manager import WallpaperManager

DAILY_CANDIDATE_COUNT = 4

@dataclass
class Services:
    """Application services used by CLI commands."""

    provider: WallhavenProvider
    downloader: Downloader
    history: HistoryManager
    database: Database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wallpaper-app")
    parser.add_argument(
        "command",
        nargs="?",
        choices=[
            "download",
            "today",
            "next",
            "previous",
            "random",
            "history",
            "current",
            "daily",
            "menu",
            "select",
        ],
    )
    parser.add_argument("value", nargs="?")
    return parser


def build_services(settings: Settings | None = None) -> Services:
    resolved = settings or load_settings()
    database = Database(resolved.database_path)
    provider = WallhavenProvider(
        query=resolved.wallhaven_query,
        categories=resolved.wallhaven_categories,
        purity=resolved.wallhaven_purity,
        atleast=resolved.wallhaven_atleast,
        sorting=resolved.wallhaven_sorting,
    )
    downloader = Downloader(database, resolved.images_dir)
    history = HistoryManager(database, WallpaperManager())
    return Services(provider, downloader, history, database)


def main(argv: Sequence[str] | None = None, services: Services | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0

    owns_services = services is None
    try:
        active_services = services or build_services()
        return _run_command(args.command, active_services, args.value)
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        parser.error(str(error))
        return 2
    finally:
        if owns_services and services is None and "active_services" in locals():
            active_services.database.close()


def _run_command(command: str, services: Services, value: str | None = None) -> int:
    if command == "menu":
        _print_menu(services.history)
        return 0
    if command == "select":
        if value is None or not value.isdigit():
            raise ValueError("select requires a numeric local image ID")
        image = services.database.get_by_id(int(value))
        if image is None or image.local_path is None:
            raise ValueError(f"Local image not found: {value}")
        _print_image(services.history.set_wallpaper(image))
        return 0
    if command == "daily":
        latest = _latest(services.history)
        today = datetime.now(timezone.utc).date().isoformat()
        if latest is not None and latest.last_used_at and latest.last_used_at[:10] == today:
            _print_image(latest)
            return 0
        images = _download_new_candidates(services, DAILY_CANDIDATE_COUNT)
        used = services.history.set_wallpaper(images[0])
        _print_image(used)
        return 0
    if command == "download":
        image = _download_new_candidates(services, 1)[0]
        _print_image(image)
        return 0
    if command == "history":
        for image in services.history.get_history():
            _print_image(image)
        return 0
    if command in {"today", "current"}:
        image = _latest(services.history)
        if image is None:
            print("No wallpaper history.")
            return 1
        _print_image(image)
        return 0

    current = _latest(services.history)
    current_id = current.id if current else None
    if command == "next":
        image = services.history.get_next(current_id)
    elif command == "previous":
        image = services.history.get_previous(current_id)
    else:
        image = services.history.get_random()
    if image is None:
        print("No local wallpapers.")
        return 1
    services.history.set_wallpaper(image)
    _print_image(image)
    return 0


def _latest(history: HistoryManager) -> ImageRecord | None:
    records = history.get_history()
    return records[0] if records else None


def _print_menu(history: HistoryManager) -> None:
    current = history.get_current()
    current_id = current.id if current else None
    payload = [
        {
            "id": image.id,
            "path": image.local_path,
            "provider": image.provider,
            "remote_id": image.remote_id,
            "current": image.id == current_id,
        }
        for image in history.get_menu_candidates(4)
    ]
    print(json.dumps(payload))


def _download_new_candidates(services: Services, count: int) -> list[ImageRecord]:
    """Download a pool of new Wallhaven candidates after ID filtering."""
    downloaded: list[ImageRecord] = []
    page = 1
    while len(downloaded) < count and page <= 5:
        candidates = services.provider.search(page=page)
        if not candidates:
            break
        known = services.database.get_existing_ids(
            candidates[0].provider, [candidate.remote_id for candidate in candidates]
        )
        for candidate in candidates:
            if candidate.remote_id in known:
                continue
            downloaded.append(services.downloader.download(candidate))
            if len(downloaded) == count:
                break
        page += 1
    if len(downloaded) < count:
        raise RuntimeError(f"Wallhaven returned fewer than {count} new wallpapers")
    return downloaded


def _print_image(image: ImageRecord) -> None:
    print(
        f"id={image.id} provider={image.provider} "
        f"remote_id={image.remote_id} path={image.local_path} "
        f"use_count={image.use_count}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
