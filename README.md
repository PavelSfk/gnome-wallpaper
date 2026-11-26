# Wallpaper App

Local application for downloading and changing wallpapers on Ubuntu GNOME.

The application uses Wallhaven as its wallpaper provider. The search query is
configurable through `WALLHAVEN_QUERY` and defaults to `nature`.

## Development

Create the virtual environment:

```bash
python3 -m venv .venv
```

Run the smoke test:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## systemd user timer

Install the user units after installing the package in `.venv`:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/wallpaper-app.service systemd/wallpaper-app.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now wallpaper-app.timer
```

To retry after Wi-Fi becomes available later, install the NetworkManager
dispatcher manually:

```bash
sudo install -m 0755 systemd/90-wallpaper-app-network-dispatcher \
	/etc/NetworkManager/dispatcher.d/90-wallpaper-app-wallpaper
sudo systemctl restart NetworkManager
```

The dispatcher reacts only to a connection state of `up`. It starts the
short-lived user service; `daily` checks SQLite first, so repeated network
events do not download another set after today's update is complete.

The unit expects the project at `~/Projects/Wallpaper_app` and runs the
short-lived `wallpaper-app daily` command once per day using the Wallhaven
query `nature`. Change the query with a systemd override or environment when
needed. Check its state with:

```bash
systemctl --user status wallpaper-app.timer
systemctl --user start wallpaper-app.service
journalctl --user -u wallpaper-app.service
```
