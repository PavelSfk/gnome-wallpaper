# GNOME Wallpaper

GNOME Wallpaper downloads images from Wallhaven, changes the GNOME desktop
background automatically, and adds a wallpaper picker to the top bar.

The application:

- downloads four new wallpapers once per day;
- sets the first downloaded image as the current wallpaper;
- keeps all four images available in the GNOME Shell extension menu;
- avoids downloading Wallhaven images already stored in its SQLite database;
- runs from a systemd user timer at 09:00;
- can optionally retry when a network connection becomes available later.

## Current compatibility

The current release is tested with:

- Ubuntu 24.04 LTS;
- GNOME Shell 46;
- Python 3.12.

The extension currently declares support for GNOME Shell 46 only. Ubuntu 26.04
uses GNOME Shell 50 and is not supported until the extension has been tested
and its metadata has been updated.

## Quick install

On a fresh Ubuntu 24.04 GNOME installation, paste this entire block into a
terminal:

```bash
(
set -e
sudo apt update
sudo apt install -y git python3 python3-venv

mkdir -p "$HOME/Projects"
git clone https://github.com/PavelSfk/gnome-wallpaper.git \
  "$HOME/Projects/Wallpaper_app"
cd "$HOME/Projects/Wallpaper_app"

python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/wallpaper-app daily

mkdir -p "$HOME/.local/share/gnome-shell/extensions"
ln -s "$PWD/gnome-extension/wallpaper-app@pavel" \
  "$HOME/.local/share/gnome-shell/extensions/wallpaper-app@pavel"

mkdir -p "$HOME/.config/systemd/user"
cp systemd/wallpaper-app.service systemd/wallpaper-app.timer \
  "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now wallpaper-app.timer
)
```

Sign out of Ubuntu and sign back in. Then paste the second and final block:

```bash
gnome-extensions enable wallpaper-app@pavel
gnome-extensions info wallpaper-app@pavel
systemctl --user status wallpaper-app.timer --no-pager
```

The wallpaper icon should now appear in the top bar. Installation is complete.

## What the installation does

- Application files: `~/Projects/Wallpaper_app`
- Python environment: `~/Projects/Wallpaper_app/.venv`
- Wallpapers and database: `~/.local/share/wallpaper-app`
- GNOME extension: linked under `~/.local/share/gnome-shell/extensions`
- Automatic update: systemd user timer every day at 09:00
- External service: public Wallhaven API, with no API key required

Tests, custom search settings, the optional network retry, troubleshooting,
updates, and removal instructions are available in the expandable sections
below.

## Detailed reference

<details>
<summary>Manual installation, step by step</summary>

### Installation

Follow every step in this section on a fresh Ubuntu installation.

### 1. Install system requirements

Open a terminal and install Git and Python virtual environment support:

```bash
sudo apt update
sudo apt install git python3 python3-venv
```

GNOME Shell, `gsettings`, `systemd --user`, and the `gnome-extensions` command
are included in a standard Ubuntu GNOME installation.

### 2. Clone the repository

The current service and extension expect the project at the exact path
`~/Projects/Wallpaper_app`. Clone it there:

```bash
mkdir -p ~/Projects
git clone https://github.com/PavelSfk/gnome-wallpaper.git ~/Projects/Wallpaper_app
cd ~/Projects/Wallpaper_app
```

Do not use a different directory unless you also update the paths in
`systemd/wallpaper-app.service` and
`gnome-extension/wallpaper-app@pavel/extension.js`.

### 3. Create the Python environment

Create a virtual environment and install the application:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

Confirm that the command is available:

```bash
.venv/bin/wallpaper-app --help
```

### 4. Run the tests

Run the test suite before enabling automatic execution:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

All tests should finish with `OK`. The provider tests use mocked HTTP requests
and do not download real wallpapers.

### 5. Perform the first wallpaper update

Run the daily command manually:

```bash
.venv/bin/wallpaper-app daily
```

This command downloads four new images from Wallhaven, stores them under
`~/.local/share/wallpaper-app/images`, records their metadata in
`~/.local/share/wallpaper-app/wallpaper.db`, and sets the first image as both
the light and dark GNOME wallpaper.

Running `daily` again on the same day does not download another set.

### 6. Install the GNOME Shell extension

Create the user extension directory and link the extension from the cloned
repository:

```bash
mkdir -p ~/.local/share/gnome-shell/extensions
ln -s ~/Projects/Wallpaper_app/gnome-extension/wallpaper-app@pavel \
  ~/.local/share/gnome-shell/extensions/wallpaper-app@pavel
```

Sign out of the GNOME session and sign back in. This is required for GNOME
Shell to discover a newly installed extension in a Wayland session.

After signing back in, enable and inspect the extension:

```bash
gnome-extensions enable wallpaper-app@pavel
gnome-extensions info wallpaper-app@pavel
```

A wallpaper icon should appear in the top bar. Open it to select one of the
four most recently downloaded wallpapers.

If the `ln` command reports that the destination already exists, do not create
another link. Check the existing installation with:

```bash
ls -l ~/.local/share/gnome-shell/extensions/wallpaper-app@pavel
```

