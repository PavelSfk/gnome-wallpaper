# AI Context

## Current state
Wallhaven is the active provider. The CLI uses the configurable
`WALLHAVEN_QUERY` setting, which defaults to `nature`, and rejects known
`provider + remote_id` pairs before downloading an image. On a new day,
`daily` downloads four new wallpapers, sets the first one, and leaves all four
available for selection in the extension. The systemd user service has passed
validation and successfully run `daily`. The timer is active and waiting for
its scheduled run. A project NetworkManager dispatcher can start the service
when the network becomes available later; installation under `/etc` remains a
manual step. Full security hardening has not been implemented yet.

## Environment
Ubuntu 24.04.4 LTS, GNOME Shell 46, Python 3.12.3, `gsettings`, and
`systemd --user` are available.

## Next step
Install the NetworkManager dispatcher and verify its behavior after Wi-Fi connects.
