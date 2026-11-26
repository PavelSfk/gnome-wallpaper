# Decisions

## 2026-08-20 — Minimal `src/` skeleton

- **Decision:** The project uses the `src/` layout and requires Python >= 3.12.
- **Reason:** This separates package code from tests and project files while matching the target architecture.
- **Consequence:** Tests and tools must run the package from an installed environment or with a correctly configured import path.

## 2026-08-20 — Wallhaven as the active provider

- **Decision:** The public Wallhaven API replaced the active Unsplash integration.
- **Reason:** The Unsplash API is not suitable for the planned wallpaper use case.
- **Consequence:** Configuration uses `WALLHAVEN_QUERY`, the provider parses candidates from `data`, and SQLite filters known `provider + remote_id` pairs before the downloader runs.

## 2026-08-23 — Responding to a delayed network connection

- **Decision:** Use a NetworkManager dispatcher as a short trigger for the user service, while retaining the timer as a fallback.
- **Reason:** A laptop may boot offline and obtain Wi-Fi later. A continuously running process or external connectivity polling is unnecessary.
- **Consequence:** The dispatcher reacts only to the `up` state and starts `wallpaper-app.service`. The `daily` command checks SQLite first and is idempotent. Installing the dispatcher under `/etc/NetworkManager/dispatcher.d/` requires a manual `sudo` step.
