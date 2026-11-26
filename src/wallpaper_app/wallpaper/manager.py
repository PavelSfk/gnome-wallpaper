"""Set wallpapers using GNOME settings."""

from pathlib import Path
import subprocess


class WallpaperManager:
    """Manage the light and dark GNOME wallpaper URIs."""

    schema = "org.gnome.desktop.background"

    def set_wallpaper(self, path: Path | str) -> None:
        """Set one image as both the light and dark wallpaper."""
        wallpaper_path = Path(path).expanduser()
        if not wallpaper_path.is_file():
            raise FileNotFoundError(wallpaper_path)

        uri = wallpaper_path.resolve().as_uri()
        for key in ("picture-uri", "picture-uri-dark"):
            subprocess.run(
                ["gsettings", "set", self.schema, key, uri],
                check=True,
            )
