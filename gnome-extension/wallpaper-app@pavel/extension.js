import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Clutter from 'gi://Clutter';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const PYTHON_PATH = GLib.build_filenamev([
    GLib.get_home_dir(),
    'Projects',
    'Wallpaper_app',
    '.venv',
    'bin',
    'python',
]);
const USER_CONFIG_HOME = GLib.build_filenamev([
    GLib.get_home_dir(),
    '.config',
]);
const USER_DATA_HOME = GLib.build_filenamev([
    GLib.get_home_dir(),
    '.local',
    'share',
]);

export default class WallpaperAppExtension extends Extension {
    enable() {
        this._stylesheet = this.dir.get_child('stylesheet.css');
        this._theme = St.ThemeContext.get_for_stage(global.stage).get_theme();
        this._theme.load_stylesheet(this._stylesheet);
        this._indicator = new PanelMenu.Button(0.0, 'Wallpaper App', false);
        this._indicator.reactive = true;
        this._indicator.can_focus = true;

        this._indicator.connect('button-release-event', () => {
            if (!this._indicator.menu.isOpen)
                this._indicator.menu.open();
            return Clutter.EVENT_STOP;
        });

        this._indicator.add_child(new St.Icon({
            icon_name: 'preferences-desktop-wallpaper-symbolic',
            style_class: 'system-status-icon',
        }));

        Main.panel.addToStatusArea('wallpaper-app', this._indicator);
        this._loadMenu();
    }

    disable() {
        this._theme?.unload_stylesheet(this._stylesheet);
        this._theme = null;
        this._stylesheet = null;
        this._indicator?.destroy();
        this._indicator = null;
    }
    _runCli(args, callback) {
        const flags = Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE;
        const launcher = Gio.SubprocessLauncher.new(flags);
        launcher.setenv('XDG_CONFIG_HOME', USER_CONFIG_HOME, true);
        launcher.setenv('XDG_DATA_HOME', USER_DATA_HOME, true);
        const subprocess = launcher.spawnv([PYTHON_PATH, '-m', 'wallpaper_app.main', ...args]);
        subprocess.communicate_utf8_async(null, null, (process, result) => {
            try {
                const [, stdout, stderr] = process.communicate_utf8_finish(result);
                if (stderr)
                    log(`Wallpaper App CLI: ${stderr.trim()}`);
                callback(stdout, stderr);
            } catch (error) {
                log(`Wallpaper App CLI failed: ${error.message}`);
            }
        });
    }

    _loadMenu() {
        if (!this._indicator)
            return;

        this._indicator.menu.removeAll();
        this._indicator.menu.addMenuItem(new PopupMenu.PopupMenuItem('Loading...'));
        this._runCli(['menu'], (stdout) => {
            let candidates;
            try {
                candidates = JSON.parse(stdout);
            } catch (error) {
                log(`Wallpaper App returned invalid menu JSON: ${error.message}`);
                return;
            }
            this._renderCandidates(candidates);
        });
    }

    _renderCandidates(candidates) {
        if (!this._indicator)
            return;

        this._indicator.menu.removeAll();
        if (candidates.length === 0) {
            this._indicator.menu.addMenuItem(new PopupMenu.PopupMenuItem('No wallpapers'));
            return;
        }

        for (const candidate of candidates) {
            const item = new PopupMenu.PopupBaseMenuItem({
                reactive: true,
                can_focus: true,
            });
            const icon = new St.Icon({
                gicon: Gio.icon_new_for_string(candidate.path),
                icon_size: 96,
                style_class: 'wallpaper-thumbnail',
            });
            const label = new St.Label({
                text: candidate.remote_id,
                y_align: Clutter.ActorAlign.CENTER,
            });
            item.add_child(icon);
            item.add_child(label);
            if (candidate.current)
                item.add_style_class_name('wallpaper-current');
            item.connect('activate', () => {
                this._runCli(['select', String(candidate.id)], () => this._loadMenu());
            });
            this._indicator.menu.addMenuItem(item);
        }
    }
}
