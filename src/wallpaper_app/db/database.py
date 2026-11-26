"""SQLite database access."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from wallpaper_app.db.migrations import run_migrations
from wallpaper_app.db.models import ImageRecord


class Database:
    """Small repository for downloaded wallpaper metadata."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        run_migrations(self.connection)

    def close(self) -> None:
        self.connection.close()

    def insert_image(self, image: ImageRecord) -> int:
        """Insert an image and return its local ID, or the existing ID."""
        downloaded_at = image.downloaded_at or _utc_now()
        cursor = self.connection.execute(
            """
            INSERT INTO images (
                provider, remote_id, source_url, author_url, author_name,
                description, width, height, file_type, category, purity,
                local_path, downloaded_at, first_used_at, last_used_at,
                use_count, favorite
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, remote_id) DO NOTHING
            """,
            (
                image.provider,
                image.remote_id,
                image.source_url,
                image.author_url,
                image.author_name,
                image.description,
                image.width,
                image.height,
                image.file_type,
                image.category,
                image.purity,
                image.local_path,
                downloaded_at,
                image.first_used_at,
                image.last_used_at,
                image.use_count,
                int(image.favorite),
            ),
        )
        self.connection.commit()
        if cursor.lastrowid:
            return cursor.lastrowid
        existing = self.get_by_provider_remote_id(image.provider, image.remote_id)
        if existing is None:
            raise RuntimeError("Image insert did not produce a record")
        return existing.id  # type: ignore[return-value]

    def get_by_provider_remote_id(
        self, provider: str, remote_id: str
    ) -> ImageRecord | None:
        row = self.connection.execute(
            "SELECT * FROM images WHERE provider = ? AND remote_id = ?",
            (provider, remote_id),
        ).fetchone()
        return _record_from_row(row) if row else None

    def get_existing_ids(self, provider: str, remote_ids: list[str]) -> set[str]:
        """Return known remote IDs without downloading their files."""
        if not remote_ids:
            return set()
        placeholders = ", ".join("?" for _ in remote_ids)
        rows = self.connection.execute(
            f"SELECT remote_id FROM images WHERE provider = ? AND remote_id IN ({placeholders})",
            [provider, *remote_ids],
        ).fetchall()
        return {row["remote_id"] for row in rows}

    def get_local_images(self) -> list[ImageRecord]:
        rows = self.connection.execute(
            "SELECT * FROM images WHERE local_path IS NOT NULL ORDER BY id"
        ).fetchall()
        return [_record_from_row(row) for row in rows]

    def get_recent_local_images(self, limit: int = 4) -> list[ImageRecord]:
        if limit < 1:
            return []
        rows = self.connection.execute(
            """
            SELECT * FROM images
            WHERE local_path IS NOT NULL
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [_record_from_row(row) for row in rows]

    def get_by_id(self, image_id: int) -> ImageRecord | None:
        row = self.connection.execute(
            "SELECT * FROM images WHERE id = ?", (image_id,)
        ).fetchone()
        return _record_from_row(row) if row else None

    def get_history(self) -> list[ImageRecord]:
        rows = self.connection.execute(
            """
            SELECT * FROM images
            WHERE local_path IS NOT NULL AND use_count > 0
            ORDER BY last_used_at DESC, id DESC
            """
        ).fetchall()
        return [_record_from_row(row) for row in rows]

    def get_unused(self) -> list[ImageRecord]:
        rows = self.connection.execute(
            """
            SELECT * FROM images
            WHERE local_path IS NOT NULL AND use_count = 0
            ORDER BY id
            """
        ).fetchall()
        return [_record_from_row(row) for row in rows]

    def update_usage(self, image_id: int, used_at: str | None = None) -> None:
        timestamp = used_at or _utc_now()
        self.connection.execute(
            """
            UPDATE images
            SET first_used_at = COALESCE(first_used_at, ?),
                last_used_at = ?,
                use_count = use_count + 1
            WHERE id = ?
            """,
            (timestamp, timestamp, image_id),
        )
        self.connection.commit()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_from_row(row: sqlite3.Row) -> ImageRecord:
    return ImageRecord(
        id=row["id"],
        provider=row["provider"],
        remote_id=row["remote_id"],
        source_url=row["source_url"],
        author_url=row["author_url"],
        author_name=row["author_name"],
        description=row["description"],
        width=row["width"],
        height=row["height"],
        file_type=row["file_type"],
        category=row["category"],
        purity=row["purity"],
        local_path=row["local_path"],
        downloaded_at=row["downloaded_at"],
        first_used_at=row["first_used_at"],
        last_used_at=row["last_used_at"],
        use_count=row["use_count"],
        favorite=bool(row["favorite"]),
    )