### 7. Install and enable the systemd timer

Copy the user service and timer into the systemd user configuration:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/wallpaper-app.service systemd/wallpaper-app.timer \
  ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now wallpaper-app.timer
```

Confirm that the timer is active:

```bash
systemctl --user status wallpaper-app.timer --no-pager
systemctl --user list-timers wallpaper-app.timer
```

Test the service manually:

```bash
systemctl --user start wallpaper-app.service
systemctl --user status wallpaper-app.service --no-pager
```

The service is a short-lived `oneshot` unit. A successful service normally
shows `inactive (dead)` after it finishes; this does not mean it failed. Check
`Result=success` or inspect its logs:

```bash
journalctl --user -u wallpaper-app.service -n 50 --no-pager
```

The timer runs every day at 09:00. `Persistent=true` allows systemd to run a
missed update after the computer starts or resumes later.

</details>

<details>
<summary>Optional network retry</summary>

The timer may run while the computer is offline. The optional NetworkManager
dispatcher starts the user service when a network interface later reaches the
`up` state.

Install it system-wide:

```bash
sudo install -m 0755 systemd/90-wallpaper-app-network-dispatcher \
  /etc/NetworkManager/dispatcher.d/90-wallpaper-app-wallpaper
sudo systemctl restart NetworkManager
```

The dispatcher does not run continuously and does not poll an external site.
Repeated network events are safe because `daily` checks the SQLite history
before downloading another set.

</details>

<details>
<summary>Configuration</summary>

### Change the Wallhaven search query

The default query is `nature`. Create a systemd user override to change it:

```bash
systemctl --user edit wallpaper-app.service
```

Enter the following content, replacing `mountains` with the desired query:

```ini
[Service]
Environment=WALLHAVEN_QUERY=mountains
```

Save the editor, then reload systemd and test the service:

```bash
systemctl --user daemon-reload
systemctl --user start wallpaper-app.service
```

The application also supports these environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `WALLHAVEN_QUERY` | `nature` | Search text |
| `WALLHAVEN_CATEGORIES` | `100` | Wallhaven category filter |
| `WALLHAVEN_PURITY` | `100` | Wallhaven purity filter |
| `WALLHAVEN_ATLEAST` | `1920x1080` | Minimum image resolution |
| `WALLHAVEN_SORTING` | `random` | Result sorting mode |

</details>

<details>
<summary>Useful commands</summary>

Run these commands from `~/Projects/Wallpaper_app`:

```bash
# Download one new image without setting it
.venv/bin/wallpaper-app download

# Run the once-per-day download and wallpaper update
.venv/bin/wallpaper-app daily

# Show the current wallpaper record
.venv/bin/wallpaper-app current

# Show wallpaper history
.venv/bin/wallpaper-app history

# Select the next, previous, or a random local wallpaper
.venv/bin/wallpaper-app next
.venv/bin/wallpaper-app previous
.venv/bin/wallpaper-app random
```

</details>

<details>
<summary>Updating</summary>

Update the repository and reinstall the editable Python package:

```bash
cd ~/Projects/Wallpaper_app
git pull --ff-only
.venv/bin/python -m pip install -e .
```

Reinstall the systemd unit files in case they changed:

```bash
cp systemd/wallpaper-app.service systemd/wallpaper-app.timer \
  ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user restart wallpaper-app.timer
```

The GNOME extension is linked to the repository, so extension file updates do
not need to be copied. Sign out and back in after an extension update.

</details>

<details>
<summary>Troubleshooting</summary>

### The extension is not listed

Confirm the link and UUID:

```bash
ls -l ~/.local/share/gnome-shell/extensions/wallpaper-app@pavel
gnome-extensions list
```

Then sign out and back in before trying to enable it again.

### The timer works but no wallpaper is downloaded

Inspect the service logs:

```bash
journalctl --user -u wallpaper-app.service -n 100 --no-pager
```

Confirm that the manual command works:

```bash
cd ~/Projects/Wallpaper_app
.venv/bin/wallpaper-app daily
```

### The service executable cannot be found

Confirm that the project is at the expected path and reinstall it:

```bash
cd ~/Projects/Wallpaper_app
.venv/bin/python -m pip install -e .
ls -l .venv/bin/wallpaper-app
```

</details>

<details>
<summary>Uninstallation</summary>

Disable the timer and extension first:

```bash
systemctl --user disable --now wallpaper-app.timer
gnome-extensions disable wallpaper-app@pavel
```

Remove the installed user units and extension link:

```bash
rm ~/.config/systemd/user/wallpaper-app.service
rm ~/.config/systemd/user/wallpaper-app.timer
rm ~/.local/share/gnome-shell/extensions/wallpaper-app@pavel
systemctl --user daemon-reload
```

If the optional NetworkManager dispatcher was installed, remove it separately:

```bash
sudo rm /etc/NetworkManager/dispatcher.d/90-wallpaper-app-wallpaper
sudo systemctl restart NetworkManager
```

The downloaded images and SQLite history remain under
`~/.local/share/wallpaper-app`. Remove that directory only if the stored
wallpapers and history are no longer needed.

</details>
