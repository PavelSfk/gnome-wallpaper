"""Database schema migrations."""

import sqlite3


SCHEMA_VERSION = 2


def run_migrations(connection: sqlite3.Connection) -> None:
    """Create the initial schema if it does not exist."""
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,
            remote_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            author_url TEXT,
            author_name TEXT,
            description TEXT,
            width INTEGER,
            height INTEGER,
            file_type TEXT,
            category TEXT,
            purity TEXT,
            local_path TEXT,
            downloaded_at TEXT NOT NULL,
            first_used_at TEXT,
            last_used_at TEXT,
            use_count INTEGER NOT NULL DEFAULT 0,
            favorite INTEGER NOT NULL DEFAULT 0,
            UNIQUE (provider, remote_id)
        );
        """
    )
    columns = {row[1] for row in connection.execute("PRAGMA table_info(images)")}
    for name, definition in {
        "width": "INTEGER",
        "height": "INTEGER",
        "file_type": "TEXT",
        "category": "TEXT",
        "purity": "TEXT",
    }.items():
        if name not in columns:
            connection.execute(f"ALTER TABLE images ADD COLUMN {name} {definition}")
    connection.execute("DELETE FROM schema_version")
    connection.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
    connection.commit()
