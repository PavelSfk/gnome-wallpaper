"""Configuration paths and environment-backed settings."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    """Resolved application settings."""

    config_dir: Path
    data_dir: Path
    images_dir: Path
    database_path: Path
    wallhaven_query: str
    wallhaven_categories: str = "100"
    wallhaven_purity: str = "100"
    wallhaven_atleast: str = "1920x1080"
    wallhaven_sorting: str = "random"


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Build settings from XDG variables and Wallhaven options."""
    environment = os.environ if environ is None else environ
    config_home = Path(environment.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    data_home = Path(environment.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    config_dir = config_home / "wallpaper-app"
    data_dir = data_home / "wallpaper-app"

    return Settings(
        config_dir=config_dir,
        data_dir=data_dir,
        images_dir=data_dir / "images",
        database_path=data_dir / "wallpaper.db",
        wallhaven_query=environment.get("WALLHAVEN_QUERY", "nature"),
        wallhaven_categories=environment.get("WALLHAVEN_CATEGORIES", "100"),
        wallhaven_purity=environment.get("WALLHAVEN_PURITY", "100"),
        wallhaven_atleast=environment.get("WALLHAVEN_ATLEAST", "1920x1080"),
        wallhaven_sorting=environment.get("WALLHAVEN_SORTING", "random"),
    )
