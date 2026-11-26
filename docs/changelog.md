# Changelog

## 2026-08-20

- Created the initial Python package skeleton using the `src/` layout.
- Added a virtual environment, project configuration, smoke test, and basic documentation.
- Added XDG path configuration and support for reading `UNSPLASH_ACCESS_KEY`.
- Added the SQLite schema and operations for storing image metadata and usage history.
- Added a provider abstraction and an official Unsplash API client with mocked HTTP tests.
- Added a deduplicating file downloader that stores metadata in SQLite.
- Added light and dark GNOME wallpaper updates through `gsettings`.
- Added usage history and local image selection: unused, random, next, and previous.
- Added an `argparse` CLI for downloading, selecting, viewing history, and showing the current wallpaper.
- Replaced the active Unsplash integration with the Wallhaven provider.
- Added filtering of known Wallhaven `remote_id` values before download and the `WALLHAVEN_QUERY` setting.
- Added systemd user units for the API-key-free `daily` command.
- Manually verified `wallpaper-app.service`: Wallhaven downloaded and set a wallpaper, and the process completed successfully.
- Enabled `wallpaper-app.timer`, with the first scheduled run set to 09:00.
- Changed `daily` to download four new wallpapers on a new day and refresh the menu candidate pool.
- Added a NetworkManager dispatcher that starts the user service when the network becomes available.
